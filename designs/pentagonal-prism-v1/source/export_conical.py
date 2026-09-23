"""Closed print STLs, named 3MF plates and explicit print/assembly transforms."""
from conical_design import *
from finish_conical import stand
from mesh_io import cleaned
from print_3mf import save_3mf
import hashlib,html,sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
for folder in ['stl/puzzle','stl/fit-coupons','stl/optional','plates','print-options','reference','reports','images']:(DEST/folder).mkdir(parents=True,exist_ok=True)
manifest=[];groups={};assembly=[];orientation_options=[]

def oriented_copy(m,kind,n=None):
 m=m.copy();bed_area=None
 if kind in ['V','H','radial-down']:q=Rotation.align_vectors([[0,0,1]],[n])[0].as_matrix()
 elif kind in ['C','K','face-down']:
  choices=[]
  for j in range(3):
   for sign in [-1,1]:
    normal=R[:,j]*sign;hit=(m.face_normals@normal>.999)&((m.triangles@normal).min(axis=1)>SIDE/2-.01)
    choices.append((float(m.area_faces[hit].sum()),normal))
  bed_area,normal=max(choices,key=lambda p:p[0]);assert bed_area>4
  q=Rotation.align_vectors([[0,0,-1]],[normal])[0].as_matrix()
 elif kind in ['core','stand']:q=Rotation.align_vectors([[0,0,-1]],[n])[0].as_matrix()
 else:q=np.eye(3)
 v=m.vertices@q.T;best=None
 for angle in np.arange(0,180,2):
  z=Rotation.from_euler('z',angle,degrees=True).as_matrix();dim=np.ptp(v@z.T,axis=0);score=dim[0]*dim[1]+.2*max(dim[:2])**2
  if best is None or score<best[0]:best=(score,z)
 q=best[1]@q;v=m.vertices@q.T;shift=-np.r_[((v.max(axis=0)+v.min(axis=0))/2)[:2],v[:,2].min()]
 m.vertices=v+shift
 return m,matrix(q,shift),bed_area

def orient(s,kind,n=None):
 m=cleaned(mesh(main(s).simplify(.001)))
 m,t,area=oriented_copy(m,kind,n)
 return cleaned(m),t,area

def add(name,s,folder,kind,n=None,group=None,description=None):
 m,T,area=orient(s,kind,n);path=DEST/'stl'/folder/(name+'.stl');m.export(path)
 re=trimesh.load(path,force='mesh');assert re.is_watertight and re.is_winding_consistent and re.volume>0 and len(re.split())==1,name
 assert np.max(np.ptp(re.vertices,axis=0))<230
 assert abs(re.bounds[0,2])<.005
 rec=dict(name=name,family=kind,quantity=1,file=path.relative_to(DEST).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions_mm=np.ptp(re.vertices,axis=0).tolist(),volume_mm3=float(re.volume),triangles=len(re.faces),watertight=True,components=1,mechanism_to_print=T.tolist(),cleanup=m.metadata.get('cleanup',{}),bed_face_area_mm2=area,first_layer_0_16_mm_area_mm2=float(from_mesh(re).slice(.16).area()))
 if kind in ['V','H']:
  rec['print_orientation']='inward-radial-down';rec['inward_vector_print']=(-np.array(n)@T[:,:3].T).tolist();assert np.linalg.norm(np.array(rec['inward_vector_print'])-[0,0,-1])<1e-9
 if description:rec['description']=description
 manifest.append(rec);groups.setdefault(group or kind,[]).append((name,re))
 restored=trimesh.Trimesh((re.vertices-T[:,3])@T[:,:3],re.faces,process=False);save(from_mesh(restored),CACHE/'printed'/(name+'.npz'))
 if folder=='puzzle':assembly.append((name,mesh(xform(from_mesh(restored),R.T)),[0,0,0]))
 print('EXPORT',name,len(re.faces),flush=True)

