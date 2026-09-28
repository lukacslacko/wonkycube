from hardware import *
import mesh_render as mr
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPoly
from shapely.geometry import Polygon
from shapely.ops import unary_union
# DEST is defined by design.py
def font(size):
 from matplotlib.font_manager import findfont
 return ImageFont.truetype(findfont('DejaVu Sans'),size)
def title(im,heading,sub=''):
 d=ImageDraw.Draw(im);d.text((35,20),heading,font=font(30),fill='#24343b')
 if sub:d.text((35,62),sub,font=font(18),fill='#58646a')
def render(maps_only=False):
 meta=json.loads((DEST/'manifest.json').read_text());base={}
 for row in meta['parts']:
  if '/puzzle/' not in row['file']:continue
  m=trimesh.load(DEST/row['file'],force='mesh');T=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];base[row['family']]=m
 mr.meshes['core']=base['core'];colors={'T':'#83b6a5','S':'#e2bf72','P':'#80acc9','core':'#7b8791'}
 for row in ROWS:
  m=base[row['family']].copy();q=mapping(canonical(row['family'])['signature'],row['signature']);m.vertices=m.vertices@q.T;mr.meshes[row['name']]=m
 for a,n in enumerate(AXES):
  for label,s in zip(['screw','washer','nut'],hardware(a)):mr.meshes[f'{label}{a}']=mesh(s)
 def objects(families='TSP',colored=True,explode=0):
  return [(r['name'],np.eye(3),np.array(r['direction'])*explode,colors[r['family']] if colored else '#efeee9') for r in ROWS if r['family'] in families]+[('core',np.eye(3),np.zeros(3),colors['core'])]
 hw=[(f'{label}{a}',np.eye(3),np.zeros(3),'#b5bbc0') for a in range(14) for label in ['screw','washer']]
 if maps_only:painting_map();return
 canvas=Image.new('RGB',(1600,900),'#fafaf8');title(canvas,'Face-turning cuboctahedron · single cut','64 mm between square faces · 8 triangle centers + 6 square centers + 24 petals')
 for j,(el,az) in enumerate([(28,-55),(-28,125)]):canvas.paste(mr.render(objects(colored=False)+hw,size=800,extent=49,elev=el,az=az),(800*j,100))
 canvas.save(DEST/'images/solved-two-sides.png');print('RENDER solved',flush=True)
 canvas=Image.new('RGB',(1600,560),'#fafaf8');title(canvas,'Three piece types and a one-piece core','Green: triangle center × 8 · gold: square center × 6 · blue: petal × 24 · grey: core × 1')
 for j,f in enumerate(['T','S','P','core']):
  name=canonical(f)['name'] if f!='core' else 'core';m=mr.meshes[name];q=frame(canonical(f)['direction']).T if f!='core' else np.eye(3);v=m.vertices@q.T;mid=(v.max(0)+v.min(0))/2
  im=mr.render([(name,q,-mid,colors[f])],size=400,extent=25,elev=-30,az=-45);canvas.paste(im,(400*j,130))
 canvas.save(DEST/'images/internal-pieces.png');print('RENDER internals',flush=True)
 canvas=Image.new('RGB',(1500,620),'#fafaf8');title(canvas,'Assembly: petals → triangle centers → square centers','Temporary tape or a soft elastic band can hold the incomplete shell while you add its retainers.')
 for j,(fs,text) in enumerate([('P','1 · Place twenty-four petals'),('PT','2 · Add eight triangle centers'),('PTS','3 · Add six square centers')]):
  canvas.paste(mr.render(objects(fs),size=500,extent=48,elev=28,az=-55),(j*500,110));ImageDraw.Draw(canvas).text((j*500+20,95),text,font=font(17),fill='#24343b')
 canvas.save(DEST/'images/assembly.png');print('RENDER assembly',flush=True)
 painting_map();profile_plot()
