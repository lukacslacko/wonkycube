from hardware import *
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as PlotPath
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))

def draw_sections(ax,cells):
 a,b=AXES[canonical('P')['signature']];up=(a+b)/np.linalg.norm(a+b);right=(a-b)/np.linalg.norm(a-b);F=np.array([right,up,np.cross(right,up)]);colors={'C':'#74ad9c','P':'#73a6ca','K':'#e7bd69'}
 for name,s in cells.items():
  polys=xform(s,F).slice(.01).to_polygons()
  if not polys:continue
  paths=[]
  for p in polys:
   paths.append(PlotPath(np.vstack([p,p[0]]),[1]+[2]*(len(p)-1)+[79]))
  ax.add_patch(PathPatch(PlotPath.make_compound_path(*paths),facecolor=colors[name[0]],edgecolor='#31444a',lw=.6))
 ax.set(xlim=(-14,14),ylim=(18,39),aspect='equal');ax.grid(alpha=.15);ax.set_xlabel('Across the petal (mm)');ax.set_ylabel('Outward from puzzle center (mm)')

def run():
 old=Path(os.environ.get('CUBOCTA_V1_REFERENCE','outputs/natural-cuboctahedron-45deg-64mm-v1'));groups=[]
 for folder in [old,DEST]:
  meta=json.loads((folder/'manifest.json').read_text());cells={}
  for r in meta['parts']:
   if '/puzzle/' not in r['file'] or r['family']=='core':continue
   m=trimesh.load(folder/r['file'],force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];cells.update(replicate(from_mesh(m),r['family']))
  groups.append(cells)
 fig,ax=plt.subplots(1,2,figsize=(11,6.3),facecolor='#fafaf8')
 for a,c,title in zip(ax,groups,['Failed 64 mm version','Revised 72 mm prototype']):draw_sections(a,c);a.set_title(title,fontsize=14)
 fig.suptitle('Actual exported pieces · section through one petal and its two anchors',fontsize=15)
 fig.text(.5,.025,'Green = screwed centers   ·   Blue = floating petal   ·   Section coordinates use the same scale.',ha='center',fontsize=10)
 fig.tight_layout(rect=[0,.04,1,.93]);fig.savefig(DEST/'images/retention-section-comparison.png',dpi=170);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,7),facecolor='#fafaf8');p=np.array(profile()[:4]+[[32,32]])
 ax.plot([0,33],[0,33],'--',color='#899ca3',label='45° exterior cut');ax.plot(p[:,0],p[:,1],color='#258972',lw=3,label='New internal profile')
 ax.annotate('4.9 mm cylindrical capture band',xy=(19.5,22.3),xytext=(3,29),arrowprops=dict(arrowstyle='->'),fontsize=11)
 ax.annotate('Returns to exterior cut inside the shell',xy=(25.2,25.2),xytext=(15,5),arrowprops=dict(arrowstyle='->'),fontsize=10)
 ax.set(xlim=(0,34),ylim=(0,34),aspect='equal',xlabel='Distance from turn axis (mm)',ylabel='Height along turn axis (mm)',title='Revolve this boundary about the vertical axis');ax.grid(alpha=.2);ax.legend(loc='upper left');fig.tight_layout();fig.savefig(DEST/'images/retaining-profile.png',dpi=160)
 print('COMPARISON COMPLETE',flush=True)
if __name__=='__main__':run()
