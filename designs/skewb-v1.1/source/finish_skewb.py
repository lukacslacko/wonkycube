"""Clip canonical mechanisms to the rotated cube and soften exterior edges."""
from skewb_design import *
from corner_tip_trim import trim_corner_tips
OUTER_ROUND=.8

def outer_rounded(row):
 r=OUTER_ROUND
 poly=xform(mf.Manifold.cube([SIDE-2*r]*3,True),R)
 for i,n in enumerate(AXES):poly=poly.trim_by_plane(n if i in row['signature'] else -n,BODY_GAP/2+r)
 points=mesh(poly).vertices;kernel=mesh(mf.Manifold.sphere(r,24)).vertices
 return mf.Manifold.hull_points((points[:,None,:]+kernel[None,:,:]).reshape((-1,3)))

def stand():
 seat=28.5
 foot=mf.Manifold.cylinder(seat-FOOT_PLANE,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 tube=mf.Manifold.cylinder(90-seat,5.8,5.8,96).translate([0,0,seat-.2])
 base=mf.Manifold.cylinder(4,22,22,96).translate([0,0,86])
 s=foot+tube+base-mf.Manifold.cylinder(120,1.8,1.8,96)-mf.Manifold.cylinder(120,4.8,4.8,96).translate([0,0,seat])
 return xform(main(s),frame(AXES[0]))

def finish(canonical):
 cube=xform(mf.Manifold.cube([SIDE]*3,True),R);protect=mf.Manifold.sphere(30,SEG)
 result={}
 for row in ROWS:
  name=row['name'];base=next(r for r in ROWS if r['family']==row['family']);q=mapping(base['signature'],row['signature'])
  s=xform(canonical[row['family']],q)^cube
  s=main(s^(outer_rounded(row)+protect))
  if row['family']=='C':s=add_axle(s,np.array(row['direction']))
  if row['family']=='K':s=trim_corner_tips(s,row)
  result[name]=s;save(s,CACHE/'final'/(name+'.npz'))
  print('FINISH',name,round(s.volume(),3),s.num_tri(),flush=True)
 return result
if __name__=='__main__':finish({k:load(CACHE/'ridges-3'/(k+'.npz')) for k in ['C','F','K']})
