"""Render the delivered plastic and the seated foam envelopes."""
from hardware import *
from cutting import instance_inlays,COLORS
import mesh_render as mr
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPoly
from scipy.spatial import ConvexHull

def font(size):
 from matplotlib.font_manager import findfont
 return ImageFont.truetype(findfont('DejaVu Sans'),size)
def title(im,heading,sub=''):
 d=ImageDraw.Draw(im);d.text((35,20),heading,font=font(30),fill='#24343b')
 if sub:d.text((35,65),sub,font=font(17),fill='#58646a')
def render():
 meta=json.loads((DEST/'manifest.json').read_text());base={}
 for rec in meta['parts']:
  if '/puzzle/' not in rec['file']:continue
  m=trimesh.load(DEST/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];base[rec['family']]=m
 mr.meshes['core']=base['core'];objects=[('core',np.eye(3),np.zeros(3),'#555f67')]
 for row in ROWS:
  q=mapping(canonical(row['family'])['signature'],row['signature']);m=base[row['family']].copy();m.vertices=m.vertices@q.T;mr.meshes[row['name']]=m
  objects.append((row['name'],np.eye(3),np.zeros(3),'#323b43'))
  if row['family'] in ['T','S']:
   cap=base[row['family']+'C'].copy();cap.vertices=cap.vertices@q.T;mr.meshes[row['name']+'-cap']=cap
   objects.append((row['name']+'-cap',np.eye(3),np.zeros(3),'#323b43'))
 hw=[]
 for a in range(14):
  for label,s in zip(['screw','washer','nut'],hardware(a)):
   key=f'{label}{a}';mr.meshes[key]=mesh(s)
   if label!='nut':hw.append((key,np.eye(3),np.zeros(3),'#b5bbc0'))
 items=instance_inlays();foam=[]
 for k,item in enumerate(items):
  key=f'inlay{k}';mr.meshes[key]=mesh(item['solid']);item['render_key']=key;foam.append((key,np.eye(3),np.zeros(3),COLORS[item['face_index']]))
 canvas=Image.new('RGB',(1700,970),'#fafaf8');title(canvas,'Vertex-turning rhombic dodecahedron','76 mm between opposite faces · central keyed screw plugs · 2 mm foam inlays · actual generated geometry')
 for j,(el,az) in enumerate([(24,-57),(-24,123)]):canvas.paste(mr.render(objects+foam+hw,size=850,extent=59,elev=el,az=az),(850*j,110))
 canvas.save(DEST/'images/solved-two-sides.png');print('RENDER solved',flush=True)
 canvas=Image.new('RGB',(1600,620),'#fafaf8');title(canvas,'Printable parts','Threefold centers × 8 · fourfold centers × 6 · floating petals × 24 · reusable core × 1')
 for j,f in enumerate(['T','S','P','core']):
  key=canonical(f)['name'] if f!='core' else 'core';q=frame(canonical(f)['direction']).T if f!='core' else np.eye(3)
  v=mr.meshes[key].vertices@q.T;mid=(v.max(0)+v.min(0))/2
  canvas.paste(mr.render([(key,q,-mid,['#83b6a5','#e2bf72','#80acc9','#88969c'][j])],size=400,extent=27,elev=-28,az=-48),(400*j,130))
 canvas.save(DEST/'images/parts.png');print('RENDER parts',flush=True)
 canvas=Image.new('RGB',(1600,940),'#fafaf8');title(canvas,'Simple central plugs cover the screws','Outer rims and most foam backing stay on the screwed pieces. Foam omitted to show the joints.')
 for j,f in enumerate(['T','S']):
  row=canonical(f);key=row['name'];q=frame(row['direction']).T;mid=np.array([0.,0,40. if f=='T' else 44.])
  scene=[(key,q,-mid,'#b7c4cc'),(key+'-cap',q,-mid+[0,0,13],'#3e515d')]
  for label in ['screw','washer']:
   scene.append((label+str(row['signature'][0]),q,-mid,'#a4a9ae'))
  canvas.paste(mr.render(scene,size=800,extent=36,elev=28,az=-55),(j*800,120))
  ImageDraw.Draw(canvas).text((j*800+45,100),'Three-way plug × 8' if f=='T' else 'Four-way plug × 6',font=font(24),fill='#24343b')
 canvas.save(DEST/'images/exploded-plugs.png');print('RENDER plugs',flush=True)
 canvas=Image.new('RGB',(1400,800),'#fafaf8');title(canvas,'Compact keyed plugs','Rounded triangle / rounded square · flat print bases · shallow friction ribs')
 for j,f in enumerate(['T','S']):
  row=canonical(f);key=row['name']+'-cap';q=frame(row['direction']).T;v=mr.meshes[key].vertices@q.T;mid=(v.min(0)+v.max(0))/2
  canvas.paste(mr.render([(key,q,-mid,'#86aeb5')],size=700,extent=12,elev=-32,az=-55),(j*700,100))
 canvas.save(DEST/'images/plug-keys.png')
 canvas=Image.new('RGB',(1600,940),'#fafaf8');title(canvas,'Foam spans the main piece and the central plug','Foam is lifted off the pockets here. Glue after adjusting the puzzle; remove foam to service a screw.')
 for j,f in enumerate(['T','S']):
  row=canonical(f);key=row['name'];q=frame(row['direction']).T;mid=np.array([0.,0,38. if f=='T' else 41.])
  scene=[(key,q,-mid,'#b7c4cc'),(key+'-cap',q,-mid,'#376b78')]
  for item in items:
   if item['piece']==key:
    normal=FACES[item['face_index']][0];scene.append((item['render_key'],q,-mid+q@normal*6,COLORS[item['face_index']]))
  canvas.paste(mr.render(scene,size=800,extent=33,elev=40,az=-55),(j*800,120))
 canvas.save(DEST/'images/foam-overlap.png');print('RENDER shared foam floors',flush=True)
 row=canonical('P');key=row['name'];q=frame(row['direction']).T;v=mr.meshes[key].vertices@q.T;mid=(v.max(0)+v.min(0))/2
 sample=[(key,q,-mid,'#475866')]
 for item in items:
  if item['piece']==key:
   n=FACES[item['face_index']][0];sample.append((item['render_key'],q,-mid+q@n*6,COLORS[item['face_index']]))
 canvas=Image.new('RGB',(1500,750),'#fafaf8');title(canvas,'Foam rests in a shallow pocket','Continuous perimeter walls · no fragile snap hooks · 0.1 mm allowance beneath a 2 mm inlay')
 canvas.paste(mr.render(sample,size=650,extent=23,elev=38,az=-55),(0,100))
 d=ImageDraw.Draw(canvas);x,y=770,340;s=75
 d.rectangle((x,y,x+520,y+270),fill='#475866');d.rectangle((x+45,y,x+475,y+2.1*s),fill='#fafaf8');d.rectangle((x+45,y+.1*s,x+475,y+2.1*s),fill='#30b4c5')
 d.text((x+130,y+80),'2.0 mm foam',font=font(25),fill='#18353a');d.text((x,y-60),'Pocket depth 2.10 mm',font=font(23),fill='#24343b')
 d.text((x,y+300),'Thin glue film; foam stays flush or recessed.',font=font(18),fill='#58646a')
 canvas.save(DEST/'images/inlay-detail.png');print('RENDER inlay detail',flush=True)
 fig,axes=plt.subplots(3,4,figsize=(15,12),facecolor='#fafaf8');v=mesh(outer()).vertices
 for i,(ax,(normal,h,label)) in enumerate(zip(axes.flat,FACES)):
  F=frame(normal);points=v[abs(v@normal-h)<1e-5]@F[:,:2];points=points[ConvexHull(points).vertices]
  ax.add_patch(PlotPoly(points,facecolor='#343e46',edgecolor='#343e46'))
  for item in items:
   if item['face']!=label:continue
   p=item['polygon'];ax.add_patch(PlotPoly(np.array(p.exterior.coords),facecolor=COLORS[i],edgecolor='none'));center=p.representative_point();ax.text(center.x,center.y,item['piece'],ha='center',va='center',fontsize=8,color='#18212a')
  ax.set(xlim=(-41,41),ylim=(-41,41),aspect='equal',title=label+'   '+str(tuple(int(v) for v in np.rint(normal*np.sqrt(2)))));ax.axis('off')
 fig.suptitle('Twelve face inlay sheets — viewed from outside\nCut each F01–F12 sheet once, one color per face. Labels are on this map only.',fontsize=16)
 fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(DEST/'images/inlay-face-map.png',dpi=160);fig.savefig(DEST/'images/inlay-face-map.svg');plt.close(fig);print('RENDER map',flush=True)
 from print_3mf import save_3mf
 save_3mf(DEST/'reference/DO-NOT-PRINT-with-inlays.3mf',[(name,mr.meshes[name],[0,0,0]) for name,_,_,_ in objects+foam])
if __name__=='__main__':render()
