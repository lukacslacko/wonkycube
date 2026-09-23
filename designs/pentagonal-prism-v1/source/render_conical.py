"""Render the delivered, reloaded print meshes and actual exterior face maps."""
from conical_design import *
import mesh_render as mr
from PIL import Image,ImageDraw,ImageFont
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPoly
import sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
META=json.loads((DEST/'manifest.json').read_text());MAN={r['name']:r for r in META['parts']}
COLORS={'C':'#73b69b','V':'#72abcc','H':'#d899ad','K':'#ecc867','core':'#78838b'}
for name in [r['name'] for r in ROWS]+['core']:
 row=MAN[name];m=trimesh.load(DEST/row['file'],force='mesh');t=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3];mr.meshes[name]=m
for i,n in enumerate(AXES):
 for label,s in zip(['screw','washer'],hardware(n)):
  mr.meshes[f'{label}{i}']=mesh(s)
def font(size):
 try:return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',size)
 except OSError:return ImageFont.truetype(str(Path(matplotlib.get_data_path())/'fonts/ttf/DejaVuSans.ttf'),size)
def caption(canvas,title,subtitle):
 d=ImageDraw.Draw(canvas);d.text((35,22),title,font=font(30),fill='#233c42');d.text((35,63),subtitle,font=font(18),fill='#53616a')
objects=[(r['name'],R.T,np.zeros(3),COLORS[r['family']]) for r in ROWS]+[('core',R.T,np.zeros(3),COLORS['core'])]
objects += [(f'{label}{i}',R.T,np.zeros(3),'#afb7bd') for i in range(7) for label in ['screw','washer']]
canvas=Image.new('RGB',(1600,900),'#fafaf8')
for j,(el,az) in enumerate([(30.1,-45),(-30.1,135)]):
 im=mr.render(objects,size=800,extent=56,elev=el,az=az);canvas.paste(im,(j*800,100))
caption(canvas,'Wonky pentagonal prism — 60° / 64 mm','Print meshes + hardware envelopes · centers green · vertical petals blue · horizontal petals rose · corners yellow')
canvas.save(DEST/'images/solved-two-sides.png');print('RENDER solved',flush=True)
exploded=[(r['name'],R.T,np.array(r['direction'])@R*18,COLORS[r['family']]) for r in ROWS]+[('core',R.T,np.zeros(3),COLORS['core'])]
im=mr.render(exploded,size=1200,extent=85,elev=25,az=-50)
canvas=Image.new('RGB',(1200,1290),'#fafaf8');canvas.paste(im,(0,90));caption(canvas,'32 exterior pieces + one core','Seven screwed centers retain fifteen petals; petals retain ten corners.');canvas.save(DEST/'images/exploded.png');print('RENDER exploded',flush=True)
canvas=Image.new('RGB',(1800,540),'#fafaf8')
for j,name in enumerate(['C01','V01','H01','K01']):
 row=next(r for r in ROWS if r['name']==name);n=np.array(row['direction']);q=frame(n).T
 im=mr.render([(name,q,-q@(28*n),COLORS[row['family']])],size=450,extent=32,elev=-35,az=-45);canvas.paste(im,(450*j,90))
 ImageDraw.Draw(canvas).text((450*j+30,95),name,font=font(25),fill='#233c42')
caption(canvas,'Internal shoulders, rounded track entries, and flat axle foot','Actual print meshes, viewed from the core side')
canvas.save(DEST/'images/internal-pieces.png');print('RENDER internals',flush=True)
# Six exterior panels; each displays the actual flat surface remaining after rounding.
fig,axs=plt.subplots(2,3,figsize=(15,10),facecolor='#fafaf8');maps=[]
for ax,(dim,sign) in zip(axs.flat,itertools.product(range(3),[1,-1])):
 others=[i for i in range(3) if i!=dim];count=0
 for row in ROWS:
  m=mr.meshes[row['name']];v=m.vertices@R;tri=v[m.faces];mask=np.max(abs(tri[:,:,dim]-sign*SIDE/2),axis=1)<.001
  patches=[Polygon(t[:,others]).buffer(0) for t in tri[mask]]
  if not patches:continue
  poly=unary_union(patches);items=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
  for p in items:
   if p.area<1:continue
   pts=np.asarray(p.exterior.coords);ax.add_patch(PlotPoly(pts,facecolor=COLORS[row['family']],edgecolor='#3c4c54',lw=.5))
   for hole in p.interiors:ax.add_patch(PlotPoly(np.asarray(hole.coords),facecolor='#fafaf8',edgecolor='#3c4c54',lw=.5))
   point=p.representative_point();ax.text(point.x,point.y,row['name'],ha='center',va='center',fontsize=9,fontweight='bold');count+=1
   maps.append(dict(exterior_face=f'{"+" if sign>0 else "-"}{"XYZ"[dim]}',piece=row['name'],surface_area_mm2=p.area))
 ax.set(xlim=(-34,34),ylim=(-34,34),aspect='equal',title=f'Exterior {"+" if sign>0 else "−"}{"XYZ"[dim]}');ax.axis('off')
fig.suptitle('Assembly identification — six outside faces\nFlat surface areas only; white bands include rounded edges',fontsize=17);fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(DEST/'images/assembly-map.png',dpi=170);plt.close(fig)
(DEST/'reference/exterior-face-pieces.json').write_text(json.dumps(maps,indent=2));print('RENDER map',flush=True)
# Interior-facing thumbnails identify every loose piece without relying on color.
for family in ['C','V','H','K']:
 rows=[r for r in ROWS if r['family']==family];cols=4;nr=(len(rows)+cols-1)//cols
 canvas=Image.new('RGB',(cols*360,nr*370+100),'#fafaf8');caption(canvas,f'{family} pieces — mark these IDs inside','Viewed from the core side; printing orientations are stored separately in the STL files.')
 for j,row in enumerate(rows):
  n=np.array(row['direction']);q=frame(n).T;name=row['name'];v=mr.meshes[name].vertices@q.T;center=(v.min(axis=0)+v.max(axis=0))/2
  el,az=np.radians([-35.,-45.]);direction=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);right=mr.normalize(np.cross([0,0,1],direction));up=np.cross(direction,right)
  extent=float(np.max(np.abs((v-center)@np.array([right,up]).T)))*1.12
  im=mr.render([(name,q,-center,COLORS[family])],size=330,extent=extent,elev=-35,az=-45)
  x=(j%cols)*360;y=100+(j//cols)*370;canvas.paste(im,(x+15,y+30));ImageDraw.Draw(canvas).text((x+15,y+5),name,font=font(24),fill='#233c42')
 canvas.save(DEST/f'images/catalog-{family}.png');print('RENDER catalog',family,flush=True)
