"""Final-STL core, nut-loading, unchanged-envelope and v7 compatibility checks."""
from build import *
import sys,zipfile,xml.etree.ElementTree as ET
from print_3mf import q
report={};meta=json.loads((DEST/'manifest.json').read_text())
def read(r,folder=DEST):
 path=folder/r['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
 m=trimesh.load(path,force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
 t=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 return m,solid(m)
def hit(a,b):return max(0.,float((a^b).volume()))
oldr=json.loads((DEST/'reference/original-core.json').read_text());oldm,old=read(oldr)
# The modification envelope is restricted to the old/new loading-pocket regions.
def old_slot():
 h=5.4/2;e=ENTRY_AF/2;p=mf.CrossSection([[[0,-h],[3.5,-h],[6,-e],[35,-e],[35,e],[6,e],[3.5,h],[0,h]]])
 return (hexagon(5.4)+p).extrude(4.25).translate([0,0,NUT_ROOF-4.25])
nut=hexagon(5.5).extrude(4).translate([0,0,NUT_ROOF-4])-mf.Manifold.cylinder(40,1.5,1.5,72)
bolt=mf.Manifold.cylinder(20,1.5,1.5,96).translate([0,0,8.3])+mf.Manifold.cylinder(3,2.75,2.75,96).translate([0,0,28.3])
cores=[]
for r in meta['parts']:
 m,s=read(r)
 if r['kind']!='core':continue
 af=r['nut_seat_af_mm'];cores.append((r,m,s))
 maximum_radius=float(np.linalg.norm(m.vertices,axis=1).max());planes=(m.vertices@AXES.T).max(axis=0)
 assert maximum_radius<19.20001 and planes.max()<17.60001
 changed=union(xform(old_slot()+slot(af),frame(n)) for n in AXES)
 added=s-old;removed=old-s;outside=(added+removed)-changed
 assert abs(outside.volume())<.003,('outside pocket change',af,outside.volume())
 ports=[]
 gauge=hexagon(af-.1).extrude(3.9).translate([0,0,NUT_ROOF-3.95])
 for i,n in enumerate(AXES):
  f=frame(n);loads=[hit(xform(gauge.translate([d,0,0]),f),s) for d in np.arange(0,25.01,.25)];assert max(loads)<.002
  twists=[hit(xform(nut,f@Rotation.from_euler('z',a,degrees=True).as_matrix()),s) for a in [0,5,10,20,30]]
  assert 0<twists[0]<12 and twists[-1]>twists[0]+1
  assert hit(xform(bolt,f),s)<.002
  # The old washer-bearing pad land and screw bore remain available.
  ring=mf.Manifold.cylinder(.15,3.05,3.05,96).translate([0,0,CORE_PAD-.15])-bore()
  missing=(xform(ring,f)-s).volume();assert abs(missing)<.003
  ports.append(dict(axis=i+1,gauge_af_mm=af-.1,loading_max_overlap_mm3=max(loads),nominal_nut_seated_press_interference_mm3=twists[0],twist_obstruction_mm3=twists,missing_pad_mm3=missing))
 report[f'core-{af:.2f}']=dict(max_radius_mm=maximum_radius,max_pad_coordinates_mm=planes.tolist(),material_added_mm3=added.volume(),material_removed_mm3=removed.volume(),change_outside_nut_pockets_mm3=outside.volume(),nut_roof_thickness_mm=CORE_PAD-NUT_ROOF,ports=ports)
 print('CORE CHECK',af,report[f'core-{af:.2f}'],flush=True)
# A sphere bound proves core clearance for the floating pieces through arbitrary
# centered rotations. C rotors turn about their own fixed screw axes, so their
# minimum axial coordinate proves clearance to the unchanged planar pad.
if len(sys.argv)>1:
 outer=Path(sys.argv[1]);om=json.loads((outer/'manifest.json').read_text());rows={r['name']:r for r in json.loads((outer/'reference/parts.json').read_text())};records=[]
 for r in om['parts']:
  if r['name'] not in rows:continue
  m,s=read(r,outer);row=rows[r['name']];n=np.array(row['direction'])
  if row['family']=='C':
   value=float((m.vertices@n).min());assert value>17.69;rec=dict(name=r['name'],minimum_axial_coordinate_mm=value,nominal_pad_clearance_mm=value-CORE_PAD)
  else:
   _,distance,_=trimesh.proximity.closest_point(m,np.zeros((1,3)));value=float(distance[0]);assert value>19.3
   assert (m.vertices@n).min()>0
   rec=dict(name=r['name'],minimum_radial_distance_mm=value,nominal_sphere_clearance_mm=value-CORE_R)
  assert all(hit(s,c)<.002 for _,_,c in cores)
  records.append(rec)
 report['outer_compatibility']=dict(version=om['version'],manifest_sha256=hashlib.sha256((outer/'manifest.json').read_bytes()).hexdigest(),pieces=records,scope='Actual STL sphere/plane separation bounds; floating parts stay beyond core R19.2 under centered rotations. Screwed centers stay beyond their own pad planes during axial rotation. Outward radial insertion preserves those bounds.')
# Verify that the three print plates contain the exact exported meshes.
meshes={Path(r['file']).stem:trimesh.load(DEST/r['file'],force='mesh') for r in meta['parts']};plates=[]
for path in sorted((DEST/'plates').glob('*.3mf')):
 with zipfile.ZipFile(path) as z:assert z.testzip() is None;model=ET.fromstring(z.read('3D/3dmodel.model'))
 assert model.get('unit')=='millimeter';objects={o.get('id'):o for o in model.find(q('resources'))};count=0
 for item in model.find(q('build')):
  ob=objects[item.get('objectid')];name=ob.get('name');key=name.replace('core-','core-nut-seat-') if name.startswith('core-') else name;m=meshes[key];g=ob.find(q('mesh'))
  v=np.array([[float(p.get(k)) for k in ['x','y','z']] for p in g.find(q('vertices'))]);f=np.array([[int(p.get(k)) for k in ['v1','v2','v3']] for p in g.find(q('triangles'))]);assert np.array_equal(v,m.vertices) and np.array_equal(f,m.faces)
  t=np.array([float(a) for a in item.get('transform').split()]).reshape(4,3);position=v@t[:3]+t[3];assert np.all(position[:,:2]>0) and np.all(position[:,:2]<256) and abs(position[:,2].min())<.005;count+=1
 plates.append(dict(file=path.relative_to(DEST).as_posix(),objects=count,exact_stl_geometry=True))
report.update(passed=True,plates=plates,manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),scope='Finite nut loading and interference checks plus geometric outer clearance bounds. Press fits require real print/hardware testing; not a torque or endurance measurement.')
(DEST/'reports/validation.json').write_text(json.dumps(report,indent=2)+'\n');print('VALIDATION PASSED',flush=True)
