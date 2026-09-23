"""Wonky pentagonal prism: seven 60-degree cones with integral stepped retainers (mm)."""
from pathlib import Path
import itertools,json,os,time
import numpy as np
import manifold3d as mf
import trimesh
from scipy.spatial.transform import Rotation

HERE=Path(__file__).resolve().parent
WORK=Path(os.environ.get('CONICAL_BUILD_DIR',HERE.parent))
CACHE=WORK/'cache'
SIDE=64.
BODY_GAP=.03
TRACK_EXTRA=.40
CORE_R=21.2
CORE_PAD=19.6
INNER_R=21.7
FOOT_PLANE=19.7
FOOT_R=3.1
FOOT_TOP=23.2
SEAT=31.3
NUT_ROOF=17.65
NUT_SEAT_AF=5.20
NUT_ENTRY_AF=5.85
SEG=int(os.environ.get('CONICAL_SEGMENTS','240'))
R=np.array(json.loads((HERE/'chosen_rotation.json').read_text())['cube_to_mechanism_matrix'])
ANGLE=60.
SLOPE=1/np.tan(np.radians(ANGLE))
azimuth=np.arange(5)*2*np.pi/5
AXES=np.vstack([np.column_stack([np.cos(azimuth),np.sin(azimuth),np.zeros(5)]),[0,0,1],[0,0,-1]])
GROUP=[Rotation.from_euler('z',k*72,degrees=True).as_matrix()@q for k in range(5) for q in [np.eye(3),Rotation.from_euler('x',180,degrees=True).as_matrix()]]
ORBITS=['Cs','Cp','V','H','K']
ROWS=[]
adj=sorted({tuple(sorted([k,(k+1)%5])) for k in range(5)})
for family,sigs in [('C',[(i,) for i in range(7)]),('V',adj),('H',[(i,j) for i in range(5) for j in [5,6]]),('K',[(*pair,j) for pair in adj for j in [5,6]])]:
 for k,sig in enumerate(sigs):
  n=AXES[list(sig)].sum(axis=0);n/=np.linalg.norm(n)
  orbit=('Cs' if sig[0]<5 else 'Cp') if family=='C' else family
  ROWS.append(dict(name=f'{family}{k+1:02}',family=family,orbit=orbit,signature=list(sig),direction=n.tolist()))
def canonical(orbit):return next(r for r in ROWS if r['orbit']==orbit)
def replicate(result,s,orbit):
 row=canonical(orbit)
 for rr in (r for r in ROWS if r['orbit']==orbit):result[rr['name']]=xform(s,mapping(row['signature'],rr['signature']))

def matrix(q,t=(0,0,0)):return np.column_stack((q,np.array(t,float)))
def xform(s,q=np.eye(3),t=(0,0,0)):return s.transform(matrix(q,t))
def frame(n):
 n=np.asarray(n,float);seed=np.array([0.,0,1]) if abs(n[2])<.9 else np.array([1.,0,0])
 u=np.cross(seed,n);u/=np.linalg.norm(u)
 return np.column_stack((u,np.cross(n,u),n))
def mesh(s):
 m=s.to_mesh64();return trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
def from_mesh(m):return mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
def union(ss):return mf.Manifold.batch_boolean(list(ss),mf.OpType.Add)
def subtract(s,ss):return mf.Manifold.batch_boolean([s]+list(ss),mf.OpType.Subtract)
def save(s,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);m=mesh(s);np.savez_compressed(path,v=m.vertices,f=m.faces)
def load(path):
 d=np.load(path);return from_mesh(trimesh.Trimesh(d['v'],d['f'],process=False))
def main(s,allowed=.01):
 cs=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True)
 if not cs:raise ValueError('empty solid')
 discarded=sum(abs(c.volume()) for c in cs[1:])
 if discarded>allowed:raise ValueError(('disconnected components',[c.volume() for c in cs]))
 return cs[0]
def mapped(sig,q):return tuple(sorted(int(np.argmin(np.linalg.norm(AXES-q@AXES[i],axis=1))) for i in sig))
def mapping(sig,target):return next(q for q in GROUP if mapped(sig,q)==tuple(target))
def profile():
 # A flat retaining land underneath each mating cell, followed by a neck.
 # Outside radius 32 mm this is exactly the chosen 60-degree cone.
 return [[0,0],[12.6/SLOPE,12.6],[26.5,12.6],[26.5,14.4],
         [14.4/SLOPE,14.4],[180,180*SLOPE],[180,180],[0,180]]
