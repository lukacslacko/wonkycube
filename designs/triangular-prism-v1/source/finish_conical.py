"""Finish the exact rotated exterior; retain all inner fillets and hardware seats."""
from conical_design import *
OUTER_ROUND=.8

def trim_corner_tips(s,row):
 # Three small terminal regions where pairs of stepped flanges meet can
 # leave webs too narrow to print. Keep the broad capture lobes and exterior.
 tools=[]
 for i,j in itertools.combinations(row['signature'],2):
  k=next(k for k in row['signature'] if k not in [i,j])
  tools.append(mf.Manifold.cube([160]*3,True).trim_by_plane(-AXES[i],-9.5).trim_by_plane(-AXES[j],-9.5).trim_by_plane(AXES[k],17.))
 tool=union(tools)^mf.Manifold.sphere(31.0,120)
 result=main(s-tool)
 removed=s.volume()-result.volume()
 assert 0<removed<12.,(row['name'],removed)
 report=dict(name=row['name'],removed_volume_mm3=removed,pair_axis_upper_bound_mm=9.5,third_axis_lower_bound_mm=17.,maximum_radial_extent_mm=31.,purpose='Remove nonprinting terminal webs, retain the broad capture lobes.')
 path=CACHE/'terminal-trimming';path.mkdir(exist_ok=True)
 (path/(row['name']+'.json')).write_text(json.dumps(report,indent=2))
 return result

def exterior(s,extra_protection=None):
 s=s.simplify(.002);kernel=mf.Manifold.sphere(OUTER_ROUND,24)
 protected=s^mf.Manifold.sphere(30.4,SEG)
 if extra_protection is not None:protected=protected+(s^extra_protection)
 seed=s.minkowski_difference(kernel)+protected
 return main(seed.minkowski_sum(kernel)^s)

def stand():
 seat=SEAT
 foot=mf.Manifold.cylinder(seat-FOOT_PLANE,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 tube=mf.Manifold.cylinder(90-seat,5.5,5.5,96).translate([0,0,seat-.2])
 base=mf.Manifold.cylinder(4,22,22,96).translate([0,0,86])
 transition=mf.Manifold.cylinder(2.,FOOT_R,5.5,96).translate([0,0,seat-2.2])
 s=foot+tube+base+transition-mf.Manifold.cylinder(120,1.8,1.8,96)-mf.Manifold.cylinder(120,4.8,4.8,96).translate([0,0,seat])
 return xform(main(s),frame(AXES[0]))

def finish_one(row):
 name=row['name'];path=CACHE/'final'/(name+'.npz')
 if path.exists():
  result=load(path)
 else:
  cube=xform(mf.Manifold.cube([SIDE]*3,True),R)
  orbit=row['orbit'];base=canonical(orbit);q=mapping(base['signature'],row['signature'])
  s=xform(load(CACHE/'ridges-2'/(orbit+'.npz')),q)^cube
  rawclip=xform(load(CACHE/'raw'/(orbit+'.npz')),q)^cube
  if row['family']=='C':rawclip=add_axle(rawclip,np.array(row['direction']))
  guard=None
  if row['family']=='C':
   guard=xform(mf.Manifold.cylinder(SEAT+.15-FOOT_PLANE,5.6,5.6,96).translate([0,0,FOOT_PLANE]),frame(row['direction']))
  mask=exterior(rawclip,guard);result=main(s^mask)
  if row['family']=='C':result=add_axle(result,np.array(row['direction']))
  if row['family']=='K':result=trim_corner_tips(result,row)
  save(result,path)
 record=dict(name=name,volume_mm3=result.volume(),triangles=result.num_tri())
 print('FINISH',record,flush=True)
 return record

def finish():
 from concurrent.futures import ProcessPoolExecutor
 t=time.time()
 with ProcessPoolExecutor(max_workers=int(os.environ.get('CONICAL_FINISH_WORKERS','3'))) as pool:
  records=list(pool.map(finish_one,ROWS))
 (CACHE/'finish-report.json').write_text(json.dumps(records,indent=2))
 print('EXTERIOR FINISHED',time.time()-t,flush=True)
if __name__=='__main__':finish()
