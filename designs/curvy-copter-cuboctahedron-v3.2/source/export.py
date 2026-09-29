from hardware import *
from mesh_io import cleaned
from print_3mf import save_3mf
import hashlib,html,shutil
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
FACES=[(np.eye(3)[k]*sgn,SIZE/2,f'S{"XYZ"[k]}{"+" if sgn>0 else "-"}') for k in range(3) for sgn in [-1,1]]
FACES += [(np.array(v)/np.sqrt(3),SIZE/np.sqrt(3),'T'+''.join('+' if k>0 else '-' for k in v)) for v in itertools.product([-1,1],repeat=3)]
def pose(m,f,n):
 if f=='P':q=Rotation.align_vectors([[0,0,1]],[n])[0].as_matrix()
 elif f in ['C','K']:
  scores=[]
  for normal,h,label in FACES:
   mask=(m.face_normals@normal>.999)&(np.max(abs(m.triangles@normal-h),axis=1)<.008)
   scores.append((float(m.area_faces[mask].sum()),normal))
  area,normal=max(scores,key=lambda x:x[0]);assert area>10
  q=Rotation.align_vectors([[0,0,-1]],[normal])[0].as_matrix()
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
 manifest=[];printed={};solids={};names={'C':'axial-center-print-12','P':'petal-print-24','K':'corner-print-8'}
 def add(s,name,f,quantity,folder,n=None):
  chunks=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True)
  remnants=[dict(volume_mm3=float(c.volume()),bounds_mm=mesh(c).bounds.tolist()) for c in chunks[1:] if abs(c.volume())>1e-8]
  assert sum(abs(c['volume_mm3']) for c in remnants)<.1,('export detached material',name,remnants)
  m=cleaned(mesh(chunks[0].as_original().simplify(.002)));mm,T=pose(m,f,n);mm=cleaned(mm)
  if remnants:mm.metadata.setdefault('cleanup',{})['detached_pre_export_remnants']=remnants
  p=DEST/'stl'/folder/(name+'.stl');mm.export(p)
  if f=='K':
   # Keep the user's successful floating-corner STL literally unchanged.
   # The parametric source still builds it, checked equivalent below.
   assert SIZE==72 and SHOULDER_R==28.5 and COLLAR_OUTER_R==33.5 and NECK_ANGLE==40
   fixed=HERE/'fixed-parts';prior=json.loads((fixed/'corner-record.json').read_text())
   old=trimesh.load(fixed/'corner-print-8.stl',force='mesh');oldT=np.array(prior['mechanism_to_print'])
   restored=trimesh.Trimesh((old.vertices-oldT[:,3])@oldT[:,:3],old.faces,process=False);oldsolid=from_mesh(restored)
   candidate=trimesh.load(p,force='mesh');candidate.vertices=(candidate.vertices-T[:,3])@T[:,:3];candidate=from_mesh(candidate)
   assert (candidate-oldsolid).volume()+(oldsolid-candidate).volume()<.0001
   shutil.copy2(fixed/'corner-print-8.stl',p);mm=old;T=oldT;mm.metadata['cleanup']=prior['cleanup']
  re=trimesh.load(p,force='mesh')
  chunks=sorted(re.split(only_watertight=False),key=lambda m:abs(m.volume),reverse=True)
  if len(chunks)>1:
   discarded=sum(abs(m.volume) for m in chunks[1:]);assert discarded<1e-6,(name,'disconnected real material',discarded)
   mm.metadata.setdefault('cleanup',{})['discarded_export_volume_mm3']=discarded;re=chunks[0];re.export(p);re=trimesh.load(p,force='mesh')
  assert re.is_watertight and re.is_winding_consistent and re.volume>0 and len(re.split())==1,(name,'bad export')
  assert abs(re.bounds[0,2])<.005
  restored=trimesh.Trimesh((re.vertices-T[:,3])@T[:,:3],re.faces,process=False);solid=from_mesh(restored);save(solid,CACHE/f'printed-{f}.npz')
  record=dict(name=name,family=f,quantity=quantity,file=p.relative_to(DEST).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),mechanism_to_print=T.tolist(),dimensions_mm=np.ptp(re.vertices,axis=0).tolist(),volume_mm3=float(re.volume),triangles=len(re.faces),watertight=True,components=1,cleanup=mm.metadata.get('cleanup',{}))
  if f=='P':record['print_orientation']='inward radial direction down';assert np.linalg.norm(T[:,:3]@(-np.array(n))-[0,0,-1])<1e-8
  manifest.append(record);printed[f]=re;solids[f]=solid;return re
 for f,qty in [('C',12),('P',24),('K',8)]:add(load(CACHE/f'final-{f}.npz'),names[f],f,qty,'puzzle',canonical(f)['direction'])
 add(core(),'core','core',1,'puzzle')
 for af in [5.20,5.25,5.30]:add(coupon(af),f'nut-fit-{af:.2f}','coupon-'+str(af),1,'fit-coupons')
 for af in [5.20,5.30]:add(core(af),f'core-seat-{af:.2f}','core',1,'optional')
 add(stand(),'assembly-stand','stand',1,'optional',canonical('C')['direction'])
 # Restore the default core: the alternate exports use the same family key.
 core_record=next(x for x in manifest if x['file']=='stl/puzzle/core.stl');cm=trimesh.load(DEST/core_record['file'],force='mesh');T=np.array(core_record['mechanism_to_print']);c=cm.copy();c.vertices=(c.vertices-T[:,3])@T[:,:3];solids['core']=from_mesh(c);printed['core']=cm;save(solids['core'],CACHE/'printed-core.npz')
 assembly=[('core',c,[0,0,0])];layout={};instances=[]
 for row in ROWS:
  f=row['family'];q=mapping(canonical(f)['signature'],row['signature']);s=xform(solids[f],q);save(s,CACHE/'printed'/(row['name']+'.npz'))
  assembly.append((row['name'],mesh(s),[0,0,0]));layout.setdefault(f,[]).append((row['name'],printed[f]));instances.append(dict(**row,canonical_to_assembly=q.tolist()))
 layout['C'].append(('core',printed['core']));plates=[]
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
 (DEST/'manifest.json').write_text(json.dumps(dict(version=RELEASE_VERSION,units='mm',square_face_spacing_mm=SIZE,spherical_retention=dict(shoulder_radius_mm=SHOULDER_R,collar_outer_radius_mm=COLLAR_OUTER_R,neck_angle_degrees=NECK_ANGLE,petal_groove_extra_width_mm=PETAL_GROOVE_WIDTH_EXTRA,petal_to_center_bearing_clearance_mm=BODY_GAP+TRACK_EXTRA+PETAL_WALL_EXTRA,corner_to_petal_bearing_clearance_mm=BODY_GAP+TRACK_EXTRA,center_flange_end_rounding_mm=CENTER_FLANGE_END_ROUNDING,center_flange_rounding_direction='transverse outline, swept radially; original bearing rims retained'),parts=manifest,plates=plates,instances=instances),indent=2)+'\n')
 (DEST/'reference/parts.json').write_text(json.dumps(ROWS,indent=2)+'\n')
 print('EXPORTED',len(manifest),'files;',len(plates),'plates;',len(assembly),'assembled parts',flush=True)
if __name__=='__main__':export()
