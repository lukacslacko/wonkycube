"""CAD-derived sections of the delivered spherical-shell alternative."""
from retention_v2 import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Patch
COLORS={'C':'#74ad9c','P':'#73a6ca','K':'#e7bd69','c':'#84939d'}
def paint(ax,cells,F):
 for name,s in cells.items():
  ps=xform(s,F).slice(.01).to_polygons()
  paths=[MPath(np.vstack([p,p[0]]),[1]+[2]*(len(p)-1)+[79]) for p in ps]
  if paths:ax.add_patch(PathPatch(MPath.make_compound_path(*paths),facecolor=COLORS[name[0]],edgecolor='#31444a',lw=.75))
 ax.set_aspect('equal');ax.set_facecolor('#fafaf8');ax.grid(alpha=.12);ax.set_axisbelow(True)
def run():
 cells,c=load_parts();cells['core']=c
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#24343b','axes.labelcolor':'#53636d','xtick.color':'#53636d','ytick.color':'#53636d'})
 fig,axs=plt.subplots(1,2,figsize=(13,7.7),facecolor='#fafaf8');fig.subplots_adjust(top=.82,bottom=.18,wspace=.22,left=.065,right=.98)
 fig.suptitle('Spherical-shell retention · 72 mm · v3.2',fontsize=21,fontweight='bold',y=.97)
 fig.text(.5,.917,'Exact sections of the rounded, exported parts · shoulders follow spheres centered on the puzzle',ha='center',fontsize=12)
 for ax,f,title in zip(axs,['P','K'],['Petal captured by screwed centers','Corner captured by petals']):
  up=np.array(canonical(f)['direction'])
  if f=='P':
   a,b=AXES[canonical(f)['signature']];right=(a-b)/np.linalg.norm(a-b)
  else:
   p=np.array(canonical('P')['direction']);right=p-up*np.dot(up,p);right/=np.linalg.norm(right)
  F=np.array([right,up,np.cross(right,up)]);paint(ax,cells,F)
  ax.set(xlim=(-14,14),ylim=(18.5,44),xlabel='Across section (mm)',ylabel='Outward from puzzle center (mm)');ax.set_title(title,fontsize=14,pad=12)
  for radius in [SHOULDER_R,COLLAR_OUTER_R]:
   x=np.linspace(-14,14,301);ax.plot(x,np.sqrt(radius**2-x*x),':',color='#715342',lw=1.15,alpha=.85)
  ax.text(0,39.5,'Petal' if f=='P' else 'Corner',ha='center',fontsize=13)
 fig.legend(handles=[Patch(facecolor=COLORS[f],edgecolor='#31444a',label=t) for f,t in [('C','Screwed centers'),('P','Petals'),('K','Corners'),('c','Core')]],loc='lower center',bbox_to_anchor=(.5,.085),ncol=4,frameon=False)
 fig.text(.5,.06,'Dotted arcs: R28.5 and R33.5. Nominal bearing gaps: 0.43 mm petal–center; 0.33 mm corner–petal.',ha='center',fontsize=10)
 fig.text(.5,.025,'Shoulders are preserved without insertion relief. Turning and retention are checked separately from assembly.',ha='center',fontsize=10,color='#53636d')
 for ext in ['png','svg']:fig.savefig(DEST/f'images/spherical-retention-sections.{ext}',dpi=180,facecolor=fig.get_facecolor())
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(7.5,7),facecolor='#fafaf8')
 # Include all finite shoulder samples; omit the three closure vertices.
 p=np.array(profile()[:-3]+[[38,38]])
 ax.plot(p[:,0],p[:,1],lw=3,color='#258972');ax.plot([0,38],[0,38],'--',color='#93a2a6',label='45° exterior cone')
 for r in [SHOULDER_R,COLLAR_OUTER_R]:
  theta=np.linspace(0,np.pi/2,250);ax.plot(r*np.sin(theta),r*np.cos(theta),':',lw=1,color='#715342')
 ax.set(xlim=(0,38),ylim=(0,40),aspect='equal',xlabel='Distance from a turn axis (mm)',ylabel='Height along that axis (mm)',title='Revolve this profile about the vertical axis')
 ax.annotate('Spherical step at R28.5',xy=(18.9,21.3),xytext=(1,30),arrowprops=dict(arrowstyle='->'),fontsize=11)
 ax.annotate('Spherical return at R33.5',xy=(22.4,24.9),xytext=(13,36),arrowprops=dict(arrowstyle='->'),fontsize=11)
 ax.grid(alpha=.15);ax.legend(loc='lower right');fig.tight_layout();fig.savefig(DEST/'images/spherical-profile.png',dpi=180);plt.close(fig)
if __name__=='__main__':run()
