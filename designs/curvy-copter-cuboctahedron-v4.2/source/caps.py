"""Small twofold keyed plugs. Paper bridges their joint to the fixed rim."""
from inlays import *
from shapely.geometry import box
KEY_SIZE=(12.0,10.4)
KEY_RADIUS=1.2
KEY_GAP=.12
KEY_BOTTOM=38.0
RIB_INTERFERENCE=.04
def keys():
 female=box(-KEY_SIZE[0]/2,-KEY_SIZE[1]/2,KEY_SIZE[0]/2,KEY_SIZE[1]/2).buffer(-KEY_RADIUS).buffer(KEY_RADIUS,quad_segs=12)
 return female,female.buffer(-KEY_GAP,quad_segs=12)
def ribs():
 parts=[]
 for i,half in enumerate(np.array(KEY_SIZE)/2):
  for sign in [-1,1]:
   u=np.eye(3)[i]*sign;z=np.array([0,0,1]);v=np.cross(u,z)
   z0=KEY_BOTTOM+.25;z1=z0+1.
   r0=half-KEY_GAP-.12;r1=half+RIB_INTERFERENCE
   pg=mf.CrossSection([[[r0,z0],[r0,z1],[r1,z1-.22],[r1,z0+.22]]],mf.FillRule.EvenOdd)
   parts.append(xform(pg.extrude(.7).translate([0,0,-.35]),np.column_stack([u,z,v])))
 return union(parts)
def split():
 n=np.array(canonical('C')['direction']);F=frame(n)
 whole=load(CACHE/'pocketed-C.npz');female,male=keys()
 cap=main(whole^xform(cross(male).extrude(60).translate([0,0,KEY_BOTTOM]),F))
 socket=xform(cross(female).extrude(60).translate([0,0,KEY_BOTTOM]),F)
 driver=xform(mf.Manifold.cylinder(80,4.8,4.8,SEG).translate([0,0,SEAT]),F)
 base=main(whole-socket-driver)
 plug=main(cap+xform(ribs(),F))
 hit=(base^plug).volume();assert .02<hit<.3,hit
 save(base,CACHE/'final-C.npz');save(plug,CACHE/'final-cap.npz');save(cap,CACHE/'cap-nominal.npz')
 (CACHE/'caps.json').write_text(json.dumps(dict(key_size_mm=KEY_SIZE,key_corner_radius_mm=KEY_RADIUS,key_gap_per_side_mm=KEY_GAP,key_bottom_mm=KEY_BOTTOM,head_top_mm=35,head_clearance_mm=3,crush_rib_interference_mm=RIB_INTERFERENCE,rib_intersection_mm3=hit,rotational_symmetry_degrees=180,outer_rim_unchanged=True,paper_bridges_joint=True),indent=2)+'\n')
 print('CAP',plug.volume(),'BASE',base.volume(),'RIB INTERFERENCE',hit,flush=True)
if __name__=='__main__':split()
