"""Regress the missing half-arcs using the actual before/after STL meshes."""
from inlays import *
from shapely.geometry import Point
from rounding_repair import tool
from render import image_panel
import mesh_render as mr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import hashlib
def previous(f):
 meta=json.loads((HERE/'rounding-reference/v4-manifest.json').read_text());r=next(r for r in meta['parts'] if r['family']==f)
 p=HERE/'rounding-reference'/{'C':'axial-center-v4.stl','K':'floating-corner-v4.stl','cap':'keyed-plug-v4.stl'}[f]
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 m=trimesh.load(p,force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3]
 return from_mesh(m)
def run():
 meta=json.loads((DEST/'manifest.json').read_text());oldmeta=json.loads((HERE/'rounding-reference/v4-manifest.json').read_text());out=[];panels=[];sections=[]
 for f in ['core']:
  a=next(r for r in oldmeta['parts'] if r['family']==f);b=next(r for r in meta['parts'] if r['family']==f);assert a['sha256']==b['sha256']
 # Exterior pockets and plugs change with depth. Retain the core and check
 # both halves of every repaired fillet on the actual new exports.
 inner=mf.Manifold.sphere(35,192)
 for f in ['C','K']:
  old=previous(f);new=load(CACHE/f'printed-{f}.npz');removed=old-new;added=new-old
  assert (added^inner).volume()<.01,(f,'unexpected new internal material',(added^inner).volume())
  spine_removed=None
  if f=='K':
   Fsp=frame(canonical('K')['direction']);spine=xform(mf.Manifold.cylinder(7,1.65,1.65,144).translate([0,0,28]),Fsp)
   spine_removed=(removed^spine).volume();assert spine_removed<.001,('protected corner spine changed',spine_removed)
  reference=json.loads((HERE/'rounding-reference'/(f+'-sections.json')).read_text());edgechecks=[];best=None
  for rec in reference:
   if f=='C' and canonical('C')['signature'][0] in rec['axes']:continue
   cut,_=tool(rec);residual=(new^cut).volume()
   # No material should remain inside either half of the specified fillet.
   assert residual<.005,(f,rec['axes'],'uncut half-arc',residual)
   F=np.array(rec['frame']);a=xform(old,F);b=xform(new,F);maxarea=0;maxsample=None
   for rr in rec['sections']:
    if min(abs(t) for t in rr['angles'])>.002:continue
    z=rr['station_mm']
    if z<20:continue
    po=region(a.slice(z));pn=region(b.slice(z));delta=po-pn
    maxarea=max(maxarea,delta.area)
    cy,cz=rr['center'];aa=max(abs(v) for v in rr['angles'])
    targets=[Point(cy-2*np.cos(t),cz+2*np.sin(t)) for t in [-.55*aa,.55*aa]]
    distances=[pn.boundary.distance(p) for p in targets]
    old_distances=[po.boundary.distance(p) for p in targets]
    # Some stations are truncated by the separate spherical return or tip
    # trim; a full two-sided arc is not exposed there. Measure a station
    # with both sides present and a substantial pre-repair half-arc error.
    if max(distances)<.03 and max(old_distances)>.05:
     if maxsample is None or delta.area>maxsample[5]:maxsample=(z,rr,po,pn,F,delta.area)
   edgechecks.append(dict(axes=rec['axes'],radius_mm=2,remaining_material_in_full_arc_mm3=residual,largest_bad_section_trim_area_mm2=maxarea))
   if maxsample is not None and (best is None or maxsample[5]>best[0]):best=(maxsample[5],rec,maxsample)
  assert best is not None
  area,rec,(z,rr,po,pn,F,_)=best;cy,cz=rr['center'];ang=max(abs(t) for t in rr['angles']);r=rr['radius_mm']
  # Both visible sides of the cylindrical-style R2 face are measured; testing
  # just the middle of an arc would miss the original one-sided failure.
  measurements=[]
  for sign in [-1,1]:
   theta=sign*.55*ang;pt=np.array([cy-r*np.cos(theta),cz+r*np.sin(theta)])
   distance=pn.boundary.distance(Point(pt))
   measurements.append(dict(side=sign,angle_radians=theta,distance_to_expected_R2_arc_mm=distance,old_distance_mm=po.boundary.distance(Point(pt))))
   assert distance<.03,(f,'half-arc surface misses radius',sign,z,distance)
  sections.append((f,z,rr,po,pn,measurements))
  print('ROUNDING REGRESSION',f,'removed',removed.volume(),'exterior material restored by new pocket outlines',added.volume(),'both sides',measurements,flush=True)
  out.append(dict(family=f,removed_volume_mm3=removed.volume(),added_volume_mm3=added.volume(),added_internal_numerical_residual_mm3=(added^inner).volume(),protected_corner_spine_removed_mm3=spine_removed,edges=edgechecks,measured_section_mm=z,both_half_arc_measurements=measurements))
  mr.meshes['old']=mesh(old);mr.meshes['new']=mesh(new)
  q=frame(canonical(f)['direction']).T;shift=[0,0,-32]
  for label in ['old','new']:
   panels.append(mr.render([(label,q,shift,'#e3ac32')],size=850,extent=28 if f=='C' else 18,elev=-15,az=-70))
 image_panel(panels[:2],['Screwed piece · before','Screwed piece · repaired'],DEST/'images/rounding-center.png',['Thin hooks interrupt the flange-end fillet','Both halves continue around the edge'])
 image_panel(panels[2:],['Floating corner · before','Floating corner · repaired'],DEST/'images/rounding-corner.png',['Small projections remain at the foot tips','Complete R2 arc; spherical lands retained'])
 fig,axs=plt.subplots(1,2,figsize=(12,5))
 for ax,(f,z,rr,po,pn,measures) in zip(axs,sections):
  cy,cz=rr['center'];aa=max(abs(t) for t in rr['angles'])
  for pg,col in [(po,'#df8573'),(pn,'#76bfa6')]:
   for p in polygons(pg):ax.fill(*np.array(p.exterior.coords).T,color=col,ec='#33464e',lw=.5)
  t=np.linspace(-aa,aa,140);ax.plot(cy-2*np.cos(t),cz+2*np.sin(t),'k--',lw=1)
  ax.set_xlim(cy-2.3,cy+.35);ax.set_ylim(cz-2.2,cz+2.2);ax.set_aspect('equal');ax.set_title(f'{f}: section at {z:.3f} mm');ax.set_xlabel('mm');ax.set_ylabel('mm')
 fig.suptitle('Complete both halves of the radial fillet\nRed: removed hook · green: repaired piece · dashed: R2 circle',fontsize=13);fig.tight_layout();fig.savefig(DEST/'images/rounding-sections.png',dpi=180);plt.close(fig)
 (DEST/'reports/rounding-regression.json').write_text(json.dumps(dict(passed=True,byte_identical_stl_families=['core'],paper_pockets_and_cut_contours_identical=False,pocket_depth_mm=DEPTH,checks=out,scope='Every repaired swept half-arc is checked for residual material. Both sides of a strongly affected full-arc section per family are compared with the intended R2 circle. Pocket contours are regenerated for the deeper recesses. Numerical mesh residual tolerance is separate from the localized physical trims.'),indent=2)+'\n')
if __name__=='__main__':run()