def cut(offset=0,rounding=0):
 p=mf.CrossSection([profile()])
 if offset:p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=32)
 if rounding<0:p=p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=32).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=32)^p
 if rounding>0:p=p+p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=32).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=32)
 if offset>BODY_GAP/2+.001:
  scale=np.sqrt(1+SLOPE*SLOPE)
  ramp=mf.CrossSection([[[26.8,-200],[200,-200],[200,200*SLOPE-BODY_GAP/2*scale],[27.6,27.6*SLOPE-BODY_GAP/2*scale],[26.8,26.8*SLOPE-offset*scale]]])
  p=p-ramp
 if offset<0:p=p+mf.CrossSection.square([1,179],False).translate([0,1])
 return p.revolve(SEG)
def raw_cells():
 inner=mf.Manifold.sphere(INNER_R,SEG);shell=mf.Manifold.cube([160]*3,True)-inner
 small=cut(-BODY_GAP/2,-.60)
 # Wide tracks only inside the mechanism. The exterior returns to .03 mm.
 large=cut(BODY_GAP/2+TRACK_EXTRA,.45)
 ci=[xform(small,frame(n)) for n in AXES];co=[xform(large,frame(n)) for n in AXES]
 cells={}
 for orbit in ORBITS:
  row=canonical(orbit);sig=row['signature'];s=shell
  for i in sig:s=s^ci[i]
  s=subtract(s,[co[i] for i in range(7) if i not in sig])
  chunks=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True)
  print('RAW COMPONENTS',orbit,[round(c.volume(),3) for c in chunks],flush=True)
  s=main(s)
  save(s,CACHE/'raw'/(orbit+'.npz'))
  replicate(cells,s,orbit)
 return cells

def downward_sweep(s,n,clearance=.05):
 f=frame(n);m=mesh(xform(s,f.T));faces=m.triangles[m.face_normals[:,2]>1e-5]
 floor=float(m.bounds[0,2]-100);indices=np.array([[0,1,2],[5,4,3],[0,3,4],[0,4,1],[1,4,5],[1,5,2],[2,5,3],[2,3,0]],dtype=np.uint64)
 prisms=[]
 for p in faces:
  top=p.copy();top[:,2]+=clearance;bottom=top.copy();bottom[:,2]=floor
  v=np.vstack([top,bottom]);q=mf.Manifold(mf.Mesh64(v,indices))
  if not q.is_empty():prisms.append(q)
 return xform(union(prisms),f)

def build_relief(cells):
 result=cells.copy();limit=mf.Manifold.sphere(31.0,SEG)
 for orbit,earlier in [('V',['K']),('H',['K']),('Cs',['K','V','H']),('Cp',['K','V','H'])]:
  row=canonical(orbit);n=np.array(row['direction']);s=cells[row['name']]
  feet=union([s^limit for name,s in result.items() if name[0] in earlier])
  sweep=downward_sweep(feet,n)
  relieved=main(s-sweep)
  save(relieved,CACHE/'relieved'/(orbit+'.npz'))
  print('RELIEF',orbit,'removed',s.volume()-relieved.volume(),'faces',relieved.num_tri(),flush=True)
  replicate(result,relieved,orbit)
 return result

def round_inner_cells(cells):
 result={};limit=mf.Manifold.sphere(28.8,SEG);workball=mf.Manifold.sphere(30.4,SEG)
 for orbit in ORBITS:
  row=canonical(orbit);s=cells[row['name']]
  inner=s^workball;protected=inner-limit;radius=.45 if row['family']=='C' else .60
  kernel=mf.Manifold.sphere(radius,24)
  seed=inner.minkowski_difference(kernel)+protected
  rounded=main(((seed.minkowski_sum(kernel)^inner)+(s-limit))^s)
  save(rounded,CACHE/'inner-rounded'/(orbit+'.npz'))
  print('INNER ROUND',orbit,'removed',s.volume()-rounded.volume(),flush=True)
  replicate(result,rounded,orbit)
 return result

