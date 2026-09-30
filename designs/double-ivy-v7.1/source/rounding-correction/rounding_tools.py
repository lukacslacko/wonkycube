"""Complete both tangencies of the saved symmetric outer R2 fillet.

Only C/F outer material is altered; inward station blending avoids a new
ledge where the correction starts. The caller protects the inner shell.
"""
from geometry import *
def tool(rec):
 ss=rec['sections'];base=np.array([r['station_mm'] for r in ss]);params=np.array([[*r['center'],*r['angles']] for r in ss]);xs=np.unique(np.round(np.r_[base,np.arange(32.2,33.501,.1)],6))
 rings=[]
 for x in xs:
  cy,cz,lo,hi=[np.interp(x,base,params[:,j]) for j in range(4)];assert abs(cz)<1e-8
  blend=np.clip((x-32.2)/1.2,0,1);blend=blend*blend*(3-2*blend);a=max(abs(lo),abs(hi));lo=(1-blend)*lo-blend*a;hi=(1-blend)*hi+blend*a
  theta=np.linspace(lo,hi,49);arc=np.column_stack([cy-2*np.cos(theta),cz+2*np.sin(theta)])
  yz=np.vstack([[-100,cz],[-100,arc[0,1]],arc,[-100,arc[-1,1]]]);rings.append(np.column_stack([yz,np.full(len(yz),x)]))
 n=len(rings[0]);faces=[]
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;faces.extend([[a,b,a+n],[b,b+n,a+n]])
 for j in range(1,n-1):
  faces.append([0,j+1,j]);a=(len(rings)-1)*n;faces.append([a,a+j,a+j+1])
 m=trimesh.Trimesh(np.vstack(rings),np.array(faces),process=True)
 if m.volume<0:m.invert()
 assert m.is_watertight and m.is_winding_consistent
 return xform(from_mesh(m),np.array(rec['frame']).T)
