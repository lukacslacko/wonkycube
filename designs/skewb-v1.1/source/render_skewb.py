"""Preview the delivered meshes, with assembly IDs and hardware sections."""
from skewb_design import *
import mesh_render as rr
from PIL import Image,ImageDraw,ImageFont
import sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
OUT=DEST/'images';OUT.mkdir(parents=True,exist_ok=True)
META=json.loads((DEST/'manifest.json').read_text());PARTS={};COLORS={'C':'#9e7cc1','F':'#e6b247','K':'#58a9ac'}
for r in META['parts']:
 if r['name'] not in [row['name'] for row in ROWS]+['core','assembly-stand']:continue
 m=trimesh.load(DEST/r['file'],force='mesh');t=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 PARTS[r['name']]=from_mesh(m);rr.meshes[r['name']]=mesh(PARTS[r['name']].simplify(.02))

def font(size):
 for path in ['/System/Library/Fonts/Helvetica.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
  if Path(path).exists():return ImageFont.truetype(path,size)
 return ImageFont.load_default(size=size)

def label(im,xy,text,size=24,color='#253341'):ImageDraw.Draw(im).text(xy,text,font=font(size),fill=color)
def panels(title,items,notes,path):
 canvas=Image.new('RGB',(1440,870),'#fafaf8');label(canvas,(35,20),title,30)
 for j,(caption,objects,extent) in enumerate(items):
  canvas.paste(rr.render(objects,size=720,extent=extent,elev=27,az=-55),(j*720,95));label(canvas,(j*720+35,70),caption,22)
 label(canvas,(35,825),notes,20);canvas.save(OUT/path)

objects=[];exploded=[]
for row in ROWS:
 name=row['name'];n=np.array(row['direction']);objects.append((name,R.T,np.zeros(3),COLORS[name[0]]));exploded.append((name,R.T,R.T@n*15,COLORS[name[0]]))
for o in [objects,exploded]:o.append(('core',R.T,np.zeros(3),'#aeb9c1'))
panels('Wonky Skewb | 64 mm | printable prototype', [('Solved',objects,49),('Exploded',exploded,70)],'Purple: 4 screwed corners     Gold: 6 face pieces     Teal: 4 floating corners     Gray: core','overview.png')
q=Rotation.from_rotvec(np.pi/3*AXES[3]).as_matrix();turned=[]
for row in ROWS:
 name=row['name'];turned.append((name,R.T@(q if 3 in row['signature'] else np.eye(3)),np.zeros(3),COLORS[name[0]]))
turned.append(('core',R.T,np.zeros(3),'#aeb9c1'))
panels('A Skewb turn carries seven shell pieces', [('Aligned',objects,49),('Halfway through a 120 degree turn',turned,62)],'One screwed corner rotates in place; three face pieces and three floating corners travel with it.','turn.png')

# A labeled exploded view on each side of the cube.
def project(p,size,extent,elev,az):
 el,aa=np.radians([elev,az]);direction=np.array([np.cos(el)*np.cos(aa),np.cos(el)*np.sin(aa),np.sin(el)]);right=rr.normalize(np.cross([0,0,1],direction));up=np.cross(direction,right)
 return np.array([(p@right/extent+1)*size/2,(1-p@up/extent)*size/2])
canvas=Image.new('RGB',(1600,960),'#fafaf8');label(canvas,(35,20),'Solved placement | full IDs | two opposite views',30)
for j,(elev,az) in enumerate([(27,-55),(-27,125)]):
 size=800;extent=74;canvas.paste(rr.render(exploded,size=size,extent=extent,elev=elev,az=az),(j*800,95))
 el,aa=np.radians([elev,az]);view=np.array([np.cos(el)*np.cos(aa),np.cos(el)*np.sin(aa),np.sin(el)]);d=ImageDraw.Draw(canvas)
 for row in ROWS:
  n=np.array(row['direction']);p=R.T@n*(38+15)
  if (R.T@n)@view<-.20:continue
  xy=project(p,size,extent,elev,az)+[j*800,95];label(canvas,tuple(xy-[22,12]),row['name'],22)
 label(canvas,(j*800+35,65),'Front / upper view' if j==0 else 'Opposite / lower view',22)
label(canvas,(35,910),'Use NEIGHBORS.md and the named solved 3MF to resolve the orientation of each piece.',21);canvas.save(OUT/'piece-identification.png')

# Separate families, looking into the retaining feet (radial inward-facing view).
canvas=Image.new('RGB',(1440,690),'#fafaf8');label(canvas,(35,20),'Integral feet and tracks | underside views',30)
for j,name in enumerate(['C01','F01','K01']):
 row=next(r for r in ROWS if r['name']==name);n=np.array(row['direction']);f=frame(n)
 v=rr.meshes[name].vertices@f;center=(v.min(axis=0)+v.max(axis=0))/2;extent=float(np.linalg.norm(v-center,axis=1).max()*1.06)
 ob=[(name,f.T,-center,COLORS[name[0]])]
 canvas.paste(rr.render(ob,size=480,extent=extent,elev=-60,az=-70),(j*480,100));label(canvas,(j*480+30,75),name+' | '+{'C':'screwed corner','F':'face piece','K':'floating corner'}[name[0]],22)
label(canvas,(35,600),'R3 radial ridges continue into the retaining region. Smaller lead-ins soften the rail profile.',21)
label(canvas,(35,640),'No separate internal carriers; the retaining feet are part of the printed shell pieces.',21);canvas.save(OUT/'mechanism.png')

canvas=Image.new('RGB',(1200,720),'#fafaf8');label(canvas,(30,20),'Core axes | C01 is the original print-bed flat',28)
for j,(el,az) in enumerate([(30,-70),(-30,110)]):
 canvas.paste(rr.render([('core',R.T,np.zeros(3),'#aeb9c1')],size=600,extent=26,elev=el,az=az),(j*600,80))
 for i,n in enumerate(AXES):
  ee,aa=np.radians([el,az]);view=np.array([np.cos(ee)*np.cos(aa),np.cos(ee)*np.sin(aa),np.sin(ee)])
  if (R.T@n)@view<0:continue
  xy=project(R.T@n*20,600,26,el,az)+[j*600,80];label(canvas,tuple(xy-[22,12]),f'C{i+1:02}',22)
label(canvas,(30,682),'Match these axes to the solved-piece view. Mark off the small central bearing lands.',20);canvas.save(OUT/'core-identification.png')

# Engineering section: actual core, C01 and conservative hardware envelopes.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
f=frame(AXES[0]);cutframe=np.array([[1,0,0],[0,0,1],[0,-1,0]])
fig,axs=plt.subplots(1,2,figsize=(13,8),gridspec_kw={'width_ratios':[1.15,1]});fig.patch.set_facecolor('#fafaf8')
def section(ax,s,color,name):
 local=xform(s,cutframe@f.T)
 for i,p in enumerate(local.slice(0).to_polygons()):
  ax.fill(p[:,0],p[:,1],facecolor=color,edgecolor='#33404b',lw=.6,label=name if i==0 else None)
section(axs[0],PARTS['core'],'#b6c4cf','Core')
section(axs[0],PARTS['C01'],COLORS['C'],'C01')
section(axs[0],xform(nut_shape(),f),'#667785','M3 nyloc nut (envelope)')
bolt,washer=hardware(AXES[0]);section(axs[0],bolt,'#cdd4d9','M3 x 20 screw (envelope)');section(axs[0],washer,'#e1b95a','9 x 1 washer')
axs[0].set(xlim=(-11,12),ylim=(5,41),xlabel='Across the axis (mm)',ylabel='Distance along screw axis (mm)',title='One screw stack — section')
for z,text in [(8.3,'Screw tip 8.30'),(11.65,'Nut inner face 11.65'),(15.65,'Nut roof 15.65'),(17.6,'Bearing flat 17.60'),(27.3,'Washer seat 27.30')]:
 axs[0].annotate(text,xy=(0,z),xytext=(6,z+(1 if z==17.6 else 0)),fontsize=8,arrowprops=dict(arrowstyle='-',color='#45515b'),va='center')
# Slot cut horizontally at the mid-height of the nut, in its local frame.
pocket=nut_slot();polys=pocket.slice(NUT_ROOF-2).to_polygons()
for p in polys:axs[1].fill(p[:,0],p[:,1],color='#fafaf8',edgecolor='#33404b',lw=1.5)
for p in nut_shape().slice(NUT_ROOF-2).to_polygons():axs[1].plot(*np.vstack([p,p[0]]).T,color='#cb8337',lw=2)
axs[1].set(facecolor='#b6c4cf',xlim=(-4,16),ylim=(-8,8),xlabel='Sideways insertion (mm)',ylabel='Across slot (mm)',title='Nut pocket — horizontal section')
axs[1].annotate('Push nut toward the bore',xy=(2,0),xytext=(9,0),ha='center',fontsize=9,arrowprops=dict(arrowstyle='->',lw=1.4))
axs[1].annotate('5.40 mm terminal seat',xy=(0,2.7),xytext=(-3,5),fontsize=10,arrowprops=dict(arrowstyle='-'))
axs[1].annotate('5.85 mm loading mouth',xy=(11,2.925),xytext=(2,-6),fontsize=10,arrowprops=dict(arrowstyle='-'))
for ax in axs:ax.set_aspect('equal');ax.grid(alpha=.15)
fig.suptitle('Hardware and narrowed nut capture | dimensions in mm',fontsize=16)
fig.text(.07,.05,'Nominal nut: 5.5 mm across flats x 4 mm high. Test coupons with your actual nuts before printing the core.',fontsize=10)
fig.tight_layout(rect=(0,.09,1,.95));fig.savefig(OUT/'hardware.png',dpi=150);plt.close(fig)
print('RENDERED',OUT,flush=True)
