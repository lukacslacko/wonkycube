"""Natural cuboctahedron, twelve 45 degree axes; dimensions in millimetres."""
from geometry import matrix,xform,frame,mesh,from_mesh,union,subtract,save,load,main,downward_sweep
from pathlib import Path
import os,json,itertools,time
import numpy as np
import manifold3d as mf
import trimesh
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
WORK=Path(os.environ.get('CUBOCTA_BUILD_DIR',HERE.parent));WORK.mkdir(parents=True,exist_ok=True);CACHE=WORK/'cache';CACHE.mkdir(exist_ok=True)
CONFIG=json.loads((HERE/'configuration.json').read_text());AXES=np.array(CONFIG['axes'])
SEG=int(os.environ.get('CUBOCTA_SEG','144'))
ORBITS=['C','P','K'];N_AXES=12;ANGLE=45.
SIZE=72.
RELEASE_VERSION='natural-cuboctahedron-45-spherical-v3.2'
SHOULDER_R=float(os.environ.get('SPHERICAL_SHOULDER_R','28.5'))
COLLAR_OUTER_R=float(os.environ.get('SPHERICAL_COLLAR_OUTER_R','33.5'))
NECK_ANGLE=float(os.environ.get('SPHERICAL_NECK_ANGLE','40'))
BODY_GAP=.08
TRACK_EXTRA=.25
PETAL_GROOVE_WIDTH_EXTRA=.20
PETAL_WALL_EXTRA=PETAL_GROOVE_WIDTH_EXTRA/2
CENTER_FLANGE_END_ROUNDING=1.2
CORE_R=21.2;INNER_R=21.7;CORE_PAD=19.6
FOOT_PLANE=19.7;FOOT_R=3.1;FOOT_TOP=23.2
SEAT=31.;NUT_ROOF=17.65
NUT_SEAT_AF=5.25;NUT_ENTRY_AF=5.85
GROUP=[]
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  q=np.eye(3)[list(perm)]*np.array(signs)[:,None]
  if np.linalg.det(q)>.5:GROUP.append(q)
ROWS=[];count={'C':0,'P':0,'K':0}
for j,p in enumerate(CONFIG['pieces']):
 sig=[i-1 for i in p['members']];family={1:'C',2:'P',3:'K'}[len(sig)];count[family]+=1
 d=AXES[sig].sum(axis=0);d/=np.linalg.norm(d)
 ROWS.append(dict(name=f'{family}{count[family]:02}',family=family,orbit=family,signature=sig,direction=d.tolist(),source_index=j))
def canonical(f):return next(r for r in ROWS if r['family']==f)
def mapped(sig,q):return tuple(sorted(int(np.argmin(np.linalg.norm(AXES-q@AXES[i],axis=1))) for i in sig))
def mapping(sig,target):return next(q for q in GROUP if mapped(sig,q)==tuple(target))
def replicate(s,f):return {r['name']:xform(s,mapping(canonical(f)['signature'],r['signature'])) for r in ROWS if r['family']==f}
def outer():
 s=mf.Manifold.cube([SIZE]*3,True)
 for n in itertools.product([-1,1],repeat=3):s=s.trim_by_plane(-np.array(n)/np.sqrt(3),-SIZE/np.sqrt(3))
 return s
def profile():
 # Constant-radius shoulders: revolving these arcs produces concentric
 # spherical surfaces. The retaining foot widens inward below the collar.
 # Every band remains a surface of revolution about each turn axis.
 def arc(radius,start,end):
  a=np.radians(np.linspace(start,end,max(3,int(abs(end-start)/.25)+1)))
  return np.column_stack([radius*np.sin(a),radius*np.cos(a)]).tolist()
 return [[0,0]]+arc(SHOULDER_R,45,NECK_ANGLE)+arc(COLLAR_OUTER_R,NECK_ANGLE,45)+[[110,110],[110,130],[0,130]]
