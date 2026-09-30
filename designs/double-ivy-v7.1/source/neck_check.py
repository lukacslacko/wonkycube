"""Conservative erosion probe of common internal necks, not a strength simulation."""
from design import *
report={}
for fam in 'CWEF':
 s=load(CACHE/f'rounded-{fam}.npz')^mf.Manifold.sphere(33.2,SEG)
 if fam=='C':s=axle(s,np.array(canonical(fam)['direction']))
 eroded=s.minkowski_difference(mf.Manifold.sphere(.60,20));chunks=sorted(eroded.decompose(),key=lambda x:x.volume(),reverse=True)
 radius=FOOT_LIMITS.get(fam,22.1)
 mainpart=chunks[0];foot=(mainpart^mf.Manifold.sphere(radius-.6,96)).volume();body=(mainpart-mf.Manifold.sphere(32.1,96)).volume()
 assert foot>5 and body>10,(fam,foot,body)
 report[fam]=dict(erosion_radius_mm=.6,connected_remaining_inner_foot_volume_mm3=foot,connected_remaining_outer_body_volume_mm3=body,component_volumes_mm3=[x.volume() for x in chunks])
 print(fam,report[fam],flush=True)
report['scope']='Common mechanism region below R33.2, eroded by a 0.6 mm radius ball. The retained foot and outer body remain in the same component, indicating a connected path with about 1.2 mm local thickness (nominal faceted probe). This is not FEA or an endurance/strength guarantee.'
(DEST/'reports/neck-check.json').write_text(json.dumps(report,indent=2)+'\n')
