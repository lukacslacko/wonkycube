"""Section through both retaining interfaces, from generated part geometry."""
from design import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Arc

def run(stage='printed'):
 cells=get(stage);r=canonical('P');d=np.array(r['direction']);a=AXES[r['signature'][0]];u=a-(a@d)*d;u/=np.linalg.norm(u);F=np.column_stack([u,d,np.cross(u,d)])
 names=[canonical('T')['name'],canonical('S')['name'],r['name']];colors=['#69a992','#ddb159','#629ec7']
 fig,axes=plt.subplots(1,2,figsize=(14,7),facecolor='#fafaf8')
 for ax in axes:
  for name,color in zip(names,colors):
   for pg in xform(cells[name],F.T).slice(0).to_polygons():ax.add_patch(Polygon(pg,facecolor=color,edgecolor='#37444a',lw=.45))
  for rr in [SHOULDER_R,COLLAR_OUTER_R]:
   theta=np.linspace(np.pi/6,5*np.pi/6,240);ax.plot(rr*np.cos(theta),rr*np.sin(theta),color='#56616a',lw=.7,ls='--',alpha=.7)
  ax.set_aspect('equal');ax.spines[['top','right']].set_visible(False);ax.set_xlabel('Across the petal, mm');ax.set_ylabel('Outward from puzzle center, mm')
 axes[0].set(xlim=(-31,31),ylim=(14,51),title='Petal and screwed centers (plugs / hardware omitted)')
 axes[0].text(-29,16,'Green: threefold center\nGold: fourfold center\nBlue: floating petal',fontsize=10,bbox=dict(fc='#fafaf8',ec='none',alpha=.9))
 axes[1].set(xlim=(-15,15),ylim=(24,37),title='Spherical shoulders and the matching groove')
 axes[1].text(-14,35.7,'Nominal shells R28.5 / R33.5\n0.43 mm clearance at each bearing face',fontsize=10,bbox=dict(fc='#fafaf8',ec='none',alpha=.95))
 for x in [-2,8]:
  y=np.sqrt((SHOULDER_R+BODY_GAP/2+TRACK_EXTRA)**2-x*x);start=np.array([x,y]);out=start/np.linalg.norm(start)*2
  axes[1].annotate('',xy=start+out,xytext=start,arrowprops=dict(arrowstyle='->',color='#be4141',lw=1.5))
 axes[1].text(-14,24.6,'Red arrows: local radius / holding-face normal',color='#a33434',fontsize=9)
 fig.suptitle('Concentric spherical-shell retention — actual mesh cross-sections',fontsize=17)
 fig.tight_layout(rect=[0,0,1,.94]);folder=DEST/'images';folder.mkdir(parents=True,exist_ok=True);fig.savefig(folder/'spherical-retention.png',dpi=160);plt.close(fig)
if __name__=='__main__':
 import sys
 run(sys.argv[1] if len(sys.argv)>1 else 'printed')
