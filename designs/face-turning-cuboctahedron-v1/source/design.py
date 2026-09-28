"""Single-cut face-turning cuboctahedron: eight triangle and six square axes."""
from geometry import *
import os,json,itertools,time
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
WORK=Path(os.environ.get('FC_BUILD_DIR',HERE.parent/'build'));WORK.mkdir(parents=True,exist_ok=True)
CACHE=WORK/'cache';CACHE.mkdir(exist_ok=True)
DEST=Path(os.environ.get('FC_RELEASE',WORK/'release'))
SEG=int(os.environ.get('FC_SEG','192'))
AXES=np.vstack([np.array(list(itertools.product([-1.,1.],repeat=3)))/np.sqrt(3),[np.eye(3)[k]*s for k in range(3) for s in [-1,1]]])
ANGLES=np.r_[np.full(8,np.degrees(np.arccos(np.sqrt(2/3)))),np.full(6,45.)]
COS=np.cos(np.radians(ANGLES));N_AXES=14;ORBITS=['T','S','P']
BODY_GAP=.06;TRACK_EXTRA=.40
CORE_R=21.2;INNER_R=21.7;CORE_PAD=19.6;FOOT_PLANE=19.7;FOOT_R=3.1;FOOT_TOP=23.2
SEATS={'T':32.,'S':27.3};NUT_ROOF=17.65
NUT_SEAT_AF=5.25;NUT_ENTRY_AF=5.85
WASHER_R=3.5;WASHER_H=.5;WELL_R=3.8
GROUP=[]
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  q=np.eye(3)[list(perm)]*np.array(signs)[:,None]
  if np.linalg.det(q)>.5:GROUP.append(q)
ROWS=[]
for i,a in enumerate(AXES):
 f='T' if i<8 else 'S';ROWS.append(dict(name=f'{f}{i+1 if i<8 else i-7:02}',family=f,signature=[i],direction=a.tolist()))
for i,j in itertools.product(range(8),range(8,14)):
 if AXES[i]@AXES[j]<.5:continue
 n=AXES[i]+AXES[j];n/=np.linalg.norm(n)
 ROWS.append(dict(name=f'P{sum(r["family"]=="P" for r in ROWS)+1:02}',family='P',signature=[i,j],direction=n.tolist()))
assert len(ROWS)==38
def canonical(f):return next(r for r in ROWS if r['family']==f)
def mapped(sig,q):return tuple(sorted(int(np.argmin(np.linalg.norm(AXES-q@AXES[i],axis=1))) for i in sig))
def mapping(sig,target):return next(q for q in GROUP if mapped(sig,q)==tuple(target))
def replicate(s,f):return {r['name']:xform(s,mapping(canonical(f)['signature'],r['signature'])) for r in ROWS if r['family']==f}
def outer():
 s=mf.Manifold.cube([64]*3,True)
 for n in itertools.product([-1,1],repeat=3):s=s.trim_by_plane(-np.array(n)/np.sqrt(3),-64/np.sqrt(3))
 return s
def profile(f):
 if f=='T':
  k=np.tan(np.radians(28));ke=1/np.sqrt(2)
  return [[0,0],[21*k,21],[17.,21],[17.,23.6],[11.1,23.6],[25.2*ke,25.2],[100*ke,100],[0,100]]
 k=np.tan(np.radians(38))
 return [[0,0],[18.2*k,18.2],[21.,18.2],[21.,20.8],[14.8,20.8],[22.,22.],[100,100],[0,100]]
def cut(f,offset=0,rounding=0):
 p=mf.CrossSection([profile(f)])
 if offset:p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=24)
 if rounding<0:p=p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=24).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=24)^p
 if rounding>0:p=p+p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=24).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=24)
 # Extra track clearance fades out before the exterior. Keep close main faces.
 if offset>BODY_GAP/2+.001:
  angle=np.radians(ANGLES[0] if f=='T' else 45);slope=1/np.tan(angle);scale=1/np.sin(angle)
  start,end=(17.4,18.2) if f=='T' else (21.2,22.3)
  ramp=mf.CrossSection([[[start,-150],[150,-150],[150,150*slope-BODY_GAP/2*scale],[end,end*slope-BODY_GAP/2*scale],[start,start*slope-offset*scale]]]);p=p-ramp
 if offset<0:p=p+mf.CrossSection.square([1,100],False).translate([0,1])
 return p.revolve(SEG)
