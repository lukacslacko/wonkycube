"""Compact Redi v4.3: regenerated v4.2 rails with captive locknuts (mm)."""
from mechanism import *
from exact_assembly_sweep import downward_sweep
from mechanism_v4 import rotational_profile
import sys, time, os

HERE=Path(__file__).resolve().parent
WORK=Path(os.environ.get('REDI_BUILD_DIR',HERE.parent))
OUT=WORK/'cache'
SIDE=64.
SCALE=SIDE/80.
BODY_GAP=.03
TRACK_CLEARANCE=.40
CORE_R=24*SCALE
CORE_PAD=22*SCALE
INNER_R=CORE_R+.5
FOOT_PLANE=CORE_PAD+.10
FOOT_TOP=25.5*SCALE
FOOT_R=3.2
SEAT=34*SCALE+.10
STAND_SEAT=28.5
ACCESS_D=9.6
BORE_D=3.6
NUT_ROOF=CORE_PAD-1.95
NUT_HEIGHT=4.
RAIL_RADIUS=28*SCALE
INNER_LIMIT=35.5*SCALE
INNER_WORK=37*SCALE
ROUND_R=3.
EDGE_ROUND=.60
CORNER_ROUND=.45
OUTER_ROUND=.8
SEG=288
R=np.array(json.loads((HERE/'chosen_rotation.json').read_text())['cube_to_mechanism_matrix'])
GROUP=[]
for order in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  q=np.eye(3)[list(order)]*np.array(signs)[:,None]
  if np.linalg.det(q)>.5:GROUP.append(q)
ROWS=[dict(name=f'C{i+1:02}',signature=[i],direction=n.tolist()) for i,n in enumerate(AXES)]
ROWS += [dict(name=f'E{k+1:02}',signature=list(pair),direction=((AXES[pair[0]]+AXES[pair[1]])/np.linalg.norm(AXES[pair[0]]+AXES[pair[1]])).tolist()) for k,pair in enumerate(EDGES)]

def mapped(sig,q):return tuple(sorted(int(np.argmin(np.linalg.norm(AXES-q@AXES[i],axis=1))) for i in sig))
def mapping(sig,target):return next(q for q in GROUP if mapped(sig,q)==tuple(target))
def save(s,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);m=mesh(s)
 np.savez_compressed(path,v=m.vertices,f=m.faces)
def load(path):
 z=np.load(path);return from_mesh(trimesh.Trimesh(z['v'],z['f'],process=False))
def main(s,allowed=.001):
 pieces=sorted(s.decompose(),key=lambda x:x.volume(),reverse=True)
 if not pieces:raise ValueError('empty part')
 if sum(abs(p.volume()) for p in pieces[1:])>allowed:raise ValueError(('disconnected material',[p.volume() for p in pieces]))
 return pieces[0]
def profile():
 return (np.array([[0,0],[np.sqrt(2)*14,14],[27.6,14],[28,14.4],
  [28,16.8],[27.8,17],[np.sqrt(2)*17,17],[np.sqrt(2)*150,150],[0,150]])*SCALE).tolist()
def cut(offset=0):
 p=mf.CrossSection([profile()])
 if offset:p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=48)
 return p.revolve(SEG)
def raw_cells():
 shell=mf.Manifold.sphere(SIDE*.95,SEG)-mf.Manifold.sphere(INNER_R,SEG)
 ci=[xform(cut(-BODY_GAP/2),frame(n)) for n in AXES]
 co=[xform(cut(BODY_GAP/2),frame(n)) for n in AXES]
 cells={}
 for row in ROWS:
  sig=row['signature'];s=shell
  for a in sig:s=s^ci[a]
  s=subtract(s,[co[a] for a in range(8) if a not in sig])
  chunks=sorted(s.decompose(),key=lambda p:p.volume(),reverse=True)
  for p in chunks[1:]:
   assert np.linalg.norm(mesh(p).vertices,axis=1).max()<33.1*SCALE
  cells[row['name']]=chunks[0]
 return cells
def protected_axle(n):
 stem=mf.Manifold.cylinder(100,FOOT_R+.05,FOOT_R+.05,144).translate([0,0,CORE_PAD-1])
 cup=mf.Manifold.cylinder(100,6,6,144).translate([0,0,SEAT-.8])
 return xform(stem+cup,frame(n))
def finish_hardware(s,n):
 foot=mf.Manifold.cylinder(FOOT_TOP-FOOT_PLANE,FOOT_R,FOOT_R,144).translate([0,0,FOOT_PLANE])
 bore=mf.Manifold.cylinder(150,BORE_D/2,BORE_D/2,144)
 well=mf.Manifold.cylinder(150,ACCESS_D/2,ACCESS_D/2,192).translate([0,0,SEAT])
 return main((s+xform(foot,frame(n)))-xform(bore+well,frame(n)))
def track_cutter(foot,n):
 p=rotational_profile(foot,n)
 return xform(p.offset(TRACK_CLEARANCE,join_type=mf.JoinType.Round,circular_segments=64).revolve(SEG),frame(n))
def round_inner(s,radius,axis=None):
 limit=mf.Manifold.sphere(INNER_LIMIT,SEG)
 inner=s^mf.Manifold.sphere(INNER_WORK,SEG);protected=inner-limit
 if axis is not None:protected+=inner^protected_axle(axis)
 kernel=mf.Manifold.sphere(radius,24)
 seed=inner.minkowski_difference(kernel)+protected
 return main(((seed.minkowski_sum(kernel)^inner)+(s-limit))^s)
def hex_section(af):
 return mf.CrossSection([[[af/np.sqrt(3)*np.cos(t),af/np.sqrt(3)*np.sin(t)] for t in np.arange(6)*np.pi/3]])
