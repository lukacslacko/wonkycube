from skewb_design import *
from corner_tip_trim import tip_cutters
from finish_skewb import outer_rounded
import mesh_render as rr
from PIL import Image,ImageDraw,ImageFont
row=next(r for r in ROWS if r['name']=='K01');f=frame(row['direction'])
before=load(CACHE/'ridges-3/K.npz')^xform(mf.Manifold.cube([SIDE]*3,True),R)
before=main(before^(outer_rounded(row)+mf.Manifold.sphere(30,SEG)))
after=load(CACHE/'final/K01.npz');removed=before^union(tip_cutters(row));lim=mf.Manifold.sphere(27.5,SEG)
for name,s in [('before',before^lim),('after',after^lim),('removed',removed)]:rr.meshes[name]=mesh(s.simplify(.003))
im=Image.new('RGB',(1440,830),'#fafaf8');d=ImageDraw.Draw(im);font='/System/Library/Fonts/Helvetica.ttc'
def label(x,y,t,size=24):d.text((x,y),t,font=ImageFont.truetype(font,size),fill='#253341')
label(35,20,'Floating corners — trim the perforated flange tips',30)
el,az=-65,-85;ee,aa=np.radians([el,az]);cam=np.array([np.cos(ee)*np.cos(aa),np.cos(ee)*np.sin(aa),np.sin(ee)])
for j,key in enumerate(['before','after']):
 objects=[(key,f.T,np.array([0,0,-21]),'#58a9ac')]
 if j==0:objects.append(('removed',f.T,np.array([0,0,-21])+cam*.01,'#de845d'))
 im.paste(rr.render(objects,size=720,extent=20,elev=el,az=az),(j*720,90))
label(35,65,'Before — removed portions highlighted',22);label(755,65,'After — broad retaining lobes remain',22)
label(35,790,'K01 shown from inside; the same trim is applied to K02, K03 and K04.',21)
(WORK/'release/images').mkdir(parents=True,exist_ok=True);im.save(WORK/'release/images/tip-comparison.png')
print('Saved tip comparison',flush=True)
