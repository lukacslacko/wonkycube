from pathlib import Path
import json,sys,numpy as np,trimesh
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[3];D=ROOT/'designs/triangular-prism-v1';O=ROOT/'docs/solving/triangular-prism/figures'
M=json.loads((D/'manifest.json').read_text());R=np.array(json.loads((D/'reference/cube-to-mechanism.json').read_text()))
rows={r['name']:r for r in json.loads((D/'reference/parts.json').read_text())}
labels={'C01':'L','C02':'R','C03':'B','C04':'U','C05':'D','V01':'F','V02':'BL','V03':'BR','H01':'LU','H02':'LD','H03':'RU','H04':'RD','H05':'BU','H06':'BD','K01':'FU','K02':'FD','K03':'BLU','K04':'BLD','K05':'BRU','K06':'BRD'}
pal={'C':'#73b69b','V':'#72abcc','H':'#d899ad','K':'#ecc867','core':'#adb5bc'}
parts=[]
for r in M['parts']:
 if '/puzzle/' not in r['file']:continue
 m=trimesh.load(D/r['file'],force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3]
 parts.append((r,m))
def normalize(x):return np.array(x)/np.linalg.norm(x)
def rgb(s):return np.array([int(s[i:i+2],16) for i in [1,3,5]])
for tag,el,az in [('front',26,60),('back',-26,240),('top',68,60),('bottom',-68,240)]:
 size=1000;extent=58
 a,e=np.radians([az,el]);direction=np.array([np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e)])
 right=normalize(np.cross([0,0,1],direction));up=np.cross(direction,right);view=np.array([right,up,direction]);light=normalize(.55*direction+.7*up-.4*right)
 owner=np.full((size,size),-1,np.int16);depth=np.full((size,size),-1e10);shade=np.ones((size,size))
 for k,(r,m) in enumerate(parts):
  v=m.vertices@view.T;v[:,:2]=np.column_stack(((v[:,0]/extent+1)*size/2,(1-v[:,1]/extent)*size/2))
  good=m.face_normals@direction>1e-8;faces=m.faces[good];norm=m.face_normals[good]
  shades=.35+.45*np.maximum(norm@light,0)+.20*np.maximum(norm@direction,0)
  for f,sh in zip(faces,shades):
   p=v[f];xmin,ymin=np.maximum(np.floor(p[:,:2].min(axis=0)).astype(int),0);xmax,ymax=np.minimum(np.ceil(p[:,:2].max(axis=0)).astype(int),size-1)
   if xmax<xmin or ymax<ymin:continue
   aa,b,c=p;den=(b[1]-c[1])*(aa[0]-c[0])+(c[0]-b[0])*(aa[1]-c[1])
   if abs(den)<1e-10:continue
   yy,xx=np.mgrid[ymin:ymax+1,xmin:xmax+1];xx=xx+.5;yy=yy+.5
   u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;w=((c[1]-aa[1])*(xx-c[0])+(aa[0]-c[0])*(yy-c[1]))/den;t=1-u-w
   zz=u*aa[2]+w*b[2]+t*c[2];old=depth[ymin:ymax+1,xmin:xmax+1];mask=(u>=-1e-8)&(w>=-1e-8)&(t>=-1e-8)&(zz>old)
   old[mask]=zz[mask];owner[ymin:ymax+1,xmin:xmax+1][mask]=k;shade[ymin:ymax+1,xmin:xmax+1][mask]=sh
 for mode in ['all','C','V','H','K']:
  pix=np.full((size,size,3),[250,250,248],np.uint8)
  for k,(r,m) in enumerate(parts):
   mask=owner==k;col=pal.get(r['family'],'#adb5bc') if mode=='all' or r['family']==mode else '#dfe3e5'
   pix[mask]=np.clip(shade[mask,None]*rgb(col),0,255)
  im=Image.fromarray(pix)
  if mode=='all':
   im.save(O/f'{tag}.png')
   draw=ImageDraw.Draw(im);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',32)
   for k,(r,m) in enumerate(parts):
    if r['name'] not in labels:continue
    omit={'front':{'C05'},'back':set(),'top':{'C05','H02','H04','H06','K02','K04','K06'},'bottom':{'C04','H01','H03','H05','K01','K03','K05','V01'}}
    if r['name'] in omit[tag]:continue
    mask=owner==k
    if mask.sum()<800:continue
    dist=distance_transform_edt(mask);y,x=np.unravel_index(dist.argmax(),dist.shape)
    lab=labels[r['name']];bb=draw.textbbox((0,0),lab,font=font);w=bb[2];h=bb[3]-bb[1]
    draw.rounded_rectangle((x-w/2-7,y-h/2-6,x+w/2+7,y+h/2+6),radius=5,fill='#fafaf8',outline='#536775',width=1)
    draw.text((x,y),lab,anchor='mm',font=font,fill='#243b49')
   im.save(O/f'atlas-{tag}.png')
  else:im.save(O/f'{mode}-{tag}.png')
 print('Rendered',tag,flush=True)
