"""Central plug removal after removing its foam, key fit and shared backing."""
from caps import *
from hardware import hardware

def validate():
 data=json.loads((CACHE/'inlays.json').read_text())['records'];parts={f:load(CACHE/f'printed-{f}.npz') for f in ORBITS+['TC','SC']}
 complete={}
 for f in ORBITS:
  foam=union([fitted(r).translate(np.array(r['frame'])[:,2]*.1) for r in data if r['family']==f])
  s=parts[f]+foam
  if f in ['T','S']:s=s+parts[f+'C']
  complete.update(replicate(s,f))
 hw=union([s for i in range(N_AXES) for s in hardware(i)])
 records=[]
 for f in ['T','S']:
  row=canonical(f);n=np.array(row['direction']);base=parts[f];cap=parts[f+'C'];nominal=load(CACHE/f'cap-nominal-{f}.npz')
  foam=union([fitted(r).translate(np.array(r['frame'])[:,2]*.1) for r in data if r['family']==f])
  fixed=union([s for name,s in complete.items() if name!=row['name']]+[base,load(CACHE/'printed-core.npz'),hw])
  worst=0.;contacts=[]
  for d in np.r_[np.arange(0,3.01,.1),np.arange(3.5,60.01,.5)]:
   # The owner accepts removing/replacing the foam before servicing a plug.
   hit=(nominal.translate(n*d)^fixed).volume();worst=max(worst,hit)
   crush=(cap.translate(n*d)^base).volume();contacts.append([float(d),float(crush)])
   assert hit<.005,('cap removal blocked',f,d,hit)
   assert crush<.25,('excess cap interference',f,d,crush)
  # A positive key blocks unintended rotation but admits the correct symmetry.
  locking=None
  for angle in np.arange(.25,10.01,.25):
   q=Rotation.from_rotvec(n*np.radians(angle)).as_matrix();hit=(xform(nominal,q)^base).volume()
   if hit>.01:locking=dict(angle_degrees=float(angle),overlap_mm3=float(hit));break
  assert locking is not None and locking['angle_degrees']<=3,('loose rotational key',f,locking)
  sym=120 if f=='T' else 90
  q=Rotation.from_rotvec(n*np.radians(sym)).as_matrix();symhit=(xform(nominal,q)^base).volume();assert symhit<.005,(f,'key symmetry failed',symhit)
  screw=hardware(row['signature'][0])[0];gap=cap.min_gap(screw,15);assert gap>1.0-.01,(f,'screw-head clearance',gap)
  supports=[];female,male,_=keys(f);F=frame(n)
  # Preserve a visible outer border rather than extending the plug out to
  # the perimeter. This is a projected rim margin, not a 3D wall gauge.
  shell=load(CACHE/f'bare-{f}.npz')-rd(FACE_HEIGHT-.25)
  projection=xform(shell,F.T).project()
  outline=region(mf.CrossSection(projection.to_polygons(),mf.FillRule.Positive))
  outline=Polygon(outline.exterior)
  margin=female.boundary.distance(outline.boundary)
  assert outline.contains(female) and margin>1.6,('socket reaches outer rim',f,margin)
  joint=xform(cross(female-male).extrude(100).translate([0,0,KEY_BOTTOM[f]]),F)
  for rec in data:
   if rec['family']!=f:continue
   # Foam intentionally spans both solids. Its only unsupported strip must
   # be the narrow keyed joint, not a missing floor elsewhere in the pocket.
   p=polygon(rec['pocket']).buffer(-.025)
   probe=xform(cross(p).extrude(.10).translate([0,0,FACE_HEIGHT-DEPTH-.10]),np.array(rec['frame']))
   missing=(probe-(base+cap)-joint).volume();assert missing<.003,(f,'foam floor missing outside key joint',rec['id'],missing)
   on_base=(probe^base).volume()/probe.volume();on_plug=(probe^cap).volume()/probe.volume()
   assert on_base>.4,(f,'plug takes too much of the foam floor',on_base)
   supports.append(dict(inlay=rec['id'],base_backing_fraction=on_base,plug_backing_fraction=on_plug,missing_outside_joint_mm3=missing))
  records.append(dict(family=f,maximum_removal_collision_mm3=worst,maximum_printed_rib_interference_mm3=max(c[1] for c in contacts),interference_samples=contacts,key_rotation_contact=locking,symmetry_rotation_degrees=sym,symmetry_overlap_mm3=symhit,screw_head_clearance_mm=gap,projected_socket_to_outer_rim_mm=margin,foam_backing=supports))
  print('CAP CHECK',f,'removal',worst,'head gap',gap,'rotation contact',locking,flush=True)
 (DEST/'reports/cap-fit.json').write_text(json.dumps(dict(passed=True,checks=records,scope='Straight plug removal with foam removed from that center; other assembled pieces remain present. Foam spans the base/plug joint and may be destroyed during servicing. Printed ribs have intentional limited interference; fit force and wear require a physical test.'),indent=2)+'\n')

if __name__=='__main__':validate()
