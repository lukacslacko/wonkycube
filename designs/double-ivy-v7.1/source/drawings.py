"""Actual exported meshes: assembled overview, section, and assembly groups."""
from design import *
import mesh_render as mr
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from matplotlib.font_manager import findfont
COLORS={'C':'#80b29c','W':'#80acd1','E':'#e4b96c','F':'#c490bb','core':'#899198'}
folder=DEST/'images';folder.mkdir(parents=True,exist_ok=True)
cells={r['name']:load(CACHE/'printed'/(r['name']+'.npz')) for r in ROWS};cells['core']=load(CACHE/'printed/core.npz')
for k,s in cells.items():mr.meshes[k]=mesh(s)
font=lambda n:ImageFont.truetype(findfont('DejaVu Sans'),n)
color=lambda k:COLORS.get(k[0],COLORS['core'])
def canvas(w,h,title,sub):
 im=Image.new('RGB',(w,h),'#fafaf8');d=ImageDraw.Draw(im);d.text((35,25),title,font=font(32),fill='#263844');d.text((35,72),sub,font=font(19),fill='#536570');return im,d
im,d=canvas(1600,990,'Double-cut Ivy · 72 mm · four ordered retaining layers','4 screwed centers  /  12 wings  /  6 edges  /  4 floating centers  /  original one-piece core')
objs=[(name,R.T,np.zeros(3),color(name)) for name in cells]
for i,az in enumerate([-50,130]):im.paste(mr.render(objs,size=760,extent=57,elev=25 if i==0 else -25,az=az),(20+800*i,110))
for i,(label,c) in enumerate([('C: screwed centers',COLORS['C']),('W: wings',COLORS['W']),('E: edges',COLORS['E']),('F: floating centers',COLORS['F'])]):
 x=35+390*i;d.rectangle((x,916,x+20,936),fill=c);d.text((x+30,912),label,font=font(21),fill='#263844')
im.save(folder/'overview.png')
# True sections. Right hand C-W-E chain and left E-F interface are visible.
u=np.array([-1.,0,0]);v=np.array([0.,1,-1]);v/=np.linalg.norm(v);f=np.array([u,v,np.cross(u,v)])
fig,axes=plt.subplots(1,3,figsize=(17,7),gridspec_kw={'width_ratios':[1.35,1,1]},facecolor='#fafaf8')
for ax in axes:
 ax.set_facecolor('#fafaf8')
 for name,s in cells.items():
  ps=xform(s,f).slice(.02).to_polygons();paths=[MPath(np.vstack([p,p[0]]),[1]+[2]*(len(p)-1)+[79]) for p in ps]
  if paths:ax.add_patch(PathPatch(MPath.make_compound_path(*paths),facecolor=color(name),ec='#33434a',lw=.5))
 for rad in [19.2,22.4,25.55,28.8,31.2]:
  ax.add_patch(plt.Circle((0,0),rad,fill=False,color='#54616b',lw=.5,ls='--',alpha=.4))
 ax.set_aspect('equal');ax.grid(alpha=.10);ax.set_xlabel('mm')
axes[0].set(xlim=(-55,55),ylim=(-55,55),title='Section through the reused core')
axes[1].set(xlim=(18,37),ylim=(-2,21),title='C holds W; W holds E')
axes[2].set(xlim=(-26,-9),ylim=(6,24),title='E holds F')
fig.suptitle('Floating-center feet → edge feet → wing feet → screwed-center flanges',fontsize=18,y=.98)
fig.text(.5,.03,'Green C   ·   Blue W   ·   Gold E   ·   Purple F   ·   Gray core   |   Section of the exported STLs; dashed arcs share the puzzle center.',ha='center',fontsize=11)
fig.subplots_adjust(top=.9,bottom=.14,wspace=.22);fig.savefig(folder/'retaining-sections.png',dpi=150);plt.close(fig)
# Internals: each canonical family viewed from its inward side.
im,d=canvas(1600,1120,'The replacement pieces','Four flange levels; C stems and non-retaining E/W bearing webs reach the unchanged core')
for j,fam in enumerate('CWEF'):
 row=canonical(fam);name=row['name'];q=frame(row['direction']).T;m=mr.meshes[name];vv=m.vertices@q.T;mid=(vv.max(0)+vv.min(0))/2
 view=mr.render([(name,q,-mid,color(name))],size=450,extent=34,elev=-27,az=-40)
 # Larger panels are resized equally, not geometry.
 x=20+800*(j%2);y=110+500*(j//2);im.paste(view,(x+170,y+25))
 d.text((x+35,y+12),f'{name} · '+{'C':'screwed center','W':'wing','E':'edge','F':'floating center'}[fam],font=font(24),fill='#263844')
im.save(folder/'pieces.png')
# Four real mesh cutaways show the requested assembly hierarchy.
im,d=canvas(1600,1160,'Build from the innermost feet outward','1. Floating centers   →   2. Edges   →   3. Wings   →   4. Screwed centers')
el,az=np.radians([25,-50]);direction=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
cut_normal=-(R@direction)
for name,solid in cells.items():
 crop=(solid^mf.Manifold.sphere(33.2,144)).trim_by_plane(cut_normal,0)
 mr.meshes['cut-'+name]=mesh(crop)
for j,(families,label) in enumerate([('F','1 · F on the old core'),('FE','2 · E holds the F feet'),('FEW','3 · W holds the E feet'),('FEWC','4 · C holds W; add screws')]):
 obs=[('cut-'+name,R.T,np.zeros(3),color(name)) for name in cells if name=='core' or name[0] in families]
 view=mr.render(obs,size=500,extent=37,elev=25,az=-50);x=20+800*(j%2);y=110+475*(j//2);im.paste(view,(x+145,y));d.text((x+30,y),label,font=font(23),fill='#263844')
d.text((35,1105),'Illustration only: outer bodies cropped at R33.2 and a half-section removed. Printed pieces are whole.',font=font(20),fill='#536570')
im.save(folder/'assembly-layers.png')
print('DRAWINGS DONE',flush=True)
