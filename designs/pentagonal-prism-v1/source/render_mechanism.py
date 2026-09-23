from conical_design import *
from section_connectivity import polygons
import mesh_render as mr
from PIL import Image,ImageDraw,ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());parts={}
for rec in meta['parts']:
 if rec['name'] not in ['core','C01']:continue
 m=trimesh.load(DEST/rec['file'],force='mesh');t=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3];parts[rec['name']]=from_mesh(m);mr.meshes[rec['name']]=m
objects=[('core',R.T,np.zeros(3),'#8b99a2')]
for i,n in enumerate(AXES):
 for label,s,col in zip(['screw','washer'],hardware(n),['#818e97','#d7bb73']):
  name=f'{label}-{i}';mr.meshes[name]=mesh(s);objects.append((name,R.T,np.zeros(3),col))
im=mr.render(objects,size=1100,extent=44,elev=26,az=-48);im.save(DEST/'images/core-and-hardware.png')
f=frame(AXES[0]);rot=Rotation.from_euler('x',90,degrees=True).as_matrix()
fig,ax=plt.subplots(figsize=(9,8),facecolor='#fafaf8');ax.set_facecolor('#fafaf8')
b,w=hardware(AXES[0]);nut=xform(nut_shape(),f)
for s,c,label in [(parts['core'],'#8b99a2','One-piece core'),(parts['C01'],'#83bba1','Screwed center'),(nut,'#6e7c8b','DIN985 nut'),(w,'#d7bb73','Washer'),(b,'#4a5b68','M3×20 screw')]:
 cs=xform(s,rot@f.T).slice(0)
 for p in polygons(cs):
  v=np.asarray(p.exterior.coords).copy();v[:,1]*=-1;ax.add_patch(Polygon(v,facecolor=c,edgecolor='#2f454d',lw=.6))
  for h in p.interiors:
   v=np.asarray(h.coords).copy();v[:,1]*=-1;ax.add_patch(Polygon(v,facecolor='#fafaf8',edgecolor='#2f454d',lw=.6))
 ax.plot([],[],color=c,lw=8,label=label)
ax.set(xlim=(-13,13),ylim=(10,42),aspect='equal',xlabel='Transverse distance (mm)',ylabel='Distance along C01 axis (mm)')
ax.set_title('Actual C01 center and screw stack — through-axis section',fontsize=14,pad=16)
ax.annotate('Flat bearing foot\n0.10 mm axial clearance',xy=(2.5,FOOT_PLANE),xytext=(6,21),arrowprops=dict(arrowstyle='->'),fontsize=10)
ax.annotate('Washer seat\n31.30 mm',xy=(-3.2,SEAT),xytext=(-12,34),arrowprops=dict(arrowstyle='->'),fontsize=10)
ax.annotate('Nylon end inward',xy=(-2.1,NUT_ROOF-3.8),xytext=(-12,11.2),arrowprops=dict(arrowstyle='->'),fontsize=10)
ax.legend(loc='upper left',fontsize=9);fig.tight_layout();fig.savefig(DEST/'images/screw-stack-section.png',dpi=170);plt.close(fig)
