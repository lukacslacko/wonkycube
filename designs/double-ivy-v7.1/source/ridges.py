"""Exterior radial ridge directions for the two-cut tetrahedral cells."""
from design import *
def norm(v):return v/np.linalg.norm(v)

def ridges(row):
 sig=row['signature'];circles=[(i,d,AXES[i],np.cos(np.radians([BETA,ALPHA][d]))) for i in range(4) for d in range(2)]
 points=[]
 for (i,di,n,c),(j,dj,m,e) in itertools.combinations(circles,2):
  if i==j:continue
  dot=n@m;p=((c-dot*e)*n+(e-dot*c)*m)/(1-dot*dot)
  if p@p>1+1e-10:continue
  for sign in [-1,1]:
   q=p+sign*np.sqrt(max(0,1-p@p))*norm(np.cross(n,m))
   if any(np.linalg.norm(q-o)<1e-6 for o in points):continue
   if any((a@q-v)*(1 if sig[k]>=d+1 else -1)<-1e-7 for k,d,a,v in circles):continue
   points.append(q)
 out=[]
 for q in points:
  normals=[]
  for i,d,n,c in circles:
   if abs(n@q-c)<1e-7:normals.append(((i,d),norm(n-c*q)*(1 if sig[i]>=d+1 else -1)))
  choices=[]
  for (keya,a),(keyb,b) in itertools.combinations(normals,2):
   bis=norm(a+b);ta=norm(np.cross(q,a));ta*=1 if ta@b>=0 else -1
   tb=norm(np.cross(q,b));tb*=1 if tb@a>=0 else -1
   if all(v@ta>=-1e-7 and v@tb>=-1e-7 for key,v in normals):choices.append((a@b,keya,keyb,bis))
  if not choices:raise ValueError(('no wedge',row,q,normals))
  _,a,b,u=min(choices,key=lambda t:t[0]);out.append((a,b,np.array([u,np.cross(q,u),q])))
 return out

