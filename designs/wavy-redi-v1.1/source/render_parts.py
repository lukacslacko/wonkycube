"""Previews and assembly illustrations from the delivered STL geometry."""
from redi_design import *
import mesh_render as rr
from PIL import Image,ImageDraw,ImageFont
DEST=Path(sys.argv[1]);IMG=DEST/'images';IMG.mkdir(exist_ok=True)
COLORS={'C':'#63b2ab','E':'#edaa69','core':'#a7afb8'}
def font(size):
 return ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',size)
parts={r['name']:load(OUT/'printed'/(r['name']+'.npz')) for r in ROWS};parts['core']=load(OUT/'printed/core.npz')
objects=[]
for name,s in parts.items():
 rr.meshes[name]=mesh(s.as_original().simplify(.045));objects.append((name,R.T,np.zeros(3),COLORS.get(name,COLORS.get(name[0]))))
cam=SPEC['camera'];yaw=np.degrees(cam['yaw_radians']);elev=np.degrees(cam['elevation_radians'])
board=Image.new('RGB',(1700,1060),'#fafaf8');draw=ImageDraw.Draw(board)
draw.text((60,35),'Wavy Redi · 64 mm',font=font(43),fill='#243b40')
draw.text((60,94),'Wavy cuts with reinforced core connections',font=font(25),fill='#4c6469')
for j,(az,el) in enumerate([(yaw,elev),(yaw+180,-elev)]):
 im=rr.render(objects,size=820,extent=59,elev=el,az=az);board.paste(im,(j*840+10,150))
draw.text((60,1000),'8 screwed pieces  ·  12 floating petals  ·  1 core with 6 exposed patches',font=font(25),fill='#4c6469')
board.save(IMG/'solved.png')

# A diagonal cut shows one complete axial bearing and the adjacent petal.
cut=[];plane=np.array([1.,-1,0])/np.sqrt(2)
for name,s in parts.items():
 v=s.trim_by_plane(plane,0)
 if not v.is_empty():rr.meshes[name+'-cut']=mesh(v.as_original().simplify(.035));cut.append((name+'-cut',np.eye(3),np.zeros(3),COLORS.get(name,COLORS.get(name[0]))))
for i,n in enumerate(AXES):
 for j,s in enumerate(hardware(n)):
  v=s.trim_by_plane(plane,0)
  if v.is_empty():continue
  name=f'hw-{i}-{j}';rr.meshes[name]=mesh(v);cut.append((name,np.eye(3),np.zeros(3),'#596d7a' if j==0 else '#d6b15f'))
rr.render(cut,size=1150,extent=58,elev=17,az=135).save(IMG/'section.png')
rr.render([('core',R.T,np.zeros(3),COLORS['core'])],size=1000,extent=46,elev=25,az=-55).save(IMG/'core.png')

remaining={r['name'] for r in ROWS};groups=[]
for i in range(8):
 names=[r['name'] for r in ROWS if r['name'] in remaining and i in r['signature']];remaining.difference_update(names);groups.append((i,names))
board=Image.new('RGB',(1640,1090),'#fafaf8');d=ImageDraw.Draw(board)
d.text((38,22),'Assembly order · insert each pictured group together',font=font(32),fill='#243b40')
for j,(i,names) in enumerate(groups[::-1]):
 n=AXES[i];view=n@R;el=np.degrees(np.arcsin(view[2]));az=np.degrees(np.arctan2(view[1],view[0]))
 objs=[o for o in objects if o[0] in names]
 im=rr.render(objs,size=395,extent=48,elev=el,az=az)
 x=(j%4)*410;y=85+(j//4)*485;board.paste(im,(x,y))
 d.text((x+20,y+385),f'{j+1}. '+', '.join(names),font=font(20),fill='#243b40')
 d.text((x+20,y+418),f'Slide toward pad {i+1}; then add screw.',font=font(17),fill='#5b6c72')
board.save(IMG/'assembly-groups.png')

board=Image.new('RGB',(1320,1250),'#fafaf8');d=ImageDraw.Draw(board)
d.text((35,20),'Piece identification · mark IDs on the inside',font=font(32),fill='#243b40')
for j,row in enumerate(ROWS):
 name=row['name'];m=rr.meshes[name];center=m.bounds.mean(axis=0)
 rr.meshes['tile']=m.copy();rr.meshes['tile'].vertices-=center
 tile=rr.render([('tile',R.T,np.zeros(3),COLORS[name[0]])],size=254,extent=max(16,np.linalg.norm(np.ptp(m.vertices,axis=0))*.57),elev=26,az=-55)
 x=j%5*264;y=80+j//5*288;board.paste(tile,(x,y));d.text((x+15,y+247),name,font=font(22),fill='#243b40')
board.save(IMG/'piece-identification.png')

# Show core-pad labels in their actual 3D locations on the core.
def pad_view(az,el):
 size=800;extent=46
 im=rr.render([('core',R.T,np.zeros(3),COLORS['core'])],size=size,extent=extent,elev=el,az=az);d=ImageDraw.Draw(im)
 elev,az=np.radians([el,az]);v=np.array([np.cos(elev)*np.cos(az),np.cos(elev)*np.sin(az),np.sin(elev)])
 right=np.cross([0,0,1],v);right/=np.linalg.norm(right);up=np.cross(v,right)
 for i,n in enumerate(AXES):
  nc=n@R
  if nc@v<.02:continue
  p=nc*18.4;x=(p@right/extent+1)*size/2;y=(1-p@up/extent)*size/2
  d.ellipse([x-25,y-17,x+25,y+17],fill='#fafaf8',outline='#30515c',width=2)
  d.text((x,y),str(i+1),font=font(24),anchor='mm',fill='#243b40')
 return im
board=Image.new('RGB',(1620,885),'#fafaf8');board.paste(pad_view(-55,25),(0,70));board.paste(pad_view(125,-25),(820,70));d=ImageDraw.Draw(board)
d.text((35,18),'Core pad numbers · also marked by 1–8 recessed dots',font=font(32),fill='#243b40');board.save(IMG/'core-pad-map.png')
print('Rendered',IMG,flush=True)