def painting_map():
 # Orthogonal views of every painting facet, using the flat triangles from
 # the delivered meshes. Labels identify pieces and face directions.
 faces=[(np.eye(3)[k]*sgn,32.,f'S{"XYZ"[k]}{"+" if sgn>0 else "-"}') for k in range(3) for sgn in [-1,1]]
 faces += [(np.array(v)/np.sqrt(3),64/np.sqrt(3),'T'+''.join('+' if k>0 else '-' for k in v)) for v in itertools.product([-1,1],repeat=3)]
 fig,axs=plt.subplots(4,4,figsize=(16,16),facecolor='#fafaf8');face_records=[]
 for ax,(normal,h,label) in zip(axs.flat,faces):
  F=frame(normal);seen=[]
  for row in ROWS:
   m=mr.meshes[row['name']];mask=(np.max(abs(m.triangles@normal-h),axis=1)<.025)&(m.face_normals@normal>.9999)
   tris=m.triangles[mask]@F[:,:2]
   if not len(tris):continue
   # Close micron-scale triangulation slits before drawing the facet.
   patches=unary_union([Polygon(t).buffer(.002,join_style=2) for t in tris]).buffer(-.002,join_style=2)
   patches=list(patches.geoms) if patches.geom_type=='MultiPolygon' else [patches]
   patches=[pg for pg in patches if pg.area>1]
   for pg in patches:
    ax.add_patch(PlotPoly(np.array(pg.exterior.coords),facecolor='#e5e6df',edgecolor='#40515b',lw=.6))
    # Petal/corner outer facets have no intended holes. Tiny closed loops
    # in their planar extraction are triangulation/normal artifacts.
    for hole in (pg.interiors if row['family']!='P' else []):ax.add_patch(PlotPoly(np.array(hole.coords),facecolor='#fafaf8',edgecolor='#40515b',lw=.5))
   if patches:
    rp=max(patches,key=lambda p:p.area).representative_point();ax.text(rp.x,rp.y,row['name'],ha='center',va='center',fontsize=7);seen.append(row['name'])
  ax.set(xlim=(-32,32),ylim=(-32,32),aspect='equal',title=label);ax.axis('off');face_records.append(dict(face=label,normal=normal.tolist(),pieces=sorted(set(seen))))
 for ax in list(axs.flat)[14:]:ax.axis('off')
 fig.suptitle('Painting / assembly map — six squares and eight triangles\nGive each face its own color or color-and-symbol combination; leave moving surfaces unpainted.',fontsize=17)
 fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(DEST/'images/painting-map.png',dpi=160);fig.savefig(DEST/'images/painting-map.svg');plt.close(fig)
 (DEST/'reference/faces.json').write_text(json.dumps(face_records,indent=2)+'\n');print('RENDER painting map',flush=True)
def profile_plot():
 fig,axs=plt.subplots(1,2,figsize=(12,6),facecolor='#fafaf8')
 for ax,f in zip(axs,['T','S']):
  pts=np.array(profile(f)[:6]);angle=ANGLES[0] if f=='T' else 45
  ax.set_facecolor('#fafaf8');z=np.array([0.,40.]);ax.plot(z*np.tan(np.radians(angle)),z,'--',color='#839098',label=f'{angle:.3f}° exterior')
  ax.plot(pts[:,0],pts[:,1],color='#177d71',lw=2.5,label='Internal retaining profile')
  ax.set(xlim=(7,26),ylim=(16,32),aspect='equal',xlabel='Distance from axis, rho (mm)',ylabel='Height along axis, z (mm)',title='Triangle axis' if f=='T' else 'Square axis')
  ax.grid(alpha=.18);ax.legend(loc='upper left',fontsize=8)
 fig.suptitle('Positive shoulders with enlarged tracks; exterior cone angles preserved',fontsize=14)
 fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(DEST/'images/retaining-profiles.png',dpi=160);plt.close(fig)
if __name__=='__main__':render()
