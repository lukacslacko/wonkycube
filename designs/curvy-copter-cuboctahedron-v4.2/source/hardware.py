from design import *
def hex_section(af):return mf.CrossSection([[[af/np.sqrt(3)*np.cos(t),af/np.sqrt(3)*np.sin(t)] for t in np.arange(6)*np.pi/3]])
def nut_slot(af=NUT_SEAT_AF):
 half=af/2;entry=NUT_ENTRY_AF/2
 p=mf.CrossSection([[[0,-half],[3.,-half],[6.,-entry],[35,-entry],[35,entry],[6.,entry],[3.,half],[0,half]]])
 return (hex_section(af)+p).extrude(4.25).translate([0,0,NUT_ROOF-4.25])
def core(af=NUT_SEAT_AF):
 s=mf.Manifold.sphere(CORE_R,SEG)
 for n in AXES:s=s.trim_by_plane(-n,-CORE_PAD)
 holes=[xform(nut_slot(af)+mf.Manifold.cylinder(80,1.7,1.7,96).translate([0,0,-40]),frame(n)) for n in AXES]
 return main(subtract(s,holes))
def nut():return hex_section(5.5).extrude(4).translate([0,0,NUT_ROOF-4.])-mf.Manifold.cylinder(40,1.5,1.5,48)
def hardware(n,lift=0):
 z=SEAT+lift
 screw=mf.Manifold.cylinder(20,1.5,1.5,72).translate([0,0,z+1-20])+mf.Manifold.cylinder(3,2.75,2.75,72).translate([0,0,z+1])
 washer=(mf.Manifold.cylinder(1,4.5,4.5,72)-mf.Manifold.cylinder(1,1.6,1.6,72)).translate([0,0,z])
 return xform(screw,frame(n)),xform(washer,frame(n)),xform(nut(),frame(n))
def coupon(af):
 block=mf.Manifold.cube([24,18,10],False).translate([-12,-9,CORE_PAD-10])
 return main(block-nut_slot(af)-mf.Manifold.cylinder(40,1.7,1.7,72))
def stand():
 foot=mf.Manifold.cylinder(SEAT-FOOT_PLANE+.2,FOOT_R,FOOT_R,96).translate([0,0,FOOT_PLANE])
 tube=mf.Manifold.cylinder(88-SEAT,5.5,5.5,96).translate([0,0,SEAT-.1])
 base=mf.Manifold.cylinder(4,22,22,96).translate([0,0,86])
 s=foot+tube+base-mf.Manifold.cylinder(120,1.8,1.8,96)-mf.Manifold.cylinder(120,4.8,4.8,96).translate([0,0,SEAT])
 return xform(main(s),frame(canonical('C')['direction']))
if __name__=='__main__':
 s=core();save(s,CACHE/'core.npz');print('CORE',s.volume(),s.num_tri(),flush=True)
 parts=[hardware(n) for n in AXES];worst=0
 for i,j in itertools.combinations(range(12),2):
  a=union(parts[i]);b=union(parts[j]);worst=max(worst,(a^b).volume())
 print('HARDWARE PAIRS',worst,flush=True)
 assert worst<1e-7
