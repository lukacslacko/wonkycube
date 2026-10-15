"""Read exported STLs back; test preserved internals and new pockets/plugs."""
from caps import *
from hardware import hardware
from section_connectivity import check as layers
from retention_v2 import retaining_foot,curve,summary,unit
import hashlib
def report(name,data):
 (DEST/'reports'/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
def run():
 meta=json.loads((DEST/'manifest.json').read_text());parts={};rows=meta['parts']
 for r in rows:
  m=trimesh.load(DEST/r['file'],force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3]
  assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
  parts[r['family']]=from_mesh(m)
 assert hashlib.sha256((DEST/'stl/puzzle/core.stl').read_bytes()).hexdigest()==hashlib.sha256((HERE/'fixed-baseline/core.stl').read_bytes()).hexdigest()
 data=json.loads((CACHE/'inlays.json').read_text())['records']
 combined={};preservation=[];floor=[]
 sphere=mf.Manifold.sphere(35,192)
 for f in ORBITS:
  s=parts[f]+(parts['cap'] if f=='C' else mf.Manifold());old=load(CACHE/f'mechanism-{f}.npz')
  delta=(((s^sphere)-(old^sphere))+((old^sphere)-(s^sphere))).volume()
  assert delta<.01,('inner geometry changed',f,delta)
  preservation.append(dict(family=f,verified_radius_mm=35,symmetric_difference_mm3=delta))
  inlays=[]
  for rec in data:
   if rec['family']!=f:continue
   paper=fitted(rec);hit=(s^paper).volume();assert hit<.005,('paper overlaps plastic',rec['id'],hit)
   inlays.append(paper)
   p=polygon(rec['pocket']).buffer(-.025);probe=xform(cross(p).extrude(.1).translate([0,0,rec['height_mm']-DEPTH-.1]),np.array(rec['frame']))
   if f=='C':
    a,b=keys();joint=xform(cross(a-b).extrude(60).translate([0,0,KEY_BOTTOM]),frame(canonical('C')['direction']))
    miss=(probe-s-joint).volume();base=(probe^parts['C']).volume()/probe.volume();plug=(probe^parts['cap']).volume()/probe.volume()
    assert base>.4 and plug>.01,(rec['id'],'paper does not span plug',base,plug)
   else:miss=(probe-s).volume();base=1.;plug=0.
   assert miss<.005,('missing paper backing',rec['id'],miss)
   floor.append(dict(inlay=rec['id'],missing_floor_outside_joint_mm3=miss,base_floor_fraction=base,plug_floor_fraction=plug))
  combined[f]=s+union(inlays)
 report('preserved-mechanism',dict(core_identical=True,pocket_stage_preserves_repaired_mechanism_to_float32_export_precision=preservation,source='Bundled SHA-verified v3.2 meshes with localized completion of both R2 fillet halves on C/K. Spherical bearing lands are preserved away from those rounded edge ends.',rounding_repair=json.loads((CACHE/'rounding-repair.json').read_text()),spherical_retention=meta['spherical_retention']))
 report('paper-backing',floor)
 cells={};bare={}
 for f in ORBITS:cells.update(replicate(combined[f],f));bare.update(replicate(parts[f],f))
 hardware_all=union([ss for n in AXES for ss in hardware(n)]);fixed_mech=parts['core']+hardware_all
 # Driver and plug are removable from outside before paper is glued on.
 n=np.array(canonical('C')['direction']);name=canonical('C')['name'];F=frame(n);female,male=keys()
 nominal=parts['cap']^xform(cross(male).extrude(80).translate([0,0,KEY_BOTTOM-.01]),F)
 fixed=union([s for k,s in cells.items() if k!=name]+[parts['C'],fixed_mech]);contacts=[]
 for distance in np.r_[np.arange(0,3.01,.1),np.arange(3.5,60.01,.5)]:
  hit=(nominal.translate(n*distance)^fixed).volume();crush=(parts['cap'].translate(n*distance)^parts['C']).volume()
  assert hit<.005 and crush<.3,('plug insertion',distance,hit,crush)
  contacts.append([float(distance),float(hit),float(crush)])
 driver=xform(mf.Manifold.cylinder(70,4.79,4.79,96).translate([0,0,SEAT+.02]),F)
 hit=(driver^parts['C']).volume();assert hit<.005,('washer/driver access',hit)
 gap=parts['cap'].min_gap(hardware(n)[0],10);assert gap>2.95
 locking=[]
 for a in [.25,.5,1,2,3,90,180]:
  hit=(xform(nominal,Rotation.from_rotvec(n*np.radians(a)).as_matrix())^parts['C']).volume();locking.append([a,float(hit)])
 assert max(v for a,v in locking if a<=3)>.01 and locking[-2][1]>1 and locking[-1][1]<.005
 report('plug-fit',dict(removal_samples=contacts,head_clearance_mm=gap,driver_diameter_test_mm=9.58,rotational_key_intersections_mm3=locking,friction_ribs_intentional_interference=True,paper_removed_for_service=True))
 print('MECHANISM, POCKETS AND PLUG CHECKS PASSED',flush=True)
 # Capture uses feet below R28.5 only: outer surfaces cannot fake retention.
 capture=[]
 for f,support,lift in [('P','C',.15),('K','P',.8)]:
  row=canonical(f);d=np.array(row['direction']);foot=retaining_foot(bare[row['name']]);F=frame(d)
  fixed=union([v.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*lift) for k,v in bare.items() if k[0]==support])
  for slope in [0,.35,.7,1.2]:
   for theta in ([0] if slope==0 else np.arange(12)*np.pi/6):
    direction=unit(d+slope*(np.cos(theta)*F[:,0]+np.sin(theta)*F[:,1]));cc=curve(foot,direction,fixed,np.arange(0,8.01,.25));ss=summary(cc)
    assert cc[0][1]<.005 and ss['maximum_intersection_mm3']>1,('capture',f,ss)
    capture.append(dict(family=f,support_family=support,support_outward_lift_mm=lift,direction=direction.tolist(),**ss))
 report('capture',dict(probes=capture,scope='Finite straight extraction probes using only actual exported retaining feet. Supported corner test gives every petal 0.8 mm outward play. No force or elastic simulation.'))
 print('CAPTURE PASSED',flush=True)
 layer_checks=[]
 for r in rows:
  if r['family']=='core':continue
  s=from_mesh(trimesh.load(DEST/r['file'],force='mesh'))
  for h,w in [(.16,.42),(.20,.45)]:
   cs=layers(s,h,w);scraps=[c for c in cs[1:] if c['volume_mm3']>.03]
   print('LAYERS',r['family'],h,cs[:3],flush=True);assert not scraps,('layer islands',r['family'],scraps)
   layer_checks.append(dict(family=r['family'],layer_height_mm=h,line_width_mm=w,components=cs))
 report('layer-connectivity',layer_checks)
 items=[cells[r['name']] for r in ROWS];normal=[]
 for axis,n in enumerate(AXES):
  moving=union([cells[r['name']] for r in ROWS if axis in r['signature']]);still=union([cells[r['name']] for r in ROWS if axis not in r['signature']]+[fixed_mech]);worst=[0,0]
  for a in np.arange(0,181,3):
   hit=(xform(moving,Rotation.from_rotvec(n*np.radians(a)).as_matrix())^still).volume()
   if hit>worst[1]:worst=[float(a),float(hit)]
  print('NORMAL',axis,worst,flush=True);assert worst[1]<.005,('normal turn',axis,worst)
  normal.append(dict(axis=axis,sample_step_degrees=3,worst=worst));report('normal-turns',normal)
 seq=json.loads((HERE/'sequence.json').read_text())['sequence'];states=np.tile(np.eye(3),(44,1,1));checks=[]
 for k,step in enumerate(seq):
  chosen=set(step['pieces']);a=step['axis'];angle=step['angle_degrees'];worst=[0,0]
  moving=union([xform(items[i],states[i]) for i in chosen]);still=union([xform(items[i],states[i]) for i in range(44) if i not in chosen]+[fixed_mech])
  for theta in np.linspace(0,angle,49):
   hit=(xform(moving,Rotation.from_rotvec(AXES[a]*np.radians(theta)).as_matrix())^still).volume()
   if hit>worst[1]:worst=[float(theta),float(hit)]
  assert worst[1]<.005,('jumble turn',k,worst)
  q=Rotation.from_rotvec(AXES[a]*np.radians(angle)).as_matrix();states[list(chosen)]=q@states[list(chosen)]
  checks.append(dict(step=k+1,axis=a,angle_degrees=angle,samples=49,worst=worst));print('JUMBLE',k+1,worst,flush=True);report('jumbling',checks)
 walk=json.loads((HERE/'fixed-baseline/jumbling-walk.json').read_text());states=np.tile(np.eye(3),(44,1,1));checks=[]
 for step in walk['checks']:
  chosen={i for i,row in enumerate(ROWS) if row['name'] in step['moving_pieces']};a=step['axis'];angle=step['angle_degrees'];worst=0.
  moving=union([xform(items[i],states[i]) for i in chosen]);still=union([xform(items[i],states[i]) for i in range(44) if i not in chosen]+[fixed_mech])
  for theta in np.linspace(0,angle,7):worst=max(worst,(xform(moving,Rotation.from_rotvec(AXES[a]*np.radians(theta)).as_matrix())^still).volume())
  assert worst<.005,('48 move walk',step['step'],worst)
  q=Rotation.from_rotvec(AXES[a]*np.radians(angle)).as_matrix();states[list(chosen)]=q@states[list(chosen)]
  checks.append(dict(**{k:v for k,v in step.items() if k!='maximum_collision_mm3'},maximum_collision_mm3=worst));report('jumbling-walk',dict(passed=len(checks)==48,checks=checks))
  if step['step']%8==0:print('WALK',step['step'],worst,flush=True)
 report('assembly',dict(basis='Core and spherical-shell mechanism inherited from physically assembled v3.2. Local subtractive C/K fillet completion narrows no assembly route. New plugs are installed from outside after screw adjustment, then paper is fitted.',new_plug_insertion_checked=True,shell_assembly='Assemble floating shell with screwed centers absent or loose, using rotational hooking as on the printed base puzzle. No new glue joints in mechanism.',scope='Inherited physical assembly evidence; no exhaustive numerical shell assembly planner. The 0.5 mm pocket version was printed; the owner reports insufficient inlay guidance. The new 1 mm version is not yet printed.'))
 report('summary',dict(passed=True,delivered_stls_reloaded=True,normal_axes=12,jumbling_demonstration_steps=5,jumbling_walk_steps=48,capture_probes=len(capture),maximum_collision_tolerance_mm3=.005,core_reusable=True,physical_evidence='Original spherical v3.2 printed and built successfully. The owner printed the 0.5 mm inlay version and requested deeper locating pockets. These 1 mm pockets and their regenerated outlines are not yet physically tested.',scope='Finite rigid mesh motion/capture, floor containment, keyed access and layer connectivity checks; no simulation of paper, glue, support scars, wear or elastic forces.'))
 print('ALL VALIDATION PASSED',flush=True)
if __name__=='__main__':run()
