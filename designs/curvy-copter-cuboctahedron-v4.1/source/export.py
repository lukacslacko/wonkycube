"""Export standalone millimetre STLs and geometry-only print/reference 3MFs."""
from caps import *
from mesh_io import cleaned
from print_3mf import save_3mf
import hashlib,shutil
NAMES={'C':'axial-center-print-12','P':'petal-print-24','K':'floating-corner-print-8','cap':'keyed-plug-print-12','core':'core'}
COUNT={'C':12,'P':24,'K':8,'cap':12,'core':1}
def export():
 for p in ['stl/puzzle','stl/fit-coupons','plates','reference','reports','images']:(DEST/p).mkdir(parents=True,exist_ok=True)
 records=[];printed={};solids={}
 old=json.loads((HERE/'fixed-baseline/manifest.json').read_text())
 for f in ['C','P','K','cap','core']:
  path=DEST/'stl/puzzle'/(NAMES[f]+'.stl')
  if f=='core':
   rec=next(r for r in old['parts'] if r['file']=='stl/puzzle/core.stl');T=np.array(rec['mechanism_to_print'])
   shutil.copy2(HERE/'fixed-baseline/core.stl',path);m=trimesh.load(path,force='mesh')
  else:
   s=load(CACHE/f'final-{f}.npz');n=np.array(canonical('C' if f=='cap' else f)['direction']);q=frame(n).T
   m=mesh(xform(s,q));t=-np.r_[m.bounds[:,:2].mean(axis=0),m.bounds[0,2]];m.vertices+=t
   m=cleaned(m);m.export(path);T=matrix(q,t)
  m=trimesh.load(path,force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
  printed[f]=m;mm=m.copy();mm.vertices=(mm.vertices-T[:,3])@T[:,:3];s=from_mesh(mm);solids[f]=s;save(s,CACHE/f'printed-{f}.npz')
  records.append(dict(family=f,name=NAMES[f],quantity=COUNT[f],file=path.relative_to(DEST).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),mechanism_to_print=T.tolist(),dimensions_mm=m.extents.tolist(),volume_mm3=float(m.volume),triangles=len(m.faces),watertight=True,components=1,orientation='original flat axle pad down' if f=='core' else 'inward radial direction down; exterior pockets up'))
  print('EXPORTED',f,len(m.faces),flush=True)
 # Four reasonably spaced plates. Slice with support as documented; no
 # machine profile or untested support settings are embedded in these 3MFs.
 plates=[]
 for f in ['C','P','K','cap']:
  items=[];m=printed[f];spacing=m.extents[:2]+14;cols=min(6,int(226//spacing[0]));cols=max(1,cols)
  for i in range(COUNT[f]):
   x=(i%cols)*spacing[0]+25+m.extents[0]/2;y=(i//cols)*spacing[1]+25+m.extents[1]/2
   assert x+m.extents[0]/2<245 and y+m.extents[1]/2<245,(f,x,y)
   items.append((f'{f}{i+1:02}',m,[x,y,0]))
  name={'C':'01-centers','P':'02-petals','K':'03-floating-corners','cap':'04-keyed-plugs'}[f]
  save_3mf(DEST/'plates'/(name+'.3mf'),items);plates.append(dict(file='plates/'+name+'.3mf',objects=[i[0] for i in items]))
 instances=[];assembled=[('core',mesh(solids['core']),[0,0,0])]
 for row in ROWS:
  q=mapping(canonical(row['family'])['signature'],row['signature']);instances.append(dict(**row,canonical_to_assembly=q.tolist()))
  assembled.append((row['name'],mesh(xform(solids[row['family']],q)),[0,0,0]))
  if row['family']=='C':assembled.append((row['name']+'-plug',mesh(xform(solids['cap'],q)),[0,0,0]))
 save_3mf(DEST/'reference/DO-NOT-PRINT-assembled.3mf',assembled)
 # Fast fit coupon has the exact socket and the same ribbed key as the plug.
 female,male=keys();h=4.25
 socket=mf.Manifold.cube([18,17,6.25],False).translate([-9,-8.5,0])-cross(female).extrude(8).translate([0,0,2])
 couponkey=cross(male).extrude(3.5)+ribs().translate([0,0,-KEY_BOTTOM])
 couponkey+=mf.Manifold.cylinder(3,3,3,48).translate([0,0,3.45])
 for name,s in [('plug-socket-fit-test',socket),('plug-key-fit-test',couponkey)]:cleaned(mesh(s)).export(DEST/'stl/fit-coupons'/(name+'.stl'))
 meta=dict(version=RELEASE_VERSION,units='mm',square_face_spacing_mm=SIZE,pocket_depth_mm=DEPTH,nominal_pocket_border_mm=RIM,inlay_count=104,hardware=dict(screws='12 DIN912 M3 x 20',washers='12 of 9 mm OD x 1 mm',nuts='12 DIN985 M3',terminal_nut_seat_af_mm=5.25),spherical_retention=old['spherical_retention'],parts=records,plates=plates,instances=instances)
 (DEST/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
 for name in ['inlays','caps','baseline','rounding-repair']:(DEST/'reports'/(name+'.json')).write_text((CACHE/(name+'.json')).read_text())
if __name__=='__main__':export()
