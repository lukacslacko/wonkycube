"""Central keyed screw plugs; the main piece keeps its rim and foam backing."""
from inlays import *

KEY_GAP=.12
KEY_AF=8.0
KEY_CORNER_RADIUS={'T':2.25,'S':1.0}
KEY_BOTTOM={'T':36.6,'S':40.0}
RIB_INTERFERENCE=.04

def rd(height):
 s=mf.Manifold.cube([140]*3,True)
 for n,_,_ in FACES:s=s.trim_by_plane(-n,-height)
 return s

def prepare():
 ball=mf.Manifold.sphere(.45,24)
 rounded_outer=outer().minkowski_difference(ball).minkowski_sum(ball)^outer()
 for f in ORBITS:
  s=load(CACHE/f'final-{f}.npz');save(s,CACHE/f'mechanism-bare-{f}.npz')
  if f!='P':
   n=np.array(canonical(f)['direction']);bottom=SEATS[f]+WASHER_H+3+.9
   fill=xform(mf.Manifold.cylinder(70,WELL_R+.015,WELL_R+.015,SEG).translate([0,0,bottom]),frame(n))^rounded_outer
   s=main(s+fill,.001)
  save(s,CACHE/f'bare-{f}.npz')

def keys(f):
 n=np.array(canonical(f)['direction']);F=frame(n)
 normals=[nn for nn,_,_ in FACES if nn@n>.7]
 directions=[];pg=Polygon([[-30,-30],[30,-30],[30,30],[-30,30]])
 for nn in normals:
  u=F[:,:2].T@nn;u/=np.linalg.norm(u);directions.append(u)
  v=np.array([-u[1],u[0]]);anchor=u*KEY_AF/2
  pg=pg.intersection(Polygon([anchor-v*100,anchor+v*100,anchor+v*100-u*200,anchor-v*100-u*200]))
 assert len(directions)==(3 if f=='T' else 4)
 r=KEY_CORNER_RADIUS[f]
 female=pg.buffer(-r,quad_segs=12).buffer(r,quad_segs=12)
 male=female.buffer(-KEY_GAP,quad_segs=12)
 return female,male,directions

def ribs(f,directions):
 n=np.array(canonical(f)['direction']);F=frame(n);parts=[]
 z0=KEY_BOTTOM[f]+.25;z1=KEY_BOTTOM[f]+1.25
 r0=KEY_AF/2-KEY_GAP-.12;r1=KEY_AF/2+RIB_INTERFERENCE
 profile=mf.CrossSection([[[r0,z0],[r0,z1],[r1,z1-.22],[r1,z0+.22]]],mf.FillRule.EvenOdd).extrude(.7).translate([0,0,-.35])
 for u in directions:
  radial=np.r_[u,0];axial=np.array([0.,0,1]);tangent=np.cross(radial,axial)
  parts.append(xform(profile,F@np.column_stack([radial,axial,tangent])))
 return union(parts)

def split():
 records=[]
 for f in ['T','S']:
  row=canonical(f);n=np.array(row['direction']);F=frame(n)
  whole=load(CACHE/f'pocketed-{f}.npz')
  female,male,directions=keys(f)
  plug_column=xform(cross(male).extrude(100).translate([0,0,KEY_BOTTOM[f]]),F)
  socket=xform(cross(female).extrude(100).translate([0,0,KEY_BOTTOM[f]]),F)
  nominal=main(whole^plug_column,.002)
  # The socket is local to the screw well. Retain the complete outer rim,
  # the divider walls beyond the key, and the original foam-pocket floors.
  driver=xform(mf.Manifold.cylinder(100,WELL_R,WELL_R,SEG).translate([0,0,SEATS[f]]),F)
  base=main(whole-socket-driver,.002)
  plug=main(nominal+ribs(f,directions),.002)
  assert plug.status()==mf.Error.NoError and plug.volume()>100,(f,'invalid plug',plug.status())
  assert (nominal^base).volume()<.003,(f,'rigid plug interference')
  overlap=(plug^base).volume();assert .025<overlap<.25,(f,'friction-rib fit',overlap)
  print('PLUG',f,'base',base.volume(),'plug',plug.volume(),'rib overlap',overlap,flush=True)
  save(base,CACHE/f'final-{f}.npz');save(plug,CACHE/f'final-{f}C.npz');save(nominal,CACHE/f'cap-nominal-{f}.npz')
  save(base+plug,CACHE/f'combined-{f}.npz')
  records.append(dict(family=f,plug_family=f+'C',key_across_flats_mm=KEY_AF,key_corner_radius_mm=KEY_CORNER_RADIUS[f],key_clearance_per_side_mm=KEY_GAP,key_bottom_mm=KEY_BOTTOM[f],screw_head_mm=SEATS[f]+WASHER_H+3,head_clearance_mm=KEY_BOTTOM[f]-(SEATS[f]+WASHER_H+3),crush_rib_interference_mm=RIB_INTERFERENCE,rib_overlap_mm3=overlap,outer_rim_modified=False,foam_bridges_plug_joint=True,female_key=coords(female),male_key=coords(male)))
 save(load(CACHE/'final-P.npz'),CACHE/'combined-P.npz')
 (CACHE/'caps.json').write_text(json.dumps(records,indent=2)+'\n')

if __name__=='__main__':
 import sys
 prepare() if '--prepare' in sys.argv else split()
