"""Measure the washer-well/neck web on exported centers; no force rating."""
from conical_design import *
from section_connectivity import polygons
import hashlib,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PP
from shapely.geometry import Polygon
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());ref=json.loads((HERE/'v1-root-reference.json').read_text());records=[];local={}
angles=np.linspace(0,2*np.pi,720,endpoint=False)
for row in ROWS[:6]:
 rec=next(r for r in meta['parts'] if r['name']==row['name']);m=trimesh.load(DEST/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=((m.vertices-T[:,3])@T[:,:3])@frame(row['direction']);local[row['name']]=from_mesh(m)
 tri=m.triangles;r=np.linalg.norm(tri[:,:,:2],axis=2)
 # Select the outward root/underside, excluding the screw and washer bores.
 mask=(r.min(axis=1)>4.85)&(tri[:,:,2].max(axis=1)<31)&(tri[:,:,2].min(axis=1)>23)
 root=m.submesh([np.flatnonzero(mask)],append=True,repair=False)
 points=np.column_stack([4.8*np.cos(angles),4.8*np.sin(angles),np.full(len(angles),SEAT)])
 closest,distances,_=trimesh.proximity.closest_point(root,points);i=int(np.argmin(distances));minimum=float(distances[i]);assert minimum>2.0,(row['name'],minimum)
 segment=np.linspace(points[i],closest[i],21)[1:-1];assert m.contains(segment).all(),row['name']
 old=next(r for r in ref['ligaments'] if r['name']==row['name'])['results'][0]
 records.append(dict(name=row['name'],old_minimum_mm=old['min_root_ligament'],new_minimum_mm=minimum,angle_samples=720,well_corner=points[i].tolist(),root_surface_point=closest[i].tolist()))
 print('ROOT WEB',records[-1],flush=True)
cube=xform(mf.Manifold.cube([SIDE]*3,True),R);hardware=[]
for i,n in enumerate(AXES):
 b,w=hardware_pair=__import__('conical_design').hardware(n)
 assert (b-cube).volume()<.001 and (w-cube).volume()<.001
 v=mesh(b).vertices@R;gap=float((SIDE/2-abs(v)).min());hardware.append(dict(axis=i,minimum_screw_to_cube_face_mm=gap))
tip=SEAT+1-20;past=(NUT_ROOF-4)-tip;assert past>=1
report=dict(passed=True,manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),centers=records,
            washer_seat_mm=SEAT,screw_tip_mm=tip,tip_beyond_nut_mm=past,hardware=hardware,
            scope='Sampled geometric web distance from the washer-well bottom rim to the exposed stalk-root surface. Material on the shortest segment is checked. This is not a strength or fatigue test.')
(DEST/'reports/root-web.json').write_text(json.dumps(report,indent=2))
# Side-by-side actual through-axis section, plus close-ups of the critical root.
old=mf.CrossSection(ref['section_loops']);new=xform(local['C01'],Rotation.from_euler('x',90,degrees=True).as_matrix()).slice(0);added=new-old
fig,axs=plt.subplots(2,2,figsize=(12,10),gridspec_kw={'height_ratios':[2,1]},facecolor='#fafaf8')
for j,(cs,seat,label) in enumerate([(old,27.3,'v1 — original'),(new,SEAT,'v1.1 — reinforced')]):
 for ax in axs[:,j]:
  for p in polygons(cs):
   ax.add_patch(PP(np.array(p.exterior.coords),facecolor='#79b59e',edgecolor='#243e45',lw=.8))
   for ring in p.interiors:ax.add_patch(PP(np.array(ring.coords),facecolor='#fafaf8',edgecolor='#243e45',lw=.8))
  if j:
   for p in polygons(added):ax.add_patch(PP(np.array(p.exterior.coords),facecolor='#efbf57',edgecolor='none'))
  ax.set_aspect('equal');ax.axis('off')
 axs[0,j].set(xlim=(-15,15),ylim=(-38,-16),title=label)
 axs[0,j].annotate('Bearing foot',xy=(2.5,-18.4),xytext=(7,-18),arrowprops=dict(arrowstyle='->',color='#44595d'),fontsize=11)
 axs[0,j].annotate('Ø3.6 screw passage',xy=(0,-23),xytext=(-14,-21),arrowprops=dict(arrowstyle='->',color='#44595d'),fontsize=10)
 axs[0,j].text(0,-33,'Ø9.6\nwasher well',ha='center',va='center',fontsize=11)
 axs[0,j].annotate('Washer seat',xy=(-3.3,-seat),xytext=(-14,-30),arrowprops=dict(arrowstyle='->',color='#44595d'),fontsize=10)
 axs[1,j].set(xlim=(2.4,9),ylim=(-30.5,-25.1))
 result=ref['ligaments'][0]['results'][0] if j==0 else records[0]
 p0=np.array(result['hole_corner'] if j==0 else result['well_corner']);p1=np.array(result['outside'] if j==0 else result['root_surface_point']);distance=result['min_root_ligament'] if j==0 else result['new_minimum_mm']
 a=[np.linalg.norm(p0[:2]),-p0[2]];b=[np.linalg.norm(p1[:2]),-p1[2]]
 axs[1,j].plot([a[0],b[0]],[a[1],b[1]],color='#b84635',lw=2)
 axs[1,j].annotate(f'{distance:.2f} mm web',xy=np.mean([a,b],axis=0),xytext=(6,-29.5),arrowprops=dict(arrowstyle='->',color='#b84635'),color='#9b392d',fontsize=12)
fig.suptitle('A shallower washer well reinforces the stalk root',fontsize=19,y=.98)
fig.text(.5,.03,'Green: existing material    •    Gold: added material    •    Same exterior, bearing foot and retaining surfaces',ha='center',fontsize=11)
fig.tight_layout(rect=[0,.05,1,.95]);fig.savefig(DEST/'images/root-reinforcement.png',dpi=170);plt.close(fig)
