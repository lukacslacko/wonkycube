"""Render the delivered Redi geometry and dimensioned hardware cross-section."""
from redi_design import *
from PIL import Image,ImageDraw,ImageFont
import mesh_render as rr
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
IMG=DEST/'images';IMG.mkdir(exist_ok=True)
colors={'C':'#9e7cc1','E':'#e6b247','core':'#b2b8bf'}
objects=[];cut=[]
for row in ROWS:
 name=row['name'];s=load(OUT/'printed'/(name+'.npz'))
 rr.meshes[name]=mesh(s.simplify(.07));objects.append((name,R.T,np.zeros(3),colors[name[0]]))
 inner=s.trim_by_plane([0,1,0],0)
 if not inner.is_empty():rr.meshes[name+'cut']=mesh(inner.simplify(.06));cut.append((name+'cut',np.eye(3),np.zeros(3),colors[name[0]]))
rr.meshes['core']=mesh(core().simplify(.03));objects.append(('core',R.T,np.zeros(3),colors['core']))
rr.meshes['corecut']=mesh(core().trim_by_plane([0,1,0],0).simplify(.03));cut.append(('corecut',np.eye(3),np.zeros(3),colors['core']))
rr.render(objects,size=950,extent=50,elev=27,az=-55).save(IMG/'solved.png')
rr.render(cut,size=950,extent=47,elev=18,az=-90).save(IMG/'mechanism-section.png')
try:font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
except:font=ImageFont.load_default()
im=Image.new('RGB',(1200,1060),'#fafaf8');draw=ImageDraw.Draw(im)
for idx,row in enumerate(ROWS):
 name=row['name'];m=rr.meshes[name];center=m.bounds.mean(axis=0)
 rr.meshes['tile']=m.copy();rr.meshes['tile'].vertices-=center
 tile=rr.render([('tile',R.T,np.zeros(3),colors[name[0]])],size=210,extent=max(16,np.linalg.norm(np.ptp(m.vertices,axis=0))*.56),elev=25,az=-55)
 x=(idx%5)*240;y=(idx//5)*260;im.paste(tile,(x,y));draw.text((x+10,y+218),name,fill='#29333e',font=font)
im.save(IMG/'piece-identification.png')
im=Image.new('RGB',(1500,1000),'#fafaf8');draw=ImageDraw.Draw(im)
try:
 font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',24)
 small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',21)
 title=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',34)
except:small=title=font
draw.text((65,38),'Compact Redi v4.3 · captive M3 locknut',font=title,fill='#273847')
draw.text((65,88),'Actual CAD cross-section · 64 mm cube · dimensions in mm',font=small,fill='#627481')
f=frame(AXES[0]);plane=np.array([[1.,0,0],[0,0,1],[0,-1,0]])
def point(p):return (620+18*p[0],890-24*(p[1]-6))
def shape(s,color):
 p=xform(xform(s,f.T),plane).slice(.001)
 p=p^mf.CrossSection.square([30,33],False).translate([-15,6])
 for sign in [1,-1]:
  for pp in p.to_polygons():
   a=np.asarray(pp);area=np.sum(a[:,0]*np.roll(a[:,1],-1)-a[:,1]*np.roll(a[:,0],-1))
   if area*sign>0:draw.polygon([point(v) for v in a],fill=color if sign==1 else '#fafaf8')
shape(core(),'#aeb9c1');shape(load(OUT/'printed/C01.npz'),'#b28bcc')
screw,washer=hardware(AXES[0]);shape(screw,'#506371');shape(washer,'#dfb452');shape(xform(nut_shape(),f),'#697b88')
draw.line([point([0,6]),point([0,38])],fill='#668799',width=1)
def label(text,anchor,xy):
 p=point(anchor);x,y=xy;end=(x-10,y+12) if x>p[0] else (x+325,y+12)
 draw.line([p,(end[0],p[1]),end],fill='#425a69',width=2);draw.ellipse((p[0]-3,p[1]-3,p[0]+3,p[1]+3),fill='#425a69');draw.text(xy,text,font=font,fill='#273847')
label('Ø9.6 access well',[4.8,34],(1000,175))
label('DIN912 M3 × 20\n2.5 mm hex key',[2.75,30],(1000,290))
label('9 × 1 washer\nSeat at 27.30',[4.3,27.8],(1000,400))
label('Ø3.6 rotating bore',[1.8,22],(65,480))
label('0.10 bearing release\nCore flat at 17.60',[3,17.7],(1000,575))
label('1.95 mm retaining roof',[2,16.5],(65,665))
label('DIN985 M3\nNylon end inward',[2.4,12.1],(1000,750))
label('Screw tip at 8.30\n3.35 beyond nominal nut',[0,8.3],(65,820))
draw.text((65,945),'M3 × 20 fits. One fifth turn (72°) moves the screw head by 0.10 mm; adjust gently by feel.',font=small,fill='#425a69')
im.save(IMG/'hardware-dimensions.png')
print('Rendered previews',flush=True)
