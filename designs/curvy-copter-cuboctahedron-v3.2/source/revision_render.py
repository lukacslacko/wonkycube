"""Exact-STL radial view clarifying the direction of the flange-end rounding."""
from revision_check import *
from ridge_rounding import ridges
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Patch

def draw_polys(ax,ps,color,edge='#31444a',lw=1):
 paths=[MPath(np.vstack([p,p[0]]),[1]+[2]*(len(p)-1)+[79]) for p in ps]
 if paths:ax.add_patch(PathPatch(MPath.make_compound_path(*paths),facecolor=color,edgecolor=edge,lw=lw))

def run():
 _,old=read_base(BASE);_,prev=read_base(ACCEPTED);_,new=read_base(DEST)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':'#24343b'})
 fig,axs=plt.subplots(1,2,figsize=(12,7),facecolor='#fafaf8');fig.subplots_adjust(top=.75,bottom=.19,wspace=.30,left=.08,right=.97)
 fig.suptitle('Rounded flange outline · original bearing rims',fontsize=21,fontweight='bold',y=.96)
 fig.text(.5,.895,'v3.2 · sections taken from the exported STLs',ha='center',fontsize=12)
 ax=axs[0]
 for s,col in [(old['C'],'#d6d8d6'),(new['C'],'#74ad9c')]:draw_polys(ax,s.slice(30.5).to_polygons(),col)
 ax.set(xlim=(-5.5,.5),ylim=(-4.3,4.3),aspect='equal',title='Look inward along a radial direction',xlabel='Across the flange end (mm)',ylabel='Across the flange end (mm)')
 ax.annotate('R1.2 outline fillet',xy=(-2.80,2.47),xytext=(-.2,3.55),ha='right',fontsize=11,arrowprops=dict(arrowstyle='->',color='#24343b'))
 ax.legend(handles=[Patch(facecolor='#d6d8d6',edgecolor='#31444a',label='Original v3 outline'),Patch(facecolor='#74ad9c',edgecolor='#31444a',label='v3.2 outline')],loc='lower center',fontsize=10)
 i,j,R=next(r for r in ridges(canonical('C')) if r[:2]==(1,8));G=np.array([R[0],R[2],np.cross(R[0],R[2])])
 ax=axs[1]
 for s,col in [(new['C'],'#74ad9c'),(prev['C'],'#e5c49b')]:draw_polys(ax,xform(s,G).slice(.01).to_polygons(),col)
 ax.set(xlim=(-3.5,5.5),ylim=(26.5,35.7),aspect='equal',title='Side section through a bearing rim',xlabel='Into the piece (mm)',ylabel='Along this radial edge (mm)')
 ax.legend(handles=[Patch(facecolor='#e5c49b',edgecolor='#31444a',label='v3.1 rounding being undone'),Patch(facecolor='#74ad9c',edgecolor='#31444a',label='Material restored in v3.2')],loc='lower right',fontsize=9)
 for ax in axs:ax.set_facecolor('#fafaf8');ax.grid(alpha=.12);ax.set_axisbelow(True)
 fig.text(.5,.10,'Four outline corners rounded: two at each end. The fillet follows each corner radially through the flange.',ha='center',fontsize=11)
 fig.text(.5,.055,'The accepted v3.1 petals, floating corners, core and hardware remain unchanged.',ha='center',fontsize=11)
 for ext in ['png','svg']:fig.savefig(DEST/f'images/v3.2-flange-outline.{ext}',dpi=180,facecolor=fig.get_facecolor())
 plt.close(fig)
if __name__=='__main__':run()
