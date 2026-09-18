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
COLORS={'C':'#73b69b','E':'#72abcc','K':'#ecc867','core':'#78838b'}
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
objects += [(f'{label}{i}',R.T,np.zeros(3),'#afb7bd') for i in range(6) for label in ['screw','washer']]
canvas=Image.new('RGB',(1600,900),'#fafaf8')
for j,(el,az) in enumerate([(30.1,-45),(-30.1,135)]):
 im=mr.render(objects,size=800,extent=56,elev=el,az=az);canvas.paste(im,(j*800,100))
caption(canvas,'Wonky conical 3×3 — 70° / 64 mm','Actual print meshes · opposite views · centers green, edges blue, corners yellow')
canvas.save(DEST/'images/solved-two-sides.png');print('RENDER solved',flush=True)
exploded=[(r['name'],R.T,np.array(r['direction'])@R*18,COLORS[r['family']]) for r in ROWS]+[('core',R.T,np.zeros(3),COLORS['core'])]
im=mr.render(exploded,size=1200,extent=85,elev=25,az=-50)
canvas=Image.new('RGB',(1200,1290),'#fafaf8');canvas.paste(im,(0,90));caption(canvas,'26 moving pieces + one core','Six screwed centers retain twelve edges; edges retain eight corners.');canvas.save(DEST/'images/exploded.png');print('RENDER exploded',flush=True)
canvas=Image.new('RGB',(1800,690),'#fafaf8')
for j,name in enumerate(['C01','E01','K01']):
 row=next(r for r in ROWS if r['name']==name);n=np.array(row['direction']);q=frame(n).T
 im=mr.render([(name,q,-q@(28*n),COLORS[row['family']])],size=600,extent=26,elev=-35,az=-45);canvas.paste(im,(600*j,90))
 ImageDraw.Draw(canvas).text((600*j+30,95),name,font=font(25),fill='#233c42')
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
fig.suptitle('Assembly identification — six outside faces\nMatch the shapes and mark the piece IDs on their insides',fontsize=17);fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(DEST/'images/assembly-map.png',dpi=170);plt.close(fig)
(DEST/'reference/exterior-face-pieces.json').write_text(json.dumps(maps,indent=2));print('RENDER map',flush=True)
# Interior-facing thumbnails identify every loose piece without relying on color.
for family in ['C','E','K']:
 rows=[r for r in ROWS if r['family']==family];cols=4;nr=(len(rows)+cols-1)//cols
 canvas=Image.new('RGB',(cols*360,nr*370+100),'#fafaf8');caption(canvas,f'{family} pieces — mark these IDs inside','Viewed from the core side; printing orientations are stored separately in the STL files.')
 for j,row in enumerate(rows):
  n=np.array(row['direction']);q=frame(n).T;name=row['name'];im=mr.render([(name,q,-q@(29*n),COLORS[family])],size=350,extent=27,elev=-35,az=-45)
  x=(j%cols)*360;y=100+(j//cols)*370;canvas.paste(im,(x,y));ImageDraw.Draw(canvas).text((x+15,y+5),name,font=font(24),fill='#233c42')
 canvas.save(DEST/f'images/catalog-{family}.png');print('RENDER catalog',family,flush=True)
