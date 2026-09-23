"""Constant R2 circles on concentric spherical sections of the petal lens.

Each section is an intersection of spherical caps. Shrink both caps by
delta=asin(R/r), then dilate their intersection by delta on the sphere.
The tips become circles of exactly R mm; the other cap boundaries remain
unchanged. This avoids branch jumps in Cartesian slices of a wavy ridge.
"""
from redi_design import *
from scipy.optimize import brentq
D=np.array([1,1,0])/np.sqrt(2);B=np.array([1,-1,0])/np.sqrt(2);Z=np.array([0,0,1])
A=np.sqrt(2/3);H=1/np.sqrt(3);ALPHA=np.arccos(A)

def radial_profile():
 p=np.array(mf.CrossSection([profile()]).offset(-BODY_GAP/2,join_type=mf.JoinType.Round,circular_segments=48).to_polygons()[0])
 rr=np.linalg.norm(p,axis=1);p=p[(p[:,0]>1)&(rr<58)];p=p[np.argsort(np.linalg.norm(p,axis=1))]
 rr=np.linalg.norm(p,axis=1);keep=np.r_[True,np.diff(rr)>1e-8];return p[keep],rr[keep]

def angle_function():
 p,rs=radial_profile()
 def theta(r):
  i=int(np.clip(np.searchsorted(rs,r)-1,0,len(rs)-2));a=p[i];v=p[i+1]-a
  aa=v@v;bb=2*a@v;cc=a@a-r*r;t=(-bb+np.sqrt(max(0,bb*bb-4*aa*cc)))/(2*aa)
  q=a+np.clip(t,0,1)*v;return float(np.arctan2(q[0],q[1]))
 return theta,rs

def spherical_mask(radius=ROUND_R):
 theta,stations=angle_function();f=lambda r:theta(r)-np.arcsin(radius/r)-ALPHA
 grid=np.linspace(INNER_R,28,1000);first=next(i for i,r in enumerate(grid) if f(r)>0)
 minimum=INNER_R if first==0 else brentq(f,grid[first-1],grid[first]);start=minimum+.008;memo={}
 def section(r):
  if r not in memo:
   th=theta(r);delta=np.arcsin(radius/r);bc=np.arccos(np.clip(np.cos(th-delta)/A,-1,1))
   uc=D*np.cos(bc)+B*np.sin(bc);wc=-D*np.sin(bc)+B*np.cos(bc)
   n=AXES[6];v=(uc-n*np.cos(th-delta))/np.sin(th-delta);tangent=n*np.cos(th)+v*np.sin(th)
   bt=np.arctan2(tangent@B,tangent@D);phi=np.arctan2(tangent@Z,tangent@wc)
   betas=np.linspace(-bt,bt,65);aa=A*np.cos(betas)
   lat=np.arccos(np.clip(np.cos(th)/np.sqrt(aa*aa+H*H),-1,1))-np.arctan2(H,aa)
   top=(D[None,:]*np.cos(betas)[:,None]+B[None,:]*np.sin(betas)[:,None])*np.cos(lat)[:,None]+Z[None,:]*np.sin(lat)[:,None]
   phis=np.linspace(phi,-phi,49)
   right=uc[None,:]*np.cos(delta)+(wc[None,:]*np.cos(phis)[:,None]+Z[None,:]*np.sin(phis)[:,None])*np.sin(delta)
   bottom=top[::-1].copy();bottom[:,2]*=-1
   left=right[::-1]-(right[::-1]@B)[:,None]*B[None,:]*2
   ring=np.vstack([top[:-1],right[:-1],bottom[:-1],left[:-1]])*r
   assert np.linalg.norm(top[-1]-right[0])<1e-7
   memo[r]=(ring,dict(radius_from_center_mm=float(r),fillet_radius_mm=radius,theta_rad=th,delta_rad=float(delta),center_direction=uc.tolist(),side_direction=wc.tolist(),half_arc_angle_rad=float(phi)))
  return memo[r]
 rs=sorted(set(np.r_[start,np.arange(np.ceil(start*10)/10,55.61,.16),stations[(stations>start)&(stations<55.6)],55.65].tolist()))
 for depth in range(9):
  extra=[]
  for a,b in zip(rs[:-1],rs[1:]):
   if b-a<.003:continue
   pa=section(a)[0];pb=section(b)[0];mid=(a+b)/2;pm=section(mid)[0]
   if np.linalg.norm(pm-(pa+pb)/2,axis=1).max()>.004:extra.append(mid)
  if not extra:break
  rs=sorted(rs+extra)
 rings=[section(r)[0] for r in rs]
 # A fan closing a spherical rim lies INSIDE that sphere. Closing at
 # r=55.65 therefore clipped four cube vertices despite the rim exceeding
 # the cube's circumradius. Extend the tool radially before capping it.
 # Its entire far cap now lies beyond a separating plane outside the
 # bounding sphere of every solved or scrambled piece. This continuation
 # only exists outside the puzzle; all actual R2 sections stay unchanged.
 rings.append(rings[-1]*2)
 assert float((rings[-1]@D).min()) > SIDE*np.sqrt(3)/2+5
 n=len(rings[0]);verts=list(np.vstack(rings));faces=[]
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;faces.extend([[a,b,a+n],[b,b+n,a+n]])
 for k,reverse in [(0,True),(len(rings)-1,False)]:
  center=len(verts);verts.append(np.mean(rings[k],axis=0))
  for j in range(n):
   face=[center,k*n+j,k*n+(j+1)%n];faces.append(face[::-1] if reverse else face)
 m=trimesh.Trimesh(np.array(verts),np.array(faces),process=True)
 if m.volume<0:m.invert()
 assert m.is_watertight and m.is_winding_consistent
 mask=from_mesh(m);assert mask.status()==mf.Error.NoError
 # Remove the tiny starting cap, where a full R2 disk does not yet fit.
 mask-=mf.Manifold.sphere(minimum+.05,SEG)
 return mask,[section(r)[1] for r in rs],minimum

if __name__=='__main__':
 t=time.time();s=load(OUT/'edge-inner-rounded.npz');mask,records,minimum=spherical_mask()
 save(mask,OUT/'ridge-mask.npz');result=main(s^mask)
 before_trim=result.volume();low=float((mesh(result).vertices@D).min());result=main(result.trim_by_plane(D,low+PRINT_FOOT_TRIM))
 save(result,OUT/'canonical-E.npz')
 (OUT/'ridge-sections.json').write_text(json.dumps(records,indent=2))
 (OUT/'ridge-summary.json').write_text(json.dumps(dict(method='spherical sections with exact R2 tip circles',sections=len(records),first_full_radius_section_mm=minimum,bed_flat_depth_mm=PRINT_FOOT_TRIM,bed_flat_removed_mm3=before_trim-result.volume()),indent=2))
 print('spherical R2',time.time()-t,'seconds',len(records),'sections; inner start',minimum,flush=True)
