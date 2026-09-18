"""Constant transverse circle fillets along each radial ridge, including tracks."""
from skewb_design import *
from scipy.optimize import minimize_scalar
RADIUS=3.

def ridges(row):
 sig=set(row['signature']);out=[]
 for i,j in itertools.combinations(range(4),2):
  d=np.cross(AXES[i],AXES[j]);d/=np.linalg.norm(d)
  remaining=[k for k in range(4) if k not in (i,j)]
  for sign in [-1,1]:
   v=sign*d
   if all((AXES[k]@v>0)==(k in sig) for k in remaining):
    a=AXES[i]*(1 if i in sig else -1);b=AXES[j]*(1 if j in sig else -1)
    inward=a+b;inward/=np.linalg.norm(inward)
    side=np.cross(v,inward)
    out.append((i,j,np.array([inward,side,v])))
 return out

def fronts(polygons,band=17):
 segments=[];breaks=[-band,band]
 for p in polygons:
  for a,b in zip(p,np.roll(p,-1,axis=0)):
   dz=b[1]-a[1]
   if abs(dz)<1e-9:continue
   lo=max(-band,min(a[1],b[1]));hi=min(band,max(a[1],b[1]))
   if hi-lo<1e-8:continue
   m=(b[0]-a[0])/dz;v=a[0]-m*a[1];segments.append((lo,hi,m,v));breaks.extend([lo,hi])
 parts=[]
 for lo,hi in zip(np.unique(breaks)[:-1],np.unique(breaks)[1:]):
  mid=(lo+hi)/2;active=sorted([p for p in segments if p[0]-1e-9<=mid<=p[1]+1e-9],key=lambda p:p[2]*mid+p[3])
  if len(active)>=2:
   # Use the main body's last solid interval, as in the tested Redi fillet.
   p=active[-2];parts.append((lo,hi,p[2],p[3]))
 return np.array(parts)

def circle(p,radius=RADIUS,symmetric=False):
 if not len(p):raise ValueError('No section material')
 def evaluate(cz,details=False):
  lo=np.maximum(p[:,0],cz-radius);hi=np.minimum(p[:,1],cz+radius);use=hi>lo+1e-9
  m=p[use,2];b=p[use,3]
  z=np.clip(cz+radius*m/np.sqrt(1+m*m),lo[use],hi[use])
  val=m*z+b+np.sqrt(np.maximum(0,radius*radius-(z-cz)**2))
  if not len(val):return 1e5
  cy=val.max()
  return (cy,z,val) if details else cy
 grid=np.linspace(-12,12,49);scores=np.array([evaluate(z)+.000001*z*z for z in grid]);i=int(np.argmin(scores))
 fit=minimize_scalar(lambda z:evaluate(z)+.000001*z*z,bounds=(grid[max(i-1,0)],grid[min(i+1,48)]),method='bounded',options={'xatol':1e-7})
 cz=0. if symmetric else float(fit.x);cy,z,values=evaluate(cz,True)
 hit=z[values>cy-.0002];angles=np.arcsin(np.clip((hit-cz)/radius,-1,1))
 low=min(float(angles.min()),-.0005);high=max(float(angles.max()),.0005)
 return float(cy),cz,low,high

def cutter(s,F,radius=RADIUS,symmetric=False):
 local=xform(s,F);memo={}
 def sample(x):
  if x not in memo:memo[x]=circle(fronts(local.slice(x).to_polygons()),radius,symmetric)
  return np.array(memo[x])
 xs=list(np.r_[np.arange(17.,32.,.4),np.arange(32.,64.,2.),64.])
 for depth in range(7):
  extra=[]
  for a,b in zip(xs[:-1],xs[1:]):
   if b-a<.005:continue
   pa=sample(a);pb=sample(b);mid=(a+b)/2;pm=sample(mid)
   if np.max(np.abs(pm[:2]-(pa[:2]+pb[:2])/2))>.008 or np.max(np.abs(pm[2:]-(pa[2:]+pb[2:])/2))>.02 or np.max(np.abs(pa[2:]-pb[2:]))>.08:extra.append(mid)
  if not extra:break
  xs=sorted(xs+extra)
 rings=[];records=[]
 for x in xs:
  cy,cz,lo,hi=sample(x);angles=np.linspace(lo,hi,49)
  arc=np.column_stack((cy-radius*np.cos(angles)-.005,cz+radius*np.sin(angles)))
  yz=np.vstack([[-100,cz],[-100,arc[0,1]],arc,[-100,arc[-1,1]]])
  rings.append(np.column_stack((yz,np.full(len(yz),x))))
  records.append(dict(station_mm=float(x),center=[cy-.005,cz],radius_mm=radius,angles=[lo,hi]))
 n=len(rings[0]);faces=[]
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;faces.extend([[a,b,a+n],[b,b+n,a+n]])
 for j in range(1,n-1):
  faces.append([0,j+1,j]);a=(len(rings)-1)*n;faces.append([a,a+j,a+j+1])
 m=trimesh.Trimesh(np.vstack(rings),np.array(faces),process=True)
 if m.volume<0:m.invert()
 assert m.is_watertight and m.is_winding_consistent
 solid=from_mesh(m)
 assert solid.status()==mf.Error.NoError
 return xform(solid,F.T),records

def rounded_cells(cells,radius=RADIUS):
 result={};all_records={}
 for family in ['C','F','K']:
  row=next(r for r in ROWS if r['family']==family);s=cells[row['name']];cutters=[];records=[]
  for i,j,F in ridges(row):
   t=time.time();tool,data=cutter(s,F,radius,family in ['C','K']);cutters.append(tool)
   records.append(dict(axes=[i,j],frame=F.tolist(),sections=data))
   print('RIDGE',family,i,j,len(data),round(time.time()-t,2),flush=True)
  rounded=main(subtract(s,cutters));save(rounded,CACHE/f'ridges-{radius:g}'/(family+'.npz'))
  for r in (r for r in ROWS if r['family']==family):result[r['name']]=xform(rounded,mapping(row['signature'],r['signature']))
  all_records[family]=records
 (CACHE/f'ridges-{radius:g}'/'sections.json').write_text(json.dumps(all_records,indent=2))
 return result

if __name__=='__main__':
 t=time.time();cells=build_relief(raw_cells());result=rounded_cells(cells)
 print('RETENTION',radial_tests(result),flush=True);print('INSERT',insertion_tests(result),flush=True)
 for name,s in clip(result).items():save(s,CACHE/'ridge-trial'/(name+'.npz'))
 print('FINISH',time.time()-t,flush=True)
