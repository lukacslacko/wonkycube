"""Constant transverse circle fillets along each radial ridge, including tracks."""
from conical_design import *
from scipy.optimize import minimize_scalar
RADIUS=2.

def ridges(row):
 sig=set(row['signature']);out=[];c=np.cos(np.radians(ANGLE))
 for i,j in itertools.combinations(range(7),2):
  dot=float(AXES[i]@AXES[j])
  if dot < -0.999:continue
  base=c*(AXES[i]+AXES[j])/(1+dot)
  if base@base >= 1:continue
  k=np.cross(AXES[i],AXES[j]);k/=np.linalg.norm(k)
  for sign in [-1,1]:
   d=base+sign*np.sqrt(1-base@base)*k
   if not all((AXES[m]@d>c)==(m in sig) for m in range(7) if m not in (i,j)):continue
   a=(AXES[i]-c*d)*(1 if i in sig else -1)
   b=(AXES[j]-c*d)*(1 if j in sig else -1)
   inward=a/np.linalg.norm(a)+b/np.linalg.norm(b);inward/=np.linalg.norm(inward)
   side=np.cross(d,inward)
   out.append((i,j,np.array([inward,side,d])))
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
   # Cells have a separate outer return behind their inner foot.
   # Round the entry boundary, never the far return or core-side back wall.
   p=active[0];parts.append((lo,hi,p[2],p[3]))
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
 cz=0. if symmetric else float(fit.x);detail=evaluate(cz,True)
 if not isinstance(detail,tuple):return None
 cy,z,values=detail
 hit=z[values>cy-.0002];angles=np.arcsin(np.clip((hit-cz)/radius,-1,1))
 low=min(float(angles.min()),-.0005);high=max(float(angles.max()),.0005)
 return float(cy),cz,low,high

def cutter(s,F,radius=RADIUS,symmetric=False):
 local=xform(s,F);memo={}
 fit_start=INNER_R+.1
 xs=list(np.r_[np.arange(fit_start,32.,.4),np.arange(32.,64.,2.),64.])
 # A narrow cell can start beyond the first station, inside the hollow core.
 # Extend its first/last valid arc through empty space, so there is no abrupt
 # switch to a smaller radius where material starts or ends.
 valid={}
 for x in xs:
  p=fronts(local.slice(x).to_polygons())
  if len(p):
   value=circle(p,radius,symmetric)
   if value is not None:valid[x]=value
 if not valid:raise ValueError('Radial edge has no material in the sampled range')
 vx=np.array(sorted(valid));vv=np.array([valid[x] for x in vx])
 def sample(x):
  if x not in memo:
   if x in valid:memo[x]=valid[x]
   else:
    p=fronts(local.slice(x).to_polygons())
    value=circle(p,radius,symmetric) if len(p) else None
    memo[x]=value if value is not None else tuple(np.interp(x,vx,vv[:,j]) for j in range(4))
  return np.array(memo[x])
 for depth in range(7):
  extra=[]
  for a,b in zip(xs[:-1],xs[1:]):
   if b-a<.005:continue
   pa=sample(a);pb=sample(b);mid=(a+b)/2;pm=sample(mid)
   if np.max(np.abs(pm[:2]-(pa[:2]+pb[:2])/2))>.008 or np.max(np.abs(pm[2:]-(pa[2:]+pb[2:])/2))>.02 or np.max(np.abs(pa[2:]-pb[2:]))>.08:extra.append(mid)
  if not extra:break
  xs=sorted(xs+extra)
 # Fit outside the hollow core: an inner spherical return is not a radial
 # dihedral. Extend the first valid R2 arc inward through that empty region.
 # This preserves rounding all the way to the real edge's termination.
 memo[0.]=sample(xs[0]);xs=[0.]+xs
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
 result={};all_records={};folder=CACHE/f'ridges-{radius:g}';folder.mkdir(parents=True,exist_ok=True)
 for orbit in ORBITS:
  row=canonical(orbit);s=cells[row['name']];cutters=[];records=[]
  path=folder/(orbit+'.npz');recpath=folder/(orbit+'-sections.json')
  if path.exists() and recpath.exists():
   replicate(result,load(path),orbit);all_records[orbit]=json.loads(recpath.read_text());continue
  for i,j,F in ridges(row):
   t=time.time();tool,data=cutter(s,F,radius,orbit in ['Cp','K']);cutters.append(tool.as_original().simplify(.002))
   records.append(dict(axes=[i,j],frame=F.tolist(),sections=data))
   print('RIDGE',orbit,i,j,len(data),round(time.time()-t,2),flush=True)
  recpath.write_text(json.dumps(records,indent=2));all_records[orbit]=records
  if path.exists():rounded=load(path)
  else:
   pieces=sorted(subtract(s,cutters).decompose(),key=lambda a:a.volume(),reverse=True)
   scraps=[c for c in pieces[1:] if abs(c.volume())>1e-8]
   # Remove only the tiny disconnected tips left when radial fillets meet.
   # These cannot retain a part or transmit force: they are already detached.
   discarded=sum(abs(c.volume()) for c in scraps)
   if discarded>1.0 or any(abs(c.volume())>1.0 for c in scraps):
    raise ValueError(('unexpected disconnected material',orbit,[c.volume() for c in scraps]))
   (folder/(orbit+'-tip-trimming.json')).write_text(json.dumps(dict(orbit=orbit,total_volume_mm3=discarded,components=[dict(volume_mm3=c.volume(),bounds_mm=mesh(c).bounds.tolist()) for c in scraps]),indent=2))
   rounded=pieces[0].as_original().simplify(.001);save(rounded,path)
   print('ROUNDED',orbit,rounded.num_tri(),'trimmed',discarded,flush=True)
  replicate(result,rounded,orbit)
 (folder/'sections.json').write_text(json.dumps(all_records,indent=2))
 return result

if __name__=='__main__':
 t=time.time();cells=round_inner_cells(build_relief(raw_cells()));result=rounded_cells(cells)
 print('Canonical rounding complete',flush=True)
 for name,s in clip(result).items():save(s,CACHE/'ridge-trial'/(name+'.npz'))
 print('FINISH',time.time()-t,flush=True)
