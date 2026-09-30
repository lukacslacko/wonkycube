"""Double-cut Ivy: four radially ordered piece layers, original nut core."""
from geometry import *
import os,json,itertools,time
from scipy.spatial.transform import Rotation
HERE=Path(__file__).resolve().parent
WORK=Path(os.environ.get('IVY_BUILD_DIR',HERE.parent/'build'));CACHE=WORK/'cache';CACHE.mkdir(parents=True,exist_ok=True)
DEST=Path(os.environ.get('IVY_RELEASE',WORK/'release'))
SEG=int(os.environ.get('IVY_SEG','144'));SIZE=float(os.environ.get('IVY_SIDE','72'))
ALPHA=44.;BETA=float(np.degrees(np.arccos((-np.cos(np.radians(ALPHA))+np.sqrt(2)*np.sin(np.radians(ALPHA)))/3)))
ANGLES=[BETA,ALPHA]
# F foot -> E shoulder -> W shoulder -> C shoulder, outward in that order.
# The common deep profile carries low and high tracks so every turn remains
# an axisymmetric boundary. Unused shoulders are removed family by family.
BANDS=[(22.4,25.3,78.),(25.55,28.45,float(os.environ.get('W_BAND_NECK','49'))),(28.8,float(os.environ.get('C_BAND_END','31.2')),float(os.environ.get('C_BAND_NECK','81')))]
BASE_RADII={'F':19.5,'E':22.6,'W':25.6,'C':29.0}
FOOT_LIMITS={'F':22.4,'E':25.55,'W':28.8}
BODY_GAP=.05;TRACK_GAP=float(os.environ.get('IVY_TRACK_GAP','.30'));INNER_R=19.5
CORE_R=19.2;CORE_PAD=17.6;FOOT_PLANE=17.7;FOOT_R=3.1;FOOT_TOP=21.2;SEAT=27.3
R=np.array(json.loads((HERE/'chosen_rotation.json').read_text())['cube_to_mechanism_matrix'])
AXES=np.array([[-1,-1,1],[-1,1,-1],[1,-1,-1],[1,1,1]],float)/np.sqrt(3)
GROUP=[]
for perm in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  q=np.eye(3)[list(perm)]*np.array(signs)[:,None]
  if np.linalg.det(q)>.5 and all(np.min(np.linalg.norm(AXES-n@q.T,axis=1))<1e-6 for n in AXES):GROUP.append(q)
ROWS=[]
for family,keys in [('C',[tuple(2 if j==i else 0 for j in range(4)) for i in range(4)]),('W',[tuple(2 if k==i else 1 if k==j else 0 for k in range(4)) for i in range(4) for j in range(4) if i!=j]),('E',[tuple(int(i in p) for i in range(4)) for p in itertools.combinations(range(4),2)]),('F',[tuple(int(j!=i) for j in range(4)) for i in range(4)])]:
 for k,sig in enumerate(keys):
  n=np.array(sig)@AXES;n/=np.linalg.norm(n)
  ROWS.append(dict(name=f'{family}{k+1:02}',family=family,signature=list(sig),direction=n.tolist()))
def canonical(f):return next(r for r in ROWS if r['family']==f)
def mapped(sig,q):
 out=[0]*4
 for i,v in enumerate(sig):out[int(np.argmin(np.linalg.norm(AXES-q@AXES[i],axis=1)))]=v
 return tuple(out)
def mapping(sig,target):return next(q for q in GROUP if mapped(sig,q)==tuple(target))
def expand(canonical_parts):return {r['name']:xform(canonical_parts[r['family']],mapping(canonical(r['family'])['signature'],r['signature'])) for r in ROWS}
def outer():return xform(mf.Manifold.cube([SIZE]*3,True),R)
def profile(depth,neutral_high=False):
 angle=ANGLES[depth];bands=[BANDS[0],BANDS[2]] if depth==0 else [BANDS[1]]
 if neutral_high and depth==0:bands=[BANDS[0]]
 def arc(r,a,b):
  v=np.radians(np.linspace(a,b,max(3,int(abs(a-b)/.25)+1)));return np.column_stack([r*np.sin(v),r*np.cos(v)]).tolist()
 p=[[0,0]]
 for r0,r1,neck in bands:p+=arc(r0,angle,neck)+arc(r1,neck,angle)
 a=np.radians(angle)
 return p+[[120*np.sin(a),120*np.cos(a)],[0,150]]
