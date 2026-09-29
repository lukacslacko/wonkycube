"""Remove the three print-fragile extremities of the corner's inner flange."""
from design import *
def trim_corner(s):
 # Reconstruct before measuring: tiny tangent remnants can separate when
 # triangulated. None are load-bearing attachments.
 chunks=sorted(from_mesh(mesh(s)).decompose(),key=lambda c:c.volume(),reverse=True)
 discarded=sum(abs(c.volume()) for c in chunks[1:]);assert discarded<.1
 s=chunks[0];n=np.array(canonical('K')['direction']);t=np.array([2.,-1,1])/np.sqrt(6)
 chord=6.5;level=28.5;cutters=[]
 for i in range(3):
  ti=Rotation.from_rotvec(n*i*2*np.pi/3).as_matrix()@t
  F=np.column_stack([ti,n,np.cross(ti,n)])
  # Clip the deep tip, then taper the clipping back out of the body.
  p=mf.CrossSection([[[chord,-100],[100,-100],[100,level+(100-chord)/2],[chord,level]]])
  p=p.offset(.15,join_type=mf.JoinType.Round,circular_segments=24)
  cutters.append(xform(p.extrude(200).translate([0,0,-100]),F))
 result=main(s-union(cutters),.01);removed=s.volume()-result.volume();assert 0<removed<40
 (CACHE/'corner-tip-trim.json').write_text(json.dumps(dict(threefold_symmetric=True,chord_mm=chord,transition_axis_height_mm=level,cutter_rounding_mm=.15,removed_volume_mm3=removed,prior_detached_volume_mm3=discarded,reason='Remove flange extremities which otherwise become detached printable islands at 0.20 mm layers / 0.45 mm line width.'),indent=2)+'\n')
 return result