def nut_shape():
 return hex_section(5.5).extrude(4).translate([0,0,NUT_ROOF-4])-mf.Manifold.cylinder(40,1.5,1.5,72)
def nut_slot(af=5.60):
 section=hex_section(af)+mf.CrossSection.square([32,af],False).translate([0,-af/2])
 return section.extrude(4.25).translate([0,0,NUT_ROOF-4.25])
def nut_ribs(af=5.60):
 p=mf.CrossSection([[[0,af/2-.12],[.7,af/2-.12],[1.7,af/2+.15],[0,af/2+.15]]]).extrude(1.3).translate([0,0,NUT_ROOF-1.65])
 return p+xform(p,np.diag([1,-1,-1]),[0,0,2*NUT_ROOF-2.0])
def core(with_ribs=True,af=5.60):
 envelope=mf.Manifold.sphere(CORE_R,SEG)
 for n in AXES:envelope=envelope.trim_by_plane(-n,-CORE_PAD)
 cutters=[xform(nut_slot(af)+mf.Manifold.cylinder(50,1.7,1.7,96),frame(n)) for n in AXES]
 s=subtract(envelope,cutters)
 if with_ribs:
  for n in AXES:s+=xform(nut_ribs(af),frame(n))^envelope
 return main(s)
def hardware(n,play=0):
 z=SEAT+play
 screw=mf.Manifold.cylinder(20,1.5,1.5,96).translate([0,0,z+1-20])+mf.Manifold.cylinder(3,2.75,2.75,96).translate([0,0,z+1])
 washer=mf.Manifold.cylinder(1,4.5,4.5,144)-mf.Manifold.cylinder(1,1.6,1.6,96)
 return xform(screw,frame(n)),xform(washer,frame(n),n*z)
def coupon(af):
 block=mf.Manifold.cube([24,18,10],False).translate([-12,-9,CORE_PAD-10])
 return main((block-nut_slot(af)-mf.Manifold.cylinder(40,1.7,1.7,96))+(nut_ribs(af)^block))
def rotor_coupon():
 foot=mf.Manifold.cylinder(SEAT-FOOT_PLANE+4,FOOT_R,FOOT_R,144).translate([0,0,FOOT_PLANE])
 cup=mf.Manifold.cylinder(7,6,6,144).translate([0,0,SEAT-3])
 return (foot+cup)-mf.Manifold.cylinder(100,BORE_D/2,BORE_D/2,144)-mf.Manifold.cylinder(100,ACCESS_D/2,ACCESS_D/2,192).translate([0,0,SEAT])
def stand():
 foot=mf.Manifold.cylinder(STAND_SEAT-FOOT_PLANE,FOOT_R,FOOT_R,144).translate([0,0,FOOT_PLANE])
 tube=mf.Manifold.cylinder(90-STAND_SEAT,5.8,5.8,144).translate([0,0,STAND_SEAT-.2])
 base=mf.Manifold.cylinder(4,22,22,144).translate([0,0,86])
 s=foot+tube+base-mf.Manifold.cylinder(120,BORE_D/2,BORE_D/2,144)-mf.Manifold.cylinder(120,ACCESS_D/2,ACCESS_D/2,192).translate([0,0,STAND_SEAT])
 return xform(main(s),frame(AXES[0]))

def build_canonical():
 t=time.time();OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'raw/E12.npz').exists():cells={row['name']:load(OUT/'raw'/(row['name']+'.npz')) for row in ROWS}
 else:
  cells=raw_cells()
  for name,s in cells.items():save(s,OUT/'raw'/(name+'.npz'))
 print('raw',time.time()-t,flush=True)
 n=AXES[7];ball=mf.Manifold.sphere(INNER_LIMIT,SEG)
 if (OUT/'corner-relieved.npz').exists():corner=load(OUT/'corner-relieved.npz')
 else:
  feet=[cells[f'E{k+1:02}']^ball for k,pair in enumerate(EDGES) if 7 in pair]
  sweep=union([downward_sweep(e,n,.08).minkowski_sum(mf.Manifold.sphere(.03,12)) for e in feet])
  corner=main(cells['C08']-sweep)
  cutters=[]
  for k,pair in enumerate(EDGES):
   if 7 in pair:
    other=next(i for i in pair if i!=7)
    print('swept track',pair,flush=True);cutters.append(track_cutter(cells[f'E{k+1:02}']^ball,AXES[other]))
  removable=(union(cutters)^ball)-protected_axle(n)
  corner=finish_hardware(main(corner-removable),n)
  save(corner,OUT/'corner-relieved.npz')
 print('corner relief',time.time()-t,flush=True)
 if not (OUT/'canonical-C.npz').exists():
  save(round_inner(corner,CORNER_ROUND,n),OUT/'canonical-C.npz')
 print('corner rounded',time.time()-t,flush=True)
 if not (OUT/'edge-inner-rounded.npz').exists():save(round_inner(cells['E12'],EDGE_ROUND),OUT/'edge-inner-rounded.npz')
 print('edge inner rounded',time.time()-t,flush=True)
 if not (OUT/'canonical-E.npz').exists():
  import mechanism_v4p2 as ridge
  ridge.GAP=BODY_GAP;ridge.CUTTER_START=20*SCALE;ridge.CUTTER_END=SIDE*1.2;ridge.PLAIN_CONE_START=33.5*SCALE
  e=load(OUT/'edge-inner-rounded.npz')
  cutter,sections=ridge.ridge_cutter(e,ROUND_R)
  save(cutter,OUT/'ridge-cutter.npz')
  (OUT/'ridge-sections.json').write_text(json.dumps(sections,indent=2))
  save(main(e-cutter),OUT/'canonical-E.npz')
 print('complete canonical',time.time()-t,flush=True)

if __name__=='__main__':build_canonical()
