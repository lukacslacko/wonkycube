"""Export and reload Wavy Redi parts with stable solved-location IDs."""
from redi_design import *
from mesh_io import cleaned as clean_mesh
from print_3mf import save_3mf
import hashlib,html

DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
PARTIAL='--partial' in sys.argv[2:]
for folder in ['stl/puzzle','stl/fit-coupons','stl/optional','plates','reference','reports','images']:(DEST/folder).mkdir(parents=True,exist_ok=True)
manifest=[];groups={};reference=[]
old=json.loads((DEST/'manifest.json').read_text()) if (DEST/'manifest.json').exists() else {}
cached={r['name']:r for r in old.get('parts',[])}

def orient(s,kind,n=None):
 source=mesh(s);source.metadata['cleanup']={'simplification_mm':.002}
 m=clean_mesh(source);bed_area=None
 if kind=='edge':q=Rotation.align_vectors([[0,0,1]],[n])[0].as_matrix()
 elif kind in ['axis','core']:
  choices=[]
  for j in range(3):
   for sign in [-1,1]:
    normal=R[:,j]*sign
    hit=(m.face_normals@normal>.999)&((m.triangles@normal).min(axis=1)>SIDE/2-.01)
    choices.append((float(m.area_faces[hit].sum()),normal))
  bed_area,normal=max(choices,key=lambda a:a[0]);assert bed_area>4
  q=Rotation.align_vectors([[0,0,-1]],[normal])[0].as_matrix()
 elif kind=='stand':q=Rotation.align_vectors([[0,0,-1]],[n])[0].as_matrix()
 else:q=np.eye(3)
 v=m.vertices@q.T;best=None
 for angle in np.arange(0,180,2):
  z=Rotation.from_euler('z',angle,degrees=True).as_matrix();dims=np.ptp(v@z.T,axis=0)
  score=dims[0]*dims[1]+.2*max(dims[:2])**2
  if best is None or score<best[0]:best=(score,z)
 q=best[1]@q;v=m.vertices@q.T
 shift=-np.r_[((v.max(axis=0)+v.min(axis=0))/2)[:2],v[:,2].min()]
 m.vertices=v+shift
 return clean_mesh(m),matrix(q,shift),bed_area