def raw():
 shell=outer()-mf.Manifold.sphere(INNER_R,SEG)
 shapes={f:(cut(f,-BODY_GAP/2,-.35),cut(f,BODY_GAP/2+TRACK_EXTRA,.25)) for f in ['T','S']}
 ci=[xform(shapes['T' if i<8 else 'S'][0],frame(n)) for i,n in enumerate(AXES)]
 co=[xform(shapes['T' if i<8 else 'S'][1],frame(n)) for i,n in enumerate(AXES)]
 result={}
 for f in ORBITS:
  row=canonical(f);s=shell
  for i in row['signature']:s=s^ci[i]
  s=subtract(s,[co[i] for i in range(N_AXES) if i not in row['signature']])
  if f=='P':
   # The bearing feet are added after track relief. Preserve their straight
   # insertion corridor in the petals before any rounding is applied.
   corridor=mf.Manifold.cylinder(70,FOOT_R+.10,FOOT_R+.10,SEG).translate([0,0,FOOT_PLANE-.1])
   s=subtract(s,[xform(corridor,frame(n)) for n in AXES])
  print('RAW',f,[round(c.volume(),3) for c in s.decompose()],flush=True)
  s=main(s,.1);save(s,CACHE/f'raw-{f}.npz');result.update(replicate(s,f))
 return result
def get(stage):
 result={}
 for f in ORBITS:result.update(replicate(load(CACHE/f'{stage}-{f}.npz'),f))
 return result
def relief(cells):
 result=cells.copy();save(cells[canonical('P')['name']],CACHE/'relieved-P.npz')
 for f in ['T','S']:
  row=canonical(f);n=np.array(row['direction']);s=cells[row['name']];F=frame(n);bounds=mesh(xform(s,F.T)).bounds
  lo=bounds[0]-.1;hi=bounds[1]+[.1,.1,60]
  column=xform(mf.Manifold.cube(hi-lo,False).translate(lo),F)
  feet=union([v^column for k,v in cells.items() if k[0]=='P'])
  result_s=main(s-downward_sweep(feet,n,.06),.1)
  print('RELIEF',f,s.volume()-result_s.volume(),flush=True)
  save(result_s,CACHE/f'relieved-{f}.npz');result.update(replicate(result_s,f))
 return result
def axle(s,n,f):
 top=SEATS[f] if f=='T' else FOOT_TOP
 foot=mf.Manifold.cylinder(top-FOOT_PLANE,FOOT_R,FOOT_R,SEG).translate([0,0,FOOT_PLANE])
 holes=mf.Manifold.cylinder(90,1.8,1.8,SEG)+mf.Manifold.cylinder(90,WELL_R,WELL_R,SEG).translate([0,0,SEATS[f]])
 return main((s+xform(foot,frame(n)))-xform(holes,frame(n)))
def stem_sweep():
 # A capsule encloses the complete triangular-center stem. Its rotational
 # envelope about a neighboring square axis gives continuous clearance,
 # including intermediate turn angles, rather than isolated notch positions.
 u=np.array([np.sqrt(2/3),1/np.sqrt(3)])
 a=u*FOOT_PLANE;b=u*SEATS['T'];r=FOOT_R+TRACK_EXTRA
 v=np.array([-u[1],u[0]])*r
 p=mf.CrossSection([[a-v,b-v,b+v,a+v]])
 p=p+mf.CrossSection.circle(r,96).translate(a)+mf.CrossSection.circle(r,96).translate(b)
 return xform(p.revolve(SEG),frame(AXES[canonical('P')['signature'][1]]))
if __name__=='__main__':relief(raw())
