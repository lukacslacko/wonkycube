"""Finish the exact rotated exterior; retain all inner fillets and hardware seats."""
from conical_design import *
OUTER_ROUND=.8

def exterior(s):
 s=s.simplify(.002);kernel=mf.Manifold.sphere(OUTER_ROUND,24)
 protected=s^mf.Manifold.sphere(30.4,SEG)
 seed=s.minkowski_difference(kernel)+protected
 return main(seed.minkowski_sum(kernel)^s)

def stand():
 seat=28.5
 foot=mf.Manifold.cylinder(seat-FOOT_PLANE,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 tube=mf.Manifold.cylinder(90-seat,5.8,5.8,96).translate([0,0,seat-.2])
 base=mf.Manifold.cylinder(4,22,22,96).translate([0,0,86])
 s=foot+tube+base-mf.Manifold.cylinder(120,1.8,1.8,96)-mf.Manifold.cylinder(120,4.8,4.8,96).translate([0,0,seat])
 return xform(main(s),frame(AXES[0]))

def finish():
 t=time.time();cube=xform(mf.Manifold.cube([SIDE]*3,True),R)
 canonical={k:load(CACHE/'ridges-3'/(k+'.npz')) for k in ['C','E','K']}
 raw=raw_cells();records=[];done=set()
 for row in ROWS:
  name=row['name']
  if name in done:continue
  base=next(r for r in ROWS if r['family']==row['family']);q=mapping(base['signature'],row['signature'])
  s=xform(canonical[row['family']],q)^cube
  rawclip=raw[name]^cube
  if row['family']=='C':rawclip=add_axle(rawclip,np.array(row['direction']))
  mask=exterior(rawclip)
  result=main(s^mask)
  if row['family']=='C':result=add_axle(result,np.array(row['direction']))
  save(result,CACHE/'final'/(name+'.npz'))
  opposite=next(rr['name'] for rr in ROWS if np.linalg.norm(np.array(rr['direction'])+row['direction'])<1e-5)
  save(xform(result,-np.eye(3)),CACHE/'final'/(opposite+'.npz'));done.update([name,opposite])
  records.append(dict(name=name,opposite=opposite,volume_mm3=result.volume(),triangles=result.num_tri()))
  print('FINISH',records[-1],round(time.time()-t,1),flush=True)
 (CACHE/'finish-report.json').write_text(json.dumps(records,indent=2))
if __name__=='__main__':finish()