def add(name,s,folder,kind,n=None,group=None):
 path=DEST/'stl'/folder/(name+'.stl');source=mesh(s)
 fingerprint=hashlib.sha256(source.vertices.tobytes()+source.faces.tobytes()).hexdigest()
 prior=cached.get(name)
 if prior and kind=='edge' and prior.get('print_orientation')!='inward-radial-down-v1':prior=None
 if prior and prior['geometry_sha256']==fingerprint and path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==prior['sha256']:
  rec=prior;re=trimesh.load(path,force='mesh');T=np.array(rec['mechanism_to_print'])
 else:
  s=main(s).as_original().simplify(.002);m,T,area=orient(s,kind,n);m.export(path)
  re=trimesh.load(path,force='mesh')
  assert re.is_watertight and re.is_winding_consistent and re.volume>0 and len(re.split())==1,name
  dims=np.ptp(re.vertices,axis=0);assert max(dims)<232
  first=from_mesh(re).slice(.16).area();assert first>(0 if kind=='edge' else 4),(name,first)
  rec=dict(name=name,role=kind,quantity=1,file=str(path.relative_to(DEST)),dimensions_mm=dims.tolist(),solid_volume_mm3=float(re.volume),triangles=len(re.faces),watertight=True,components=1,bed_face_area_mm2=area,first_layer_0_16_mm_area_mm2=first,cleanup=m.metadata.get('cleanup',{}),mechanism_to_print=T.tolist(),geometry_sha256=fingerprint,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
 if kind=='edge':rec['print_orientation']='inward-radial-down-v1'
 manifest.append(rec);groups.setdefault(group or folder,[]).append((name,re))
 restored=trimesh.Trimesh((re.vertices-T[:,3])@T[:,:3],re.faces,process=False)
 save(from_mesh(restored),OUT/'printed'/(name+'.npz'))
 if folder=='puzzle':reference.append((name,mesh(xform(from_mesh(restored),R.T)),[0,0,0]))
 (DEST/'manifest.json').write_text(json.dumps(dict(version='wavy-redi-v1.1',units='millimeter',cube_side_mm=SIDE,parts=manifest),indent=2))
 print(name,len(re.faces),flush=True)

for row in ROWS:
 if PARTIAL and not (OUT/'final'/(row['name']+'.npz')).exists():continue
 name=row['name'];add(name,load(OUT/'final'/(name+'.npz')),'puzzle','axis' if name[0]=='C' else 'edge',np.array(row['direction']),group='core-and-axles' if name[0]=='C' else 'petals')
add('core',load(OUT/'final/core.npz'),'puzzle','core',AXES[0],group='core-and-axles')
block=mf.Manifold.cube([24,18,10],False).translate([-12,-9,CORE_PAD-10])
coupon=main(block-nut_slot()-mf.Manifold.cylinder(40,1.7,1.7,96)).translate([0,0,10-CORE_PAD])
add('nut-fit-5.25',coupon,'fit-coupons','coupon')
plates=[]
def write_plate(group,index,objects):
 name=f'{group}-{index:02}';path=DEST/'plates'/(name+'.3mf');save_3mf(path,objects)
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="#f7f7f4"/>']
 for label,m,pos in objects:
  b=m.bounds[:,:2]+np.array(pos[:2]);x,y=b[0];w,h=b[1]-b[0]
  svg.append(f'<rect x="{x:.2f}" y="{256-y-h:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1" fill="#d8e8ef" stroke="#44697c" stroke-width=".35"/><text x="{x+w/2:.2f}" y="{256-y-h/2:.2f}" text-anchor="middle" font-family="sans-serif" font-size="3">{html.escape(label)}</text>')
 svg.append('</svg>');(DEST/'plates'/(name+'-map.svg')).write_text(''.join(svg))
 plates.append(dict(name=name,objects=[n for n,_,_ in objects],file=str(path.relative_to(DEST))))
for group,items in groups.items():
 items=sorted(items,key=lambda a:np.ptp(a[1].vertices,axis=0)[1],reverse=True)
 objects=[];x=12.;y=12.;height=0.;index=1
 for name,m in items:
  w,h=np.ptp(m.vertices,axis=0)[:2]
  if x+w>244:x=12.;y+=height+8;height=0.
  if y+h>244:
   write_plate(group,index,objects);index+=1;objects=[];x=12.;y=12.;height=0.
  objects.append((name,m,[x+w/2,y+h/2,0]));x+=w+8;height=max(height,h)
 if objects:write_plate(group,index,objects)
save_3mf(DEST/'reference/DO-NOT-PRINT-assembled-cube.3mf',reference)
(DEST/'manifest.json').write_text(json.dumps(dict(version='wavy-redi-v1.1',selection_id=SPEC['selection_id'],units='millimeter',cube_side_mm=SIDE,body_gap_mm=BODY_GAP,track_clearance_mm=TRACK_CLEARANCE,ridge_rounding_mm=ROUND_R,parts=manifest,plates=plates),indent=2))
(DEST/'reference/parts.json').write_text(json.dumps(ROWS,indent=2))
(DEST/'reference/cube-to-mechanism.json').write_text(json.dumps(R.tolist(),indent=2))
page='<meta charset="utf-8"><title>Wavy Redi print plates</title><style>body{font:16px system-ui;max-width:1050px;margin:40px auto}section{display:inline-block;width:48%;vertical-align:top}img{width:100%}h2{font-size:18px}</style><h1>Wavy Redi · print plate maps</h1><p>Geometry-only plates: set PLA/support settings. Mark each part with its full ID. Assembly order is mandatory: see ASSEMBLY.md.</p>'
for p in plates:page+=f'<section><h2>{p["name"]}</h2><img src="plates/{p["name"]}-map.svg"></section>'
(DEST/'plate-maps.html').write_text(page)
print('EXPORTED',len(manifest),'STLs',len(plates),'plates',flush=True)
