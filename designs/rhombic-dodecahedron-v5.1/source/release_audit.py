"""Audit all delivered meshes and record the core's exact compatibility."""
from design import *
import hashlib

def audit():
 checks=[]
 inlay_report=json.loads((DEST/'reports/printable-inlays.json').read_text())
 assert inlay_report['passed']
 component_counts={r['file']:r['components'] for r in inlay_report['files']}
 for p in sorted(DEST.rglob('*.stl')):
  m=trimesh.load(p,force='mesh')
  count=component_counts.get(p.relative_to(DEST).as_posix(),1)
  assert m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==count,p
  checks.append(dict(file=p.relative_to(DEST).as_posix(),watertight=True,components=count,volume_mm3=float(m.volume),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 (DEST/'reports/all-stl-audit.json').write_text(json.dumps(checks,indent=2)+'\n')
 # A deeper test recess must stay open at the top, with a real floor below it.
 coupon=trimesh.load(DEST/'stl/fit-coupons/foam-pocket-test.stl',force='mesh')
 hits,_,_=coupon.ray.intersects_location([[0,0,10]],[[0,0,-1]])
 floor=float(hits[:,2].max());depth=float(coupon.bounds[1,2]-floor)
 assert abs(depth-2.1)<.005 and floor>1.8,('coupon recess',depth,floor)
 (DEST/'reports/foam-coupon.json').write_text(json.dumps(dict(recess_depth_mm=depth,floor_thickness_mm=floor,open_top_verified=True),indent=2)+'\n')
 sha=hashlib.sha256((DEST/'stl/puzzle/core.stl').read_bytes()).hexdigest()
 assert sha=='2424250181e27338f25ef90b7bbe66e7d5ba9beca6b5c5e347a9555a172ab8cc','Core changed; reconsider compatibility and update the documentation.'
 (DEST/'reports/core-reuse.json').write_text(json.dumps(dict(byte_identical=True,compatible_design='face-turning-cuboctahedron-v1',sha256=sha,nut_seat_across_flats_mm=5.25),indent=2)+'\n')
 meta=json.loads((DEST/'manifest.json').read_text());meta['inlays']=dict(total=96,per_face=8,faces=12,thickness_mm=2.0,recess_depth_mm=2.1,minimum_between_pockets_mm=1.6,default_cuts='inlays/faces',fit_coupon='stl/fit-coupons/foam-pocket-test.stl',face_map='images/inlay-face-map.png')
 assert json.loads((DEST/'reports/cap-fit.json').read_text())['passed']
 assert json.loads((DEST/'reports/cap-key-coupons.json').read_text())['passed']
 meta['plugs']=dict(total=14,threefold=8,fourfold=6,key_clearance_per_side_mm=.12,rib_interference_mm=.04,outer_rim_modified=False,fit_test='stl/fit-coupons/cap-key-fit-tests.3mf',glue_policy='Foam spans base and plug. Glue after adjustment; remove and replace that foam to service the screw.')
 (DEST/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('RELEASE AUDIT',len(checks),'meshes',flush=True)
if __name__=='__main__':audit()
