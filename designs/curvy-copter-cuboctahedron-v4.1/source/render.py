"""Preview the reloaded printable meshes and face-mapped paper outlines."""
from cutting import *
import mesh_render as mr
from hardware import hardware
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def image_panel(images,labels,path,subtitles=None):
 w=sum(i.width for i in images);h=max(i.height for i in images)+106;out=Image.new('RGB',(w,h),'#fafaf8');draw=ImageDraw.Draw(out)
 try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',28);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
 except OSError:font=small=ImageFont.load_default()
 x=0
 for k,(im,label) in enumerate(zip(images,labels)):
  out.paste(im,(x,80));draw.text((x+28,18),label,fill='#202830',font=font)
  if subtitles:draw.text((x+28,54),subtitles[k],fill='#59646b',font=small)
  x+=im.width
 out.save(path)
def run():
 records=json.loads((CACHE/'inlays.json').read_text())['records'];parts={f:load(CACHE/f'printed-{f}.npz') for f in ORBITS+['cap','core']};objects=[]
 for f,s in parts.items():mr.meshes[f]=mesh(s)
 for rec in records:mr.meshes[rec['id']]=mesh(fitted(rec))
 for row in ROWS:
  q=mapping(canonical(row['family'])['signature'],row['signature']);objects.append((row['family'],q,np.zeros(3),'#303c46'))
  if row['family']=='C':objects.append(('cap',q,np.zeros(3),'#303c46'))
  for rec in records:
   if rec['family']!=row['family']:continue
   n=q@np.array(rec['frame'])[:,2];i=int(np.argmax([n@nn for nn,h,label in FACES]));objects.append((rec['id'],q,np.zeros(3),COLORS[i]))
 a=mr.render(objects,size=1000,extent=58,elev=24,az=-48);b=mr.render(objects,size=1000,extent=58,elev=20,az=132)
 image_panel([a,b],['Curvy Copter · paper inlays','Opposite view'],DEST/'images/assembled.png',['72 mm · 0.5 mm pockets · spherical retention','Square and triangular faces both covered'])
 n=np.array(canonical('C')['direction']);q=frame(n).T;shift=np.array([0,0,-36.]);local=[('C',q,shift,'#667b8d'),('cap',q,shift,'#dfaa4d')]
 for rec in records:
  if rec['family']=='C':local.append((rec['id'],q,shift,'#eeeeea' if rec['canonical_face'].startswith('S') else '#87c8d6'))
 a=mr.render(local,size=850,extent=24,elev=32,az=-55)
 hw=union(hardware(n)[:2]);mr.meshes['hardware']=mesh(hw)
 exploded=[('C',q,shift,'#667b8d'),('cap',q,shift+np.array([0,0,13]),'#dfaa4d'),('hardware',q,shift,'#bfc3c5')]
 b=mr.render(exploded,size=850,extent=32,elev=25,az=-55)
 image_panel([a,b],['Paper spans the plug joint','Small central keyed plug'],DEST/'images/plug-detail.png',['Four continuous inlays; perimeter stays on the main part','Paper removed here · 180° key · 3 mm above screw head'])
 # Labelled face maps are separate from cut-only cutter files.
 items=instance_inlays();fig,axs=plt.subplots(3,5,figsize=(16,10));fig.patch.set_facecolor('#fafaf8')
 for i,ax in enumerate(axs.flat):
  if i>=len(FACES):ax.axis('off');continue
  n,h,label=FACES[i];ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-40,40);ax.set_ylim(-40,40);ax.set_title(label,color='#26343e')
  for item in items:
   if item['face']!=label:continue
   p=item['polygon'];v=np.array(p.exterior.coords);ax.fill(v[:,0],v[:,1],color=COLORS[i],ec='#293641',lw=.6)
   pt=p.representative_point();ax.text(pt.x,pt.y,item['piece'],ha='center',va='center',fontsize=7)
 fig.suptitle('Face map · viewed from outside · labels are not cutting paths',fontsize=17);fig.tight_layout(rect=[0,0,.99,.95]);fig.savefig(DEST/'images/face-map.png',dpi=170);fig.savefig(DEST/'images/face-map.svg');plt.close(fig)
 # Dimensioned section near a face: top rim and pocket floor are parallel.
 fig,ax=plt.subplots(figsize=(9,3.2));ax.fill([0,0,2,2,12,12,14,14],[0,2,2,1.5,1.5,2,2,0],color='#667b8d');ax.fill([2.04,11.96,11.96,2.04],[1.5,1.5,2,2],color='#f4d44f',alpha=.7)
 ax.annotate('',(15,1.5),(15,2),arrowprops=dict(arrowstyle='<->',color='#25313b'));ax.text(15.25,1.65,'0.5 mm pocket',va='center',fontsize=11);ax.text(7,.55,'Continuous plastic floor',ha='center',fontsize=11,color='white');ax.text(7,2.3,'Laminate + adhesive: maximum 0.5 mm total',ha='center',fontsize=11)
 ax.set_xlim(-1,21);ax.set_ylim(-.3,3);ax.axis('off');fig.tight_layout();fig.savefig(DEST/'images/pocket-section.png',dpi=170);plt.close(fig)
 print('RENDERS COMPLETE',flush=True)
if __name__=='__main__':run()