for row in ROWS:add(row['name'],load(CACHE/'final'/(row['name']+'.npz')),'puzzle',row['family'],row['direction'])
for row in (r for r in ROWS if r['family'] in ['V','H','K']):
 name=row['name'];entry=next(r for r in manifest if r['name']==name)
 m=trimesh.load(DEST/entry['file'],force='mesh');t=np.array(entry['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 # Indexed double-precision 3MF preserves the validated STL exactly under a
 # rigid reorientation; a second binary float32 STL would requantize it.
 option='face-down' if row['family'] in ['V','H'] else 'radial-down'
 m,t,area=oriented_copy(m,option,row['direction'])
 path=DEST/'print-options'/(name+'-'+option+'.3mf');save_3mf(path,[(name,m,[128,128,0])])
 orientation_options.append(dict(name=name,file=path.relative_to(DEST).as_posix(),mechanism_to_print=t.tolist(),bed_face_area_mm2=area,first_layer_0_16_mm_area_mm2=float(from_mesh(m).slice(.16).area())))
 groups.setdefault(row['family']+'-'+option,[]).append((name,m))
add('core',core(),'puzzle','core',AXES[0],description='5.20 mm terminal seat, 5.85 mm loading entrance')
for af in [5.30,5.40]:add(f'core-seat-{af:.2f}',core(af),'optional','core',AXES[0],group='alternate-cores',description=f'{af:.2f} mm terminal seat; choose only one core')
for af in [5.20,5.30,5.40]:add(f'nut-fit-{af:.2f}',coupon(af),'fit-coupons','coupon',group='fit-coupons')
add('rotor-fit',rotor_coupon(),'fit-coupons','coupon',group='fit-coupons')
add('assembly-stand',stand(),'optional','stand',AXES[0])
plates=[]
def plate(group,index,objects):
 name=f'{group}-{index:02}';path=DEST/'plates'/(name+'.3mf');save_3mf(path,objects)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="#f7f7f4"/>']
 for label,m,pos in objects:
  lo,hi=m.bounds[:,:2]+np.array(pos[:2]);x,y=lo;w,h=hi-lo
  svg.append(f'<rect x="{x:.2f}" y="{256-y-h:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1" fill="#d8e8ef" stroke="#44697c" stroke-width=".35"/><text x="{x+w/2:.2f}" y="{256-y-h/2:.2f}" text-anchor="middle" font-family="sans-serif" font-size="3">{html.escape(label)}</text>')
 svg.append('</svg>');(DEST/'plates'/(name+'-map.svg')).write_text(''.join(svg))
 plates.append(dict(name=name,file=path.relative_to(DEST).as_posix(),objects=[o[0] for o in objects]))
for group,items in groups.items():
 items=sorted(items,key=lambda a:np.ptp(a[1].vertices,axis=0)[1],reverse=True)
 objects=[];x=y=12.;height=0.;idx=1
 for name,m in items:
  w,h=np.ptp(m.vertices,axis=0)[:2]
  if x+w>244:x=12.;y+=height+8;height=0.
  if y+h>244:plate(group,idx,objects);idx+=1;objects=[];x=y=12.;height=0.
  objects.append((name,m,[x+w/2,y+h/2,0]));x+=w+8;height=max(height,h)
 if objects:plate(group,idx,objects)
save_3mf(DEST/'reference/DO-NOT-PRINT-solved.3mf',assembly)
(DEST/'manifest.json').write_text(json.dumps(dict(version='wonky-pentagonal-prism-60-v1',units='millimeter',cube_side_mm=SIDE,core_seat_af_mm=NUT_SEAT_AF,parts=manifest,orientation_options=orientation_options,plates=plates),indent=2))
(DEST/'reference/parts.json').write_text(json.dumps(ROWS,indent=2));(DEST/'reference/cube-to-mechanism.json').write_text(json.dumps(R.tolist(),indent=2))
(DEST/'reference/ridge-sections.json').write_text((CACHE/'ridges-2/sections.json').read_text())
page='<meta charset="utf-8"><title>Wonky pentagonal prism — 60° print plates</title><style>body{font:16px system-ui;max-width:1050px;margin:40px auto}section{display:inline-block;width:48%;vertical-align:top}img{width:100%}h2{font-size:18px}</style><h1>Wonky pentagonal prism — 60° — plate maps</h1><p>Millimetres, 100% scale. Geometry only. Mark every piece with its full ID.</p>'
for p in plates:page+=f'<section><h2>{p["name"]}</h2><img src="plates/{p["name"]}-map.svg"></section>'
(DEST/'plate-maps.html').write_text(page)
print('COMPLETE',len(manifest),'STLs',len(plates),'plates',flush=True)
