"""Orthographic depth-buffer renderer for generated mesh previews."""
import numpy as np
from PIL import Image
meshes={}
def rgb(s):return np.array([int(s[i:i+2],16) for i in (1,3,5)],float)
def normalize(x):return np.array(x)/np.linalg.norm(x)

def render(objects,size=720,extent=90,elev=24,az=-55):
 el,aa=np.radians([elev,az]);direction=np.array([np.cos(el)*np.cos(aa),np.cos(el)*np.sin(aa),np.sin(el)])
 right=normalize(np.cross([0,0,1],direction));up=np.cross(direction,right);view=np.array([right,up,direction])
 light=normalize([-.4,-.7,1]);pixels=np.full((size,size,3),[250,250,248],np.uint8);depth=np.full((size,size),-1e10,float)
 for name,T,shift,color in objects:
  m=meshes[name];v=m.vertices@T.T+shift;norm=m.face_normals@T.T;v=v@view.T
  v[:,:2]=np.column_stack(((v[:,0]/extent+1)*size/2,(1-v[:,1]/extent)*size/2))
  faces=m.faces[norm@direction>1e-8];norm=norm[norm@direction>1e-8]
  shades=rgb(color)[None,:]*(.60+.40*np.maximum(norm@light,0))[:,None]
  for f,color in zip(faces,shades):
   p=v[f];xmin,ymin=np.maximum(np.floor(p[:,:2].min(axis=0)).astype(int),0);xmax,ymax=np.minimum(np.ceil(p[:,:2].max(axis=0)).astype(int),size-1)
   if xmax<xmin or ymax<ymin:continue
   a,b,c=p;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-10:continue
   yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+.5;yy=yy+.5
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
   w=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;t=1-u-w
   zz=u*a[2]+w*b[2]+t*c[2];old=depth[ymin:ymax+1,xmin:xmax+1]
   mask=(u>=-1e-8)&(w>=-1e-8)&(t>=-1e-8)&(zz>old)
   old[mask]=zz[mask];pixels[ymin:ymax+1,xmin:xmax+1][mask]=np.clip(color,0,255)
 return Image.fromarray(pixels)
