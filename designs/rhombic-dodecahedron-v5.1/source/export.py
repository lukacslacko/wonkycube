from hardware import *
from mesh_io import cleaned
from print_3mf import save_3mf
import hashlib,html
# DEST comes from design.py
def pose(m,f,n):
 if f in ['P','T','S','TC','SC']:q=Rotation.align_vectors([[0,0,1]],[n])[0].as_matrix()
 elif f in ['core','stand']:q=Rotation.align_vectors([[0,0,-1]],[AXES[0] if f=='core' else n])[0].as_matrix()
 else:q=np.eye(3)
 v=m.vertices@q.T;best=None
 for a in np.arange(0,180,3):
  z=Rotation.from_euler('z',a,degrees=True).as_matrix();dims=np.ptp(v@z.T,axis=0);score=dims[0]*dims[1]
  if best is None or score<best[0]:best=(score,z)
 q=best[1]@q;v=m.vertices@q.T;t=-np.r_[((v.max(0)+v.min(0))/2)[:2],v[:,2].min()]
 m=m.copy();m.vertices=v+t;return m,matrix(q,t)
def export():
 for d in ['stl/puzzle','stl/fit-coupons','stl/optional','plates','reference','reports','images','source']:(DEST/d).mkdir(parents=True,exist_ok=True)
 manifest=[];printed={};solids={};names={'T':'threefold-center-print-8','S':'fourfold-center-print-6','P':'petal-print-24'}
 def add(s,name,f,quantity,folder,n=None):
  chunks=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True)
  remnants=[dict(volume_mm3=float(c.volume()),bounds_mm=mesh(c).bounds.tolist()) for c in chunks[1:] if abs(c.volume())>1e-8]
  assert sum(abs(c['volume_mm3']) for c in remnants)<.1,('export detached material',name,remnants)
  m=cleaned(mesh(chunks[0].as_original().simplify(.002)));mm,T=pose(m,f,n);mm=cleaned(mm)
  if remnants:mm.metadata.setdefault('cleanup',{})['detached_pre_export_remnants']=remnants
  p=DEST/'stl'/folder/(name+'.stl');mm.export(p);re=trimesh.load(p,force='mesh')
  chunks=sorted(re.split(only_watertight=False),key=lambda m:abs(m.volume),reverse=True)
  if len(chunks)>1:
   discarded=sum(abs(m.volume) for m in chunks[1:]);assert discarded<1e-6,(name,'disconnected real material',discarded)
   mm.metadata.setdefault('cleanup',{})['discarded_export_volume_mm3']=discarded;re=chunks[0];re.export(p);re=trimesh.load(p,force='mesh')
  assert re.is_watertight and re.is_winding_consistent and re.volume>0 and len(re.split())==1,(name,'bad export')
  assert abs(re.bounds[0,2])<.005
  restored=trimesh.Trimesh((re.vertices-T[:,3])@T[:,:3],re.faces,process=False);solid=from_mesh(restored);save(solid,CACHE/f'printed-{f}.npz')
  record=dict(name=name,family=f,quantity=quantity,file=p.relative_to(DEST).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mechanism_to_print=T.tolist(),dimensions_mm=np.ptp(re.vertices,axis=0).tolist(),volume_mm3=float(re.volume),triangles=len(re.faces),watertight=True,components=1,cleanup=mm.metadata.get('cleanup',{}))
  if f=='P':record['print_orientation']='inward radial direction down';assert np.linalg.norm(T[:,:3]@(-np.array(n))-[0,0,-1])<1e-8
  if f in ['T','S']:record['print_orientation']='inward radial direction down; screw well upward'
  manifest.append(record);printed[f]=re;solids[f]=solid;return re
 for f,qty in [('T',8),('S',6),('P',24)]:add(load(CACHE/f'final-{f}.npz'),names[f],f,qty,'puzzle',canonical(f)['direction'])
 for f,qty in [('T',8),('S',6)]:add(load(CACHE/f'final-{f}C.npz'),('threefold' if f=='T' else 'fourfold')+f'-plug-print-{qty}',f+'C',qty,'puzzle',canonical(f)['direction'])
 add(core(),'core','core',1,'puzzle')
 add(coupon(5.25),'nut-fit-5.25','nut-coupon',1,'fit-coupons')
 add(stand(),'assembly-stand','stand',1,'optional',canonical('S')['direction'])
 # Restore the default core: the alternate exports use the same family key.
 core_record=next(x for x in manifest if x['file']=='stl/puzzle/core.stl');cm=trimesh.load(DEST/core_record['file'],force='mesh');T=np.array(core_record['mechanism_to_print']);c=cm.copy();c.vertices=(c.vertices-T[:,3])@T[:,:3];solids['core']=from_mesh(c);printed['core']=cm;save(solids['core'],CACHE/'printed-core.npz')
 assembly=[('core',c,[0,0,0])];layout={};instances=[];cap_instances=[]
 for row in ROWS:
  f=row['family'];q=mapping(canonical(f)['signature'],row['signature']);s=xform(solids[f],q);save(s,CACHE/'printed'/(row['name']+'.npz'))
  assembly.append((row['name'],mesh(s),[0,0,0]));layout.setdefault(f,[]).append((row['name'],printed[f]));instances.append(dict(**row,canonical_to_assembly=q.tolist()))
  if f in ['T','S']:
   cap=xform(solids[f+'C'],q);name=row['name']+'-cap';assembly.append((name,mesh(cap),[0,0,0]));layout.setdefault('caps',[]).append((name,printed[f+'C']));cap_instances.append(dict(name=name,family=f+'C',parent=row['name'],canonical_to_assembly=q.tolist()))
 layout['centers-core']=layout.pop('T')+layout.pop('S')+[('core',printed['core'])];plates=[]
 def plate(group,index,objects):
  label=f'{group}-{index:02}';save_3mf(DEST/'plates'/(label+'.3mf'),objects)
  svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="#fafaf8"/>']
  for name,m,shift in objects:
   lo,hi=m.bounds[:,:2]+np.array(shift[:2]);x,y=lo;w,h=hi-lo
   svg.append(f'<rect x="{x:.2f}" y="{256-y-h:.2f}" width="{w:.2f}" height="{h:.2f}" fill="#d9e5ed" stroke="#3b5968" stroke-width=".3"/><text x="{x+w/2:.2f}" y="{256-y-h/2:.2f}" font-family="sans-serif" font-size="3" text-anchor="middle">{name}</text>')
  svg.append('</svg>');(DEST/'plates'/(label+'-map.svg')).write_text(''.join(svg));plates.append(dict(name=label,file=f'plates/{label}.3mf',objects=[x[0] for x in objects]))
 for f,items in layout.items():
  items.sort(key=lambda x:np.ptp(x[1].vertices,axis=0)[1],reverse=True);x=22.;y=14.;height=0;objects=[];idx=1
  for name,m in items:
   w,h=np.ptp(m.vertices,axis=0)[:2]
   if x+w>242:x=22.;y+=height+14;height=0
   if y+h>242:plate(f,idx,objects);idx+=1;objects=[];x=22.;y=14.;height=0
   objects.append((name,m,[x+w/2,y+h/2,0]));x+=w+14;height=max(height,h)
  if objects:plate(f,idx,objects)
 save_3mf(DEST/'reference/DO-NOT-PRINT-solved.3mf',assembly)
 (DEST/'manifest.json').write_text(json.dumps(dict(version='vertex-turning-rhombic-dodecahedron-v5.1-exact-inlays',units='mm',opposite_face_spacing_mm=2*FACE_HEIGHT,opposite_axis_vertex_spacing_mm=2*VERTEX_RADIUS,parts=manifest,plates=plates,instances=instances,cap_instances=cap_instances),indent=2)+'\n')
 (DEST/'reference/parts.json').write_text(json.dumps(ROWS,indent=2)+'\n')
 print('EXPORTED',len(manifest),'files;',len(plates),'plates;',len(assembly),'assembled parts',flush=True)
if __name__=='__main__':export()
