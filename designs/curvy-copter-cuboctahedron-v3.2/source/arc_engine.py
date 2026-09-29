# Boundary-extrema engine from lukacslacko/axes, scripts/piece_orbits.py.
import base64,gzip,json,math,itertools
from pathlib import Path
import numpy as np

TAU=2*np.pi
def rot(u,a):
 u=np.asarray(u);x,y,z=u
 K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
 return np.eye(3)*math.cos(a)+(1-math.cos(a))*np.outer(u,u)+math.sin(a)*K

class Puzzle:
 def __init__(self,f,v,atlas):
  self.f=f;self.v=v;self.U=np.array(f['axes']);self.alpha=math.radians(v['angle']);self.h=math.cos(self.alpha)
  self.W=v.get('width',atlas['width']);self.H=v.get('height',atlas['height']);self.labels=np.frombuffer(gzip.decompress(base64.b64decode(v['data'])),np.uint8 if v.get('labelBytes',1)==1 else '<u2').reshape(self.H,self.W)
  self.N=v['count'];self.seeds=np.array([p['seed'] for p in v['pieces']]);self.masks=[-1]+[p['mask'] for p in v['pieces']]
  self.axes=list(self.U)
  if v['angle']==90:
   for u in self.U:
    if not any(np.linalg.norm(-u-x)<1e-7 for x in self.axes):self.axes.append(-u)
  self.axes=np.array(self.axes);self.arcs=None;self.extent_cache={};self.arc_arrays={}
 def locate(self,p):
  p=p/np.linalg.norm(p);m=sum((1<<i) for i,d in enumerate(self.U@p) if d>self.h+1e-11)
  x=int((math.atan2(p[1],p[0])/TAU+.5)*self.W)%self.W;y=min(self.H-1,int(math.acos(np.clip(p[2],-1,1))/np.pi*self.H))
  id=int(self.labels[y,x])
  if id and self.masks[id]==m:return id-1
  for r in [1,2,4,8]:
   for dy in range(-r,r+1):
    for dx in range(-r,r+1):
     j=int(self.labels[max(0,min(self.H-1,y+dy)),(x+dx)%self.W])
     if j and self.masks[j]==m:return j-1
  candidates=[i for i,mask in enumerate(self.masks[1:]) if mask==m]
  if len(candidates)==1:return candidates[0]
  # A narrow positive-area tip may have no texel within this neighborhood.
  # Certify its component by an uncut great-circle path to a known seed.
  for j in sorted(candidates,key=lambda j:-p@self.seeds[j]):
   s=self.seeds[j]/np.linalg.norm(self.seeds[j]);c=np.clip(p@s,-1,1);theta=math.acos(c)
   if theta<1e-9:return j
   if abs(math.sin(theta))<1e-9:continue
   tangent=(s-c*p)/math.sin(theta);aa=self.U@p;bb=self.U@tangent;end=self.U@s
   lo=np.minimum(aa,end);hi=np.maximum(aa,end)
   phase=np.arctan2(bb,aa)%(2*np.pi);magnitude=np.hypot(aa,bb)
   hi=np.where(phase<=theta+1e-10,np.maximum(hi,magnitude),hi)
   phase=(phase+np.pi)%(2*np.pi)
   lo=np.where(phase<=theta+1e-10,np.minimum(lo,-magnitude),lo)
   if all(lo[i]>=self.h-2e-8 if m&(1<<i) else hi[i]<=self.h+2e-8 for i in range(len(self.U))):return j
  return -1
 def standard_moves(self):
  moves=[]
  if self.v['angle']==0:return moves
  for i,u in enumerate(self.axes):
   neighbors=np.array([v for v in self.axes if np.linalg.norm(v-u)>1e-7 and np.linalg.norm(v+u)>1e-7 and u@v>math.cos(2*self.alpha)+1e-8])
   if not len(neighbors):continue
   possible=[];seen=set()
   for a in neighbors:
    for b in neighbors:
     if abs(a@u-b@u)>1e-7:continue
     aa=a-(a@u)*u;bb=b-(b@u)*u
     phi=math.atan2(u@np.cross(aa,bb),aa@bb)%TAU
     if phi<1e-7 or phi>TAU-1e-7:continue
     key=round(phi,7)
     if key in seen:continue
     seen.add(key)
     R=rot(u,phi)
     if np.all(np.min(np.linalg.norm((neighbors@R.T)[:,None,:]-neighbors[None,:,:],axis=2),axis=1)<2e-6):possible.append(phi)
   if not possible:continue
   phi=min(possible);R=rot(u,phi);perm=[]
   for j,p in enumerate(self.v['pieces']):
    perm.append(self.locate(R@self.seeds[j]) if i+1 in p['members'] else j)
   assert sorted(perm)==list(range(self.N)),(self.f['key'],self.v['angle'],i,perm)
   moves.append(dict(axis=i+1,angle=round(math.degrees(phi),8),permutation=perm))
  return moves
 def boundaries(self):
  if self.arcs is not None:return self.arcs
  circles=[]
  for u in self.U:
   if any(np.linalg.norm(u-v)<1e-7 or (self.v['angle']==90 and np.linalg.norm(u+v)<1e-7) for v in circles):continue
   circles.append(u)
  arcs=[[] for _ in range(self.N)];s=math.sin(self.alpha)
  for u in circles:
   e=np.cross(u,[0,0,1] if abs(u[2])<.9 else [0,1,0]);e/=np.linalg.norm(e);b=np.cross(u,e)
   angles=[]
   for w in circles:
    if np.linalg.norm(w-u)<1e-7:continue
    A=w@e;B=w@b;t=self.h*(1-w@u)/s;length=math.hypot(A,B)
    if length<1e-10 or abs(t)>length+1e-8:continue
    ratio=t/length
    if abs(abs(ratio)-1)<1e-8:ratio=math.copysign(1,ratio)
    phi=math.atan2(B,A);delta=math.acos(np.clip(ratio,-1,1))
    for a in [(phi-delta)%TAU,(phi+delta)%TAU]:
     if not any(abs((a-c+np.pi)%TAU-np.pi)<1e-7 for c in angles):angles.append(a)
   angles.sort()
   if not angles:angles=[0.]
   for a,z in zip(angles,angles[1:]+[angles[0]+TAU]):
    if z-a<1e-7:continue
    mid=(a+z)/2;p=self.h*u+s*(math.cos(mid)*e+math.sin(mid)*b);inside=u-self.h*p;inside/=np.linalg.norm(inside)
    clearance=min([abs(w@p-self.h) for w in circles if np.linalg.norm(w-u)>1e-7]+[1.])
    epsilon=min(.0015,clearance/4)
    for direction in [-1,1]:
     p2=p+direction*epsilon*inside;p2/=np.linalg.norm(p2);j=self.locate(p2)
     if j<0:
      p2=p+direction*.0001*inside;p2/=np.linalg.norm(p2);j=self.locate(p2)
     assert j>=0,(self.f['key'],self.v['angle'],u,a,z,direction)
     arcs[j].append((u,e,b,a,z))
  assert all(arcs)
  self.arcs=arcs;return arcs
 def extent(self,j,q):
  key=(j,*np.round(q,8))
  if key in self.extent_cache:return self.extent_cache[key]
  values=[];s=math.sin(self.alpha)
  for u,e,b,a,z in self.boundaries()[j]:
   A=q@e;B=q@b;base=self.h*(q@u)
   values.extend([base+s*(A*math.cos(a)+B*math.sin(a)),base+s*(A*math.cos(z)+B*math.sin(z))])
   t=math.atan2(B,A)
   for phi in [t,t+np.pi]:
    shifted=a+(phi-a)%TAU
    if shifted<=z+1e-8:values.append(base+s*(A*math.cos(phi)+B*math.sin(phi)))
  hi=max(values);lo=min(values)
  if self.locate(q)==j:hi=1.
  if self.locate(-q)==j:lo=-1.
  self.extent_cache[key]=(lo,hi)
  return lo,hi
 def legal(self,Rs):
  result=[]
  for i,u in enumerate(self.axes):
   inside=[];valid=True
   for j,R in enumerate(Rs):
    lo,hi=self.extent(j,R.T@u)
    if lo>=self.h-2e-7:inside.append(j)
    elif hi>self.h+2e-7:valid=False;break
   if valid:result.append((i,inside))
  return result
 def candidates(self,Rs,i,inside):
  u=self.axes[i];normals=[]
  for j in inside:
   for w,*_ in self.boundaries()[j]:
    p=Rs[j]@w
    if not any(np.linalg.norm(p-q)<1e-6 for q in normals):normals.append(p)
  angles=[]
  for n in normals:
   for target in self.axes:
    if abs(n@u-target@u)>1e-6:continue
    a=n-(n@u)*u;b=target-(target@u)*u
    if np.linalg.norm(a)<1e-7:continue
    phi=math.atan2(u@np.cross(a,b),a@b)
    if abs(phi)>1e-7 and not any(abs((phi-v+np.pi)%TAU-np.pi)<1e-6 for v in angles):angles.append(phi)
  return angles
 def fits(self,j,R,k):
  # Bound every moved boundary arc against every target circle. A candidate
  # is a slot match only when its membership signature is constant throughout.
  for i,u in enumerate(self.U):
   lo,hi=self.extent(j,R.T@u)
   if self.v['pieces'][k]['mask']&(1<<i):
    if lo<self.h-2e-6:return False
   elif hi>self.h+2e-6:return False
  return True

def groups(n,moves):
 parent=list(range(n))
 def find(i):
  while parent[i]!=i:i=parent[i]
  return i
 for m in moves:
  for i,j in enumerate(m['permutation']):parent[find(i)]=find(j)
 g={}
 for i in range(n):g.setdefault(find(i),[]).append(i)
 return sorted(g.values(),key=lambda x:x[0])
