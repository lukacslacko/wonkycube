"""Show the inner track revision and equal-radius transverse sections."""
from mechanism_v4p2 import *
from build_v4 import load_parts
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Circle
from PIL import Image,ImageDraw,ImageFont
from matplotlib.font_manager import findfont
import mesh_render as renderer
import argparse

def patch(ax,polygons,offset,face,edge,lw=1):
    verts=[];codes=[]
    for poly in polygons:
        p=poly.copy();p[:,0]-=offset
        verts.extend(list(p)+[p[0]]);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(p)-1)+[MPath.CLOSEPOLY])
    ax.add_patch(PathPatch(MPath(verts,codes),facecolor=face,edgecolor=edge,lw=lw))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    old=load_parts(args.base);new=load_parts(args.out);rows=json.loads((args.out/'reference/ridge_sections.json').read_text())
    xs=[r['x_mm'] for r in rows];cy=[r['circle_center_y_mm'] for r in rows]
    fig,axs=plt.subplots(1,4,figsize=(15.2,5.4),dpi=160,sharex=True,sharey=True);fig.patch.set_facecolor('#fafaf8')
    F=np.array([[0,1,0],[0,0,1],[1,0,0]])
    for ax,x,title in zip(axs,[25.5,31,32.5,40],['Inner ridge','Deep track section','Track transition','Outer ridge']):
        center=np.interp(x,xs,cy);ax.set_facecolor('#fafaf8')
        patch(ax,xform(old['E12'],F).slice(x).to_polygons(),center,'#e7ba83','#ad865a',.7)
        patch(ax,xform(new['E12'],F).slice(x).to_polygons(),center,'#94c8b2','#27664f',1)
        ax.add_patch(Circle((0,0),3,fill=False,edgecolor='#47645c',linestyle=(0,(4,4)),lw=.9))
        ax.plot([-3,0],[0,0],color='#254d40',lw=1)
        ax.plot(0,0,'+',color='#254d40');ax.text(-1.6,.17,'R3 mm',ha='center',fontsize=11,color='#254d40')
        ax.set(xlim=(-4.2,3.4),ylim=(-3.5,3.5),aspect='equal',title=title)
        ax.grid(alpha=.13);ax.spines[['top','right']].set_visible(False)
        ax.set_xlabel(f'Radial station {x:g} mm')
    axs[0].set_ylabel('Across ridge (mm)')
    fig.text(.052,.95,'V4.2.1  /  ONE 3 mm RADIUS THROUGH THE TRACKS',fontsize=19,weight='bold',color='#244a3e')
    fig.text(.052,.88,'Green: new piece    •    Orange: removed material    •    Dashed circles: the same 3 mm radius',fontsize=12,color='#52645e')
    fig.text(.052,.035,'Actual E12 mesh sections, centered on each fillet circle. No smaller-radius inner band and no radius taper.',fontsize=11,color='#52645e')
    fig.subplots_adjust(left=.065,right=.985,top=.78,bottom=.15,wspace=.08)
    fig.savefig(args.out/'reference/constant-radius-v4p2.png');fig.savefig(args.out/'reference/constant-radius-v4p2.svg');plt.close(fig)
    svg=args.out/'reference/constant-radius-v4p2.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    renderer.meshes={'old':mesh(old['E12']),'new':mesh(new['E12'])}
    page=Image.new('RGB',(1600,930),'#fafaf8');draw=ImageDraw.Draw(page)
    regular=findfont('DejaVu Sans');bold=findfont('DejaVu Sans:weight=bold')
    def text_at(xy,text,size=24,strong=False):draw.text(xy,text,font=ImageFont.truetype(bold if strong else regular,size),fill='#244a3e')
    text_at((55,25),'Rounding continues through the inner track',36,True)
    text_at((55,88),'Same E12 detail, same scale and camera. The core and corner pieces are reused.',23)
    for i,(name,color,label) in enumerate([('old','#b9bec0','v4.1 · smaller rounding inside'),('new','#94c8b2','v4.2.1 · 3 mm through the track')]):
        im=renderer.render([(name,np.eye(3),np.array([-32,-5,0]),color)],size=760,extent=17,elev=30,az=-65)
        page.paste(im,(20+i*800,135));text_at((55+i*800,147),label,25,True)
    text_at((55,879),'The radial ends of the flanges change too; the remaining retaining lands are checked separately.',22)
    page.save(args.out/'reference/track-detail-v4p2.png')
    print('Drawings saved',flush=True)

if __name__=='__main__':main()
