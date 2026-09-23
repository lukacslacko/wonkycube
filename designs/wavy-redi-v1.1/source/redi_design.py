"""Wavy Redi: saved exterior, stepped inner retention and exposed fixed core."""
from mechanism import *
from scipy.interpolate import PchipInterpolator
import os, sys, time

HERE=Path(__file__).resolve().parent
WORK=Path(os.environ.get('WAVY_BUILD_DIR',HERE.parent))
OUT=WORK/'cache'
SPEC=json.loads((HERE/'selection.json').read_text())
R=np.array(SPEC['cube_to_mechanism_matrix'])
SIDE=64.; BODY_GAP=.08; TRACK_CLEARANCE=.40
CORE_R=19.2;CORE_PAD=17.6;INNER_R=19.7
FOOT_PLANE=17.7;FOOT_TOP=21.4;FOOT_R=3.2
SEAT=27.3;ACCESS_D=9.6;BORE_D=3.6;NUT_ROOF=15.65
INNER_LIMIT=28.4;INNER_WORK=29.6
ROUND_R=2.;EDGE_ROUND=.50;CORNER_ROUND=.40;OUTER_ROUND=.65
PRINT_FOOT_TRIM=.24
SEG=int(os.environ.get('WAVY_SEG','240'))
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
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);m=mesh(s);np.savez_compressed(path,v=m.vertices,f=m.faces)
def load(path):
 z=np.load(path);return from_mesh(trimesh.Trimesh(z['v'],z['f'],process=False))
def main(s,allowed=.001):
 pieces=sorted(s.decompose(),key=lambda x:x.volume(),reverse=True)
 if not pieces:raise ValueError('empty part')
 if sum(abs(p.volume()) for p in pieces[1:])>allowed:raise ValueError(('disconnected material',[p.volume() for p in pieces]))
 return pieces[0]

def selected_outer():
 pts=[]
 for a,b in zip(SPEC['profile']['nodes'][:-1],SPEC['profile']['nodes'][1:]):
  c=np.array([a['p'],a['out'],b['in'],b['p']]);t=np.linspace(0,1,20001)[:,None]
  pts.extend((1-t)**3*c[0]+3*(1-t)**2*t*c[1]+3*(1-t)*t*t*c[2]+t**3*c[3])
 p=np.array(pts);p=p[p[:,0]>19.539];rr=np.linalg.norm(p,axis=1)
 keep=np.r_[True,np.diff(rr)>1e-8];p=p[keep];rr=rr[keep]
 return PchipInterpolator(rr,np.arctan2(p[:,0],p[:,1]))
OUTER_THETA=selected_outer()

def outside_theta(r):
 r=np.asarray(r);original=OUTER_THETA(r)
 # User-approved local strengthening: soft cap at 51.6 degrees near r=32.
 # The selected curve is unchanged from r=36 onward. Maximum angular
 # change on the actual cube starts at r=32: 1.714 degrees, ~0.96 mm arc.
 a=np.degrees(original);cap=51.6;w=.7
 soft=np.where(a<=cap-w,a,np.where(a>=cap+w,cap,cap-(cap-a+w)**2/(4*w)))
 return np.where(r<36,np.radians(soft),original)

def profile():
 # A steep cylindrical shoulder opposes an individual petal's radial pull
 # while remaining open along its turn axis for grouped assembly. The
 # smaller rail diameter leaves six passages for the stationary core arms.
 points=[[0,0],[11.7,14.8],[17.3,14.8],[17.65,15.15],[17.65,18.4],[17.9,20.6],[18.4,21.2]]
 r0=np.hypot(18.4,21.2);th0=np.arctan2(18.4,21.2)
 fn=PchipInterpolator([r0,30,31.6,32],[th0,np.radians(46),float(outside_theta(32)),float(outside_theta(32))])
 rs=np.r_[np.linspace(r0,32,120)[1:],np.linspace(32,56,360)[1:]]
 th=np.where(rs<32,fn(np.minimum(rs,32)),outside_theta(np.maximum(rs,32)))
 points.extend(np.column_stack((rs*np.sin(th),rs*np.cos(th))).tolist())
 # Last radius exceeds every solved/scrambled cube vertex radius.
 points.extend([[110,100],[0,100]])
 return points

def cut(offset=0):
 p=mf.CrossSection([profile()])
 if offset:p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=48)
 return p.simplify(.002).revolve(SEG)

def raw_cells():
 ball=mf.Manifold.sphere(55.6,SEG)
 shell=ball-mf.Manifold.sphere(INNER_R,SEG)
 ci=[xform(cut(-BODY_GAP/2),frame(n)) for n in AXES]
 co=[xform(cut(BODY_GAP/2),frame(n)) for n in AXES]
 cells={}
 for ref in [ROWS[7],ROWS[-1]]:
  sig=ref['signature'];s=shell
  for a in sig:s=s^ci[a]
  s=subtract(s,[co[a] for a in range(8) if a not in sig])
  pieces=sorted(s.decompose(),key=lambda p:p.volume(),reverse=True)
  print('raw',ref['name'],[(p.volume(),np.linalg.norm(mesh(p).vertices,axis=1).max()) for p in pieces],flush=True)
  for p in pieces[1:]:assert np.linalg.norm(mesh(p).vertices,axis=1).max()<26.5
  s=pieces[0]
  for row in ROWS:
   if row['name'][0]==ref['name'][0]:cells[row['name']]=xform(s,mapping(sig,row['signature']))
 return cells