def add_axle(s,n):
 foot=mf.Manifold.cylinder(FOOT_TOP-FOOT_PLANE,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 holes=mf.Manifold.cylinder(100,1.8,1.8,96)+mf.Manifold.cylinder(100,4.8,4.8,128).translate([0,0,SEAT])
 return main((s+xform(foot,frame(n)))-xform(holes,frame(n)))

def clip(cells):
 cube=xform(mf.Manifold.cube([SIDE]*3,True),R)
 return {r['name']:add_axle(cells[r['name']]^cube,np.array(r['direction'])) if r['family']=='C' else main(cells[r['name']]^cube) for r in ROWS}

def radial_tests(cells):
 out=[]
 for r in ROWS:
  if r['family']=='C':continue
  name=r['name'];n=np.array(r['direction']);s=cells[name]
  others=union([c for k,c in cells.items() if k!=name])
  contact=None
  for d in np.r_[np.arange(.1,2.01,.1),np.arange(2.5,10.1,.5)]:
   v=(s.translate(d*n)^others).volume()
   if v>.01:contact=[round(float(d),3),float(v)];break
  out.append(dict(name=name,contact=contact))
 return out

def insertion_tests(cells):
 out=[]
 for r in ROWS:
  if r not in [canonical(o) for o in ORBITS]:continue
  name=r['name'];n=np.array(r['direction']);rank={'K':0,'V':1,'H':1,'C':2};rr=rank[r['family']]
  others=union([s for k,s in cells.items() if k!=name and rank[k[0]]<=rr])
  worst=[0,0]
  for d in np.r_[np.arange(0,8.01,.25),np.arange(9,101,2)]:
   v=(cells[name].translate(d*n)^others).volume()
   if v>worst[1]:worst=[float(d),v]
  out.append(dict(name=name,worst=worst))
 return out

if __name__=='__main__':
 CACHE.mkdir(parents=True,exist_ok=True);t=time.time();cells=raw_cells()
 print('RAW',time.time()-t,flush=True)
 print('RAW RETENTION',radial_tests(cells),flush=True)
 cells=build_relief(cells);print('RELIEVED',time.time()-t,flush=True)
 print('RETENTION',radial_tests(cells),flush=True)
 print('INSERT',insertion_tests(cells),flush=True)
 for name,s in clip(cells).items():save(s,CACHE/'trial'/(name+'.npz'))
 (CACHE/'parts.json').write_text(json.dumps(ROWS,indent=2))
 print('FINISHED',time.time()-t,flush=True)

def hex_section(af):
 return mf.CrossSection([[[af/np.sqrt(3)*np.cos(t),af/np.sqrt(3)*np.sin(t)] for t in np.arange(6)*np.pi/3]])
def nut_slot(af=NUT_SEAT_AF):
 half=af/2;entry=NUT_ENTRY_AF/2
 # Only the last 3.0 mm of the loading channel grips the nut flats.
 # A 3.0 mm lead-in connects that seat to the wider mouth.
 channel=mf.CrossSection([[[0,-half],[3.0,-half],[6.,-entry],[35,-entry],[35,entry],[6.,entry],[3.0,half],[0,half]]])
 return (hex_section(af)+channel).extrude(4.25).translate([0,0,NUT_ROOF-4.25])
def nut_shape():
 return hex_section(5.5).extrude(4.).translate([0,0,NUT_ROOF-4.])-mf.Manifold.cylinder(40,1.5,1.5,72)
def core(af=NUT_SEAT_AF):
 s=mf.Manifold.sphere(CORE_R,SEG)
 for n in AXES:s=s.trim_by_plane(-n,-CORE_PAD)
 cutters=[xform(nut_slot(af)+mf.Manifold.cylinder(80,1.7,1.7,96).translate([0,0,-40]),frame(n)) for n in AXES]
 return main(subtract(s,cutters))
def hardware(n,lift=0.):
 z=SEAT+lift
 screw=mf.Manifold.cylinder(20,1.5,1.5,96).translate([0,0,z+1-20])+mf.Manifold.cylinder(3,2.75,2.75,96).translate([0,0,z+1])
 washer=(mf.Manifold.cylinder(1,4.5,4.5,96)-mf.Manifold.cylinder(1,1.6,1.6,96)).translate([0,0,z])
 return xform(screw,frame(n)),xform(washer,frame(n))
def coupon(af):
 block=mf.Manifold.cube([24,18,10],False).translate([-12,-9,CORE_PAD-10])
 return main(block-nut_slot(af)-mf.Manifold.cylinder(40,1.7,1.7,96))
def rotor_coupon():
 stem=mf.Manifold.cylinder(SEAT-FOOT_PLANE+4,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 cup=mf.Manifold.cylinder(7,6,6,96).translate([0,0,SEAT-3])
 return main(stem+cup-mf.Manifold.cylinder(80,1.8,1.8,96)-mf.Manifold.cylinder(80,4.8,4.8,128).translate([0,0,SEAT]))