def cut(offset=0,rounding=0,restore_outer=False):
 p=mf.CrossSection([profile()])
 if offset:p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=24)
 if rounding<0:p=p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=24).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=24)^p
 if rounding>0:p=p+p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=24).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=24)
 if offset>BODY_GAP/2+.001:
  scale=np.sqrt(2);start=COLLAR_OUTER_R/scale+.15;end=start+.55
  ramp=mf.CrossSection([[[start,-150],[150,-150],[150,150-BODY_GAP/2*scale],[end,end-BODY_GAP/2*scale],[start,start-offset*scale]]]);p=p-ramp
 if offset<0:p=p+mf.CrossSection.square([1,120],False).translate([0,1])
 if restore_outer:
  # Extra clearance is confined to the hidden track, blending back to the
  # original body gap beyond its upper spherical return.
  scale=np.sqrt(2);start=COLLAR_OUTER_R/scale+.15;end=start+.55
  filler=mf.CrossSection([[[start,start-offset*scale],[end,end+BODY_GAP/2*scale],[150,150+BODY_GAP/2*scale],[150,200],[start,200]]])
  p=p+filler
 return p.revolve(SEG)
def cuts(f):
 offset=-BODY_GAP/2-(PETAL_WALL_EXTRA if f=='P' else 0)
 ci=[xform(cut(offset,-.4,f=='P'),frame(n)) for n in AXES]
 co=[xform(cut(BODY_GAP/2+TRACK_EXTRA,.25),frame(n)) for n in AXES]
 return ci,co
def unclipped(f):
 # A reference for fitting fillets, not exported geometry. Remove the flat
 # exterior clipping planes so the fillet follows the cut right to the skin.
 ci,co=cuts(f);s=mf.Manifold.sphere(90,SEG)-mf.Manifold.sphere(INNER_R,SEG)
 row=canonical(f)
 for i in row['signature']:s=s^ci[i]
 return subtract(s,[co[i] for i in range(N_AXES) if i not in row['signature']])
def raw():
 shell=outer()-mf.Manifold.sphere(INNER_R,SEG)
 result={}
 for f in ['C','P','K']:
  ci,co=cuts(f)
  row=canonical(f);s=shell
  for i in row['signature']:s=s^ci[i]
  s=subtract(s,[co[i] for i in range(12) if i not in row['signature']])
  chunks=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True);print('COMPONENTS',f,[round(c.volume(),3) for c in chunks],flush=True)
  s=main(s,.2);save(s,CACHE/f'raw-{f}.npz');result.update(replicate(s,f))
 return result
def get(stage):
 result={}
 for f in ['C','P','K']:result.update(replicate(load(CACHE/f'{stage}-{f}.npz'),f))
 return result
def relief(cells):
 # Preserve the complete spherical shoulders. User explicitly preferred
 # hands-on insertion to trimming retaining geometry for straight assembly.
 # Keep the stage name for the shared finishing pipeline.
 for f in ORBITS:save(cells[canonical(f)['name']],CACHE/f'relieved-{f}.npz')
 return cells.copy()
def axle(s,n):
 foot=mf.Manifold.cylinder(FOOT_TOP-FOOT_PLANE,FOOT_R,FOOT_R,SEG).translate([0,0,FOOT_PLANE])
 holes=mf.Manifold.cylinder(90,1.8,1.8,SEG)+mf.Manifold.cylinder(90,4.8,4.8,SEG).translate([0,0,SEAT])
 return main((s+xform(foot,frame(n)))-xform(holes,frame(n)))
def motion(cells):
 seq=json.loads((HERE/'sequence.json').read_text());r=np.tile(np.eye(3),(44,1,1));items=[cells[x['name']] for x in ROWS];results=[]
 for step,m in enumerate(seq['sequence']):
  chosen=set(m['pieces']);moving=union([xform(items[i],r[i]) for i in chosen]);fixed=union([xform(items[i],r[i]) for i in range(44) if i not in chosen]);worst=[0,0]
  for angle in np.linspace(0,m['angle_degrees'],17):
   q=Rotation.from_rotvec(np.radians(angle)*AXES[m['axis']]).as_matrix();v=(xform(moving,q)^fixed).volume()
   if v>worst[1]:worst=[float(angle),v]
  q=Rotation.from_rotvec(np.radians(m['angle_degrees'])*AXES[m['axis']]).as_matrix();r[list(chosen)]=q@r[list(chosen)]
  print('MOTION',step,worst,flush=True);results.append(worst)
 return results
if __name__=='__main__':
 cells=raw();motion(cells);cells=relief(cells);motion(cells)