def protected_axle(n):
 stem=mf.Manifold.cylinder(100,FOOT_R+.05,FOOT_R+.05,96).translate([0,0,CORE_PAD-1])
 cup=mf.Manifold.cylinder(100,6,6,96).translate([0,0,SEAT-1.5])
 return xform(stem+cup,frame(n))
def finish_hardware(s,n):
 foot=mf.Manifold.cylinder(FOOT_TOP-FOOT_PLANE,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 bore=mf.Manifold.cylinder(100,BORE_D/2,BORE_D/2,96)
 well=mf.Manifold.cylinder(100,ACCESS_D/2,ACCESS_D/2,128).translate([0,0,SEAT])
 return main((s+xform(foot,frame(n)))-xform(bore+well,frame(n)))
def round_inner(s,radius,axis=None):
 limit=mf.Manifold.sphere(INNER_LIMIT,128);inner=s^mf.Manifold.sphere(INNER_WORK,128);protected=inner-limit
 if axis is not None:protected+=inner^protected_axle(axis)
 kernel=mf.Manifold.sphere(radius,16)
 # Bounded approximation only for the rounding tool. Intersecting with the
 # original solid keeps all finished geometry subtractive.
 seed=inner.as_original().simplify(.005).minkowski_difference(kernel)+protected
 return main(((seed.minkowski_sum(kernel)^inner)+(s-limit))^s)
def hex_section(af):
 return mf.CrossSection([[[af/np.sqrt(3)*np.cos(t),af/np.sqrt(3)*np.sin(t)] for t in np.arange(6)*np.pi/3]])
def nut_slot(af=5.25):
 half=af/2;entry=5.85/2
 channel=mf.CrossSection([[[0,-half],[3,-half],[6,-entry],[35,-entry],[35,entry],[6,entry],[3,half],[0,half]]])
 return (hex_section(af)+channel).extrude(4.25).translate([0,0,NUT_ROOF-4.25])
def nut_shape():
 return hex_section(5.5).extrude(4).translate([0,0,NUT_ROOF-4])-mf.Manifold.cylinder(40,1.5,1.5,72)
def hub():
 s=mf.Manifold.sphere(CORE_R,SEG)
 for n in AXES:s=s.trim_by_plane(-n,-CORE_PAD)
 return s
def core():
 cube=xform(mf.Manifold.cube([SIDE]*3,True),R)
 fixed=subtract(cube,[xform(cut(BODY_GAP/2),frame(n)) for n in AXES])
 s=fixed+hub()
 cutters=[xform(nut_slot()+mf.Manifold.cylinder(80,1.7,1.7,96).translate([0,0,-40]),frame(n)) for n in AXES]
 s=subtract(s,cutters)
 # Recessed dots identify the eight bearing pads for assembly. They sit
 # outside the rotating foot and leave at least 1.60 mm above the nut roof.
 marks=[]
 for i,n in enumerate(AXES):
  for j in range(i+1):
   a=2*np.pi*j/8
   dot=mf.Manifold.cylinder(.36,.45,.45,32).translate([5.25*np.cos(a),5.25*np.sin(a),CORE_PAD-.35])
   marks.append(xform(dot,frame(n)))
 return main(subtract(s,marks))
def hardware(n,play=0):
 z=SEAT+play
 screw=mf.Manifold.cylinder(20,1.5,1.5,96).translate([0,0,z+1-20])+mf.Manifold.cylinder(3,2.75,2.75,96).translate([0,0,z+1])
 washer=mf.Manifold.cylinder(1,4.5,4.5,128)-mf.Manifold.cylinder(1,1.6,1.6,96)
 return xform(screw,frame(n)),xform(washer,frame(n),n*z)

def build():
 OUT.mkdir(parents=True,exist_ok=True);t=time.time()
 if (OUT/'raw/E12.npz').exists():cells={r['name']:load(OUT/'raw'/(r['name']+'.npz')) for r in ROWS}
 else:
  cells=raw_cells()
  for name,s in cells.items():save(s,OUT/'raw'/(name+'.npz'))
 if not (OUT/'core.npz').exists():save(core(),OUT/'core.npz')
 print('raw+core',time.time()-t,flush=True)
 n=AXES[7];ball=mf.Manifold.sphere(INNER_LIMIT,SEG)
 if not (OUT/'corner-relieved.npz').exists():
  corner=cells['C08'];cutters=[]
  for other in range(7):
   if np.isclose(AXES[other]@n,1/3):cutters.append(xform(cut(BODY_GAP/2+TRACK_CLEARANCE),frame(AXES[other])))
  corner=finish_hardware(main(corner-((union(cutters)^ball)-protected_axle(n))),n)
  save(corner,OUT/'corner-relieved.npz')
 print('relieved',time.time()-t,flush=True)
 if not (OUT/'canonical-C.npz').exists():save(round_inner(load(OUT/'corner-relieved.npz'),CORNER_ROUND,n),OUT/'canonical-C.npz')
 print('C rounded',time.time()-t,flush=True)
 if not (OUT/'edge-inner-rounded.npz').exists():save(round_inner(cells['E12'],EDGE_ROUND),OUT/'edge-inner-rounded.npz')
 print('E rounded',time.time()-t,flush=True)

if __name__=='__main__':build()
