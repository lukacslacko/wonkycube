"""Dimensioned meridian and core-root comparison, generated from the design."""
from redi_design import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
DEST=Path(sys.argv[1]);(DEST/'images').mkdir(exist_ok=True)
fig=plt.figure(figsize=(12.5,7.2),dpi=180,facecolor='#fafaf8')
gs=fig.add_gridspec(1,2,width_ratios=[1.45,1],wspace=.23)
ax=fig.add_subplot(gs[0,0],facecolor='#fafaf8')
old=[]
for a,b in zip(SPEC['profile']['nodes'][:-1],SPEC['profile']['nodes'][1:]):
 c=np.array([a['p'],a['out'],b['in'],b['p']]);t=np.linspace(0,1,500)[:,None]
 old.extend((1-t)**3*c[0]+3*(1-t)**2*t*c[1]+3*(1-t)*t*t*c[2]+t**3*c[3])
old=np.array(old);new=np.array(profile())[:-2]
ax.add_patch(Circle((0,0),32,color='#edf0f0',zorder=0))
ax.plot(old[:,0],old[:,1],'--',color='#a082b0',lw=1.5,label='Saved Bézier profile')
ax.plot(new[:,0],new[:,1],color='#168b88',lw=2.3,label='Printable cut profile')
ax.plot([0,0],[0,43],color='#87979d',lw=1)
ax.annotate('Axially open shoulder\nCaptures a petal radially',xy=(17.65,17),xytext=(22,7),arrowprops=dict(arrowstyle='->',color='#3c515d'),fontsize=10)
ax.annotate('Small local core\nreinforcement',xy=(25.1,19.9),xytext=(32,16),arrowprops=dict(arrowstyle='->',color='#3c515d'),fontsize=10)
ax.set(xlim=(-1,46),ylim=(-1,42),xlabel='Distance from turn axis (mm)',ylabel='Height along turn axis (mm)')
ax.set_aspect('equal');ax.legend(loc='upper left',fontsize=10,frameon=False)
ax.set_title('One cutting body: rotate this curve about the vertical axis',fontsize=12,pad=16)
ax=fig.add_subplot(gs[0,1],facecolor='#fafaf8')
v=np.linspace(-5,5,701);xx,yy=np.meshgrid(v,v);p=np.stack([np.full_like(xx,32),xx,yy],axis=-1);r=np.linalg.norm(p,axis=2)
for fn,col,label in [(outside_theta,'#63b2ab','Reinforced'),(OUTER_THETA,'#a082b0','Original')]:
 threshold=r*np.cos(fn(r));inside=np.min(threshold[:,:,None]-p@AXES.T,axis=2)
 ax.contourf(v,v,inside,levels=[0,100],colors=[col],alpha=.62)
 ax.contour(v,v,inside,levels=[0],colors=[col],linewidths=1.8)
ax.set(xlim=(-5,5),ylim=(-5,5),xlabel='Cross-section coordinate (mm)',ylabel='Cross-section coordinate (mm)')
ax.set_aspect('equal');ax.set_title('One core arm at 32 mm from the puzzle center',fontsize=12,pad=16)
ax.text(-4.7,4.2,'Teal: reinforced     Purple: original',fontsize=10,color='#344d54')
ax.text(-4.7,-4.5,'Ideal cross-sections; print clearance is applied separately.',fontsize=8,color='#52676f')
fig.suptitle('Wavy Redi · hidden retention and stronger core',fontsize=20,x=.055,ha='left',y=.985)
fig.subplots_adjust(left=.065,right=.97,top=.88,bottom=.11)
fig.savefig(DEST/'images/profile-and-core.png',facecolor='#fafaf8');plt.close(fig)