def cut(depth,offset=0,rounding=0,neutral_high=False):
 p=mf.CrossSection([profile(depth,neutral_high)])
 if offset:p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=24)
 if rounding<0:p=p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=24).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=24)^p
 if rounding>0:p=p+p.offset(rounding,join_type=mf.JoinType.Round,circular_segments=24).offset(-rounding,join_type=mf.JoinType.Round,circular_segments=24)
 if offset>BODY_GAP/2+.001:
  a=np.radians(ANGLES[depth]);t=np.array([np.sin(a),np.cos(a)]);n=np.array([-np.cos(a),np.sin(a)])
  start=(BANDS[2][1] if depth==0 else BANDS[1][1])+.10;end=start+.70
  uv=np.array([[start,-180],[150,-180],[150,-BODY_GAP/2],[end,-BODY_GAP/2],[start,-offset]])
  ramp=mf.CrossSection([uv[:,0,None]*t+uv[:,1,None]*n]);p=p-ramp
 if offset<0:p=p+mf.CrossSection.square([.8,140],False).translate([0,1])
 return p.revolve(SEG)
def raw():
 shell=mf.Manifold.sphere(85,SEG)
 ci=[[xform(cut(d,-BODY_GAP/2,-.35),frame(n)) for n in AXES] for d in range(2)]
 co=[[xform(cut(d,TRACK_GAP-BODY_GAP/2,.25),frame(n)) for n in AXES] for d in range(2)]
 cn=[xform(cut(0,TRACK_GAP-BODY_GAP/2,.25,True),frame(n)) for n in AXES]
 cells={};report=[]
 for family in 'CWEF':
  row=canonical(family);s=shell-mf.Manifold.sphere(BASE_RADII[family],SEG)
  for i,v in enumerate(row['signature']):
   s=s-(cn[i] if family=='E' else co[0][i]) if v==0 else s^ci[0][i]
   s=s^ci[1][i] if v==2 else s-co[1][i]
  cs=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True);print('RAW',family,[c.volume() for c in cs],flush=True)
  assert sum(abs(c.volume()) for c in cs[1:])<.1
  s=cs[0];save(s,CACHE/f'raw-{family}.npz');cells[family]=s
 return expand(cells)
def axle(s,n):
 foot=mf.Manifold.cylinder(FOOT_TOP-FOOT_PLANE,FOOT_R,FOOT_R,SEG).translate([0,0,FOOT_PLANE])
 # Keep the original core bearing and washer seat while reaching the higher
 # C flange with a thick stem (1.6 mm wall around the 9.6 mm access well).
 foot=foot+mf.Manifold.cylinder(2.2,3.1,6.4,SEG).translate([0,0,20.0])+mf.Manifold.cylinder(11.,6.4,6.4,SEG).translate([0,0,22.0])
 holes=mf.Manifold.cylinder(90,1.8,1.8,SEG)+mf.Manifold.cylinder(90,4.8,4.8,SEG).translate([0,0,SEAT])
 return main((s+xform(foot,frame(n)))-xform(holes,frame(n)))
def clipped(cells):
 out={}
 for row in ROWS:
  s=main(cells[row['name']]^outer(),.01)
  if row['family']=='C':s=axle(s,np.array(row['direction']))
  out[row['name']]=s
 return out
if __name__=='__main__':
 cells=clipped(raw())
 for name,s in cells.items():save(s,CACHE/'trial'/(name+'.npz'))
 print('DONE',SIZE,BANDS,flush=True)
