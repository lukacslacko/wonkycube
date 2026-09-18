"""Checks on reloaded delivery meshes. No force or lifetime claims."""
from skewb_design import *
from finish_skewb import stand
import sys,hashlib,zipfile,xml.etree.ElementTree as ET
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else WORK/'release'
MODE=sys.argv[1] if len(sys.argv)>1 else 'motion'
META=json.loads((DEST/'manifest.json').read_text());MAN={r['name']:r for r in META['parts']}

def read(name):
 row=MAN[name];path=DEST/row['file'];m=trimesh.load(path,force='mesh')
 assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
 assert m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1
 t=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 return from_mesh(m)
PARTS={r['name']:read(r['name']) for r in ROWS};CORE=read('core')
BOLTS=[hardware(n)[0] for n in AXES];WASHERS=[hardware(n)[1] for n in AXES]
REPORT={}

def record(key,value):
 REPORT[key]=value;(DEST/'reports'/(MODE+'.json')).write_text(json.dumps(REPORT,indent=2));print(key, str(value)[:450],flush=True)
def volume(a,b):return max(0.,float((a^b).volume()))
def test_path(moving,others,axis,angles):
 stationary=union(others);worst=[0.,0.]
 for angle in angles:
  q=Rotation.from_rotvec(np.radians(angle)*axis).as_matrix();v=volume(xform(moving,q),stationary)
  if v>worst[1]:worst=[float(angle),v]
 assert worst[1]<.001,('turn overlap',worst)
 return dict(samples=len(angles),worst=worst)

def motion():
 for axis,n in enumerate(AXES):
  moving=[r['name'] for r in ROWS if axis in r['signature']];fixed=[PARTS[r['name']] for r in ROWS if r['name'] not in moving]+[CORE]+BOLTS+WASHERS
  record(f'axis_{axis}',test_path(union([PARTS[k] for k in moving]),fixed,n,np.arange(0,120.001,3)))
 state=PARTS.copy();sigs={r['name']:tuple(r['signature']) for r in ROWS}
 for step,axis in enumerate([0,1,2,3,1,0,3,2,0,2,1,3,0,1,0,2]):
  n=AXES[axis];moving=[k for k,sig in sigs.items() if axis in sig];fixed=[s for k,s in state.items() if k not in moving]+[CORE]+BOLTS+WASHERS
  record(f'scramble_{step}',test_path(union([state[k] for k in moving]),fixed,n,np.arange(0,120.001,6)))
  q=Rotation.from_rotvec(np.radians(120)*n).as_matrix()
  for k in moving:state[k]=xform(state[k],q);sigs[k]=mapped(sigs[k],q)
  assert sorted(sigs.values())==sorted(tuple(r['signature']) for r in ROWS)


def assembly():
 rank={'K':0,'F':1,'C':2};offsets=np.r_[np.arange(0,8.001,.25),np.arange(9,101,2)]
 jig=read('assembly-stand')
 for row in sorted(ROWS,key=lambda r:(rank[r['family']],r['name'])):
  name=row['name'];n=np.array(row['direction']);others=[s for k,s in PARTS.items() if k!=name and rank[k[0]]<=rank[row['family']]]+[CORE]
  if name!='C01':others.append(jig)
  fixed=union(others);worst=[0.,0.]
  for d in offsets:
   v=volume(PARTS[name].translate(d*n),fixed)
   if v>worst[1]:worst=[float(d),v]
  record('insert_'+name,dict(samples=len(offsets),worst=worst));assert worst[1]<.001
 others=union([s for k,s in PARTS.items() if k!='C01']+[CORE]);worst=[0.,0.]
 for d in offsets:
  v=volume(jig.translate(d*AXES[0]),others)
  if v>worst[1]:worst=[float(d),v]
 record('stand_withdrawal',dict(samples=len(offsets),worst=worst));assert worst[1]<.001


def hardware_check():
 for i,n in enumerate(AXES):
  name=f'C{i+1:02}';s=PARTS[name];bolt,washer=hardware(n);f=frame(n)
  assert volume(bolt,CORE)<.001
  assert volume(bolt,s)<.001 and volume(washer,s)<.001
  for other in BOLTS[i+1:]:assert volume(bolt,other)<.001
  bore=mf.Manifold.cylinder(SEAT-FOOT_PLANE,1.65,1.65,96).translate([0,0,FOOT_PLANE])
  assert volume(xform(bore,f),s)<.001
  for d in np.arange(0,50,.5):assert volume(washer.translate(d*n),s)<.001
  key=mf.Manifold.cylinder(90,1.45,1.45,48).translate([0,0,SEAT+1])
  assert volume(xform(key,f),s)<.001
  # Full washer land and flat bearing annulus, rather than only the screw center.
  seat_ring=(mf.Manifold.cylinder(.20,4.45,4.45,96)-mf.Manifold.cylinder(.20,1.85,1.85,96)).translate([0,0,SEAT-.20])
  foot_ring=(mf.Manifold.cylinder(.20,FOOT_R-.05,FOOT_R-.05,96)-mf.Manifold.cylinder(.20,1.85,1.85,96)).translate([0,0,FOOT_PLANE])
  assert (xform(seat_ring,f)-s).volume()<.003 and (xform(foot_ring,f)-s).volume()<.003
  nut=xform(nut_shape(),f);interference=volume(nut,CORE)
  route=[]
  for d in np.arange(0,16.01,.25):route.append([float(d),volume(nut.translate(f[:,0]*d),CORE)])
  assert max(v for d,v in route if d>=6)<.001
  assert 0<interference<8
  roof=volume(nut.translate(n*.5),CORE)-interference;assert roof>1
  rod=mf.Manifold.cylinder(35,1.5,1.5,64);rod=xform(rod,np.array([[0,0,1],[0,1,0],[-1,0,0]]),[3.25,0,NUT_ROOF-2])
  assert volume(xform(rod,f),CORE)<.001
  twist=[]
  for angle in [0,2,5,10,20,30]:
   twist.append([angle,volume(xform(nut_shape(),f@Rotation.from_euler('z',angle,degrees=True).as_matrix()),CORE)])
  # Additional interference at a half-flat rotation proves geometric keying,
  # not a torque rating: PLA compliance and the actual nut control that.
  assert twist[-1][1]>interference+1
  record(name,dict(seat_interference_mm3=interference,roof_additional_obstruction_mm3=roof,loading=route,rotated_nut_overlap_mm3=twist))
 record('stack_mm',dict(core_radius=CORE_R,flat=CORE_PAD,foot=FOOT_PLANE,washer_seat=SEAT,screw_tip=SEAT+1-20,nut_inner_face=NUT_ROOF-4,tip_beyond_nut=NUT_ROOF-4-(SEAT+1-20)))
 # Check the alternate nut seat cores against the same moving-part envelope.
 for name in ['core-seat-5.30','core-seat-5.50']:
  cr=read(name);assert volume(cr,union(list(PARTS.values())+BOLTS+WASHERS))<.001
  record(name,dict(watertight=True,components=1))


def retention():
 sphere=mf.Manifold.sphere(30,SEG)
 inner={k:s^sphere for k,s in PARTS.items()}
 for row in ROWS:
  if row['family']=='C':continue
  name=row['name'];n=np.array(row['direction']);target=inner[name]
  retainers=[]
  for other in ROWS:
   if other['name']==name:continue
   worst=max(volume(target.translate(d*n),inner[other['name']]) for d in [1.,2.,3.])
   if worst>.05:retainers.append(dict(name=other['name'],max_overlap_mm3=worst))
  fixed=union([s for k,s in inner.items() if k!=name]);first=None
  for d in np.arange(.05,3.001,.05):
   v=volume(target.translate(d*n),fixed)
   if v>.001:first=float(d);break
  assert first is not None and first<1.0,(name,first)
  record('radial_'+name,dict(first_contact_mm=first,retainers=retainers))
 # Probe both floating families against ideal rigid surroundings. These do not
 # claim exhaustive 6-DOF escape or physical holding force.
 for name in ['F01','K01']:
  row=next(r for r in ROWS if r['name']==name);n=np.array(row['direction']);f=frame(n);target=inner[name]
  for lift in [0,.10,.25]:
   fixed=union([s.translate(AXES[int(k[1:])-1]*lift) if k.startswith('C') else s for k,s in inner.items() if k!=name]+[CORE])
   dirs=[n]
   for slope in [.3,.7,1.2]:
    for angle in np.arange(0,360,60):
     tangent=f[:,0]*np.cos(np.radians(angle))+f[:,1]*np.sin(np.radians(angle));d=n+slope*tangent;dirs.append(d/np.linalg.norm(d))
   results=[]
   for d in dirs:
    contact=next((float(t) for t in np.arange(.1,12.01,.1) if volume(target.translate(t*d),fixed)>.001),None)
    assert contact is not None,(name,lift,'unblocked pull',d)
    results.append(contact)
   record(f'pull_{name}_lift_{lift}',dict(directions=len(dirs),first_contacts_mm=results))
   rocks=[]
   pivot=n*22
   for tangent in [f[:,0],f[:,1],(f[:,0]+f[:,1])/np.sqrt(2)]:
    for angle in [-10,-5,5,10]:
     hit=None
     for t in np.arange(.1,12.01,.1):
      a=np.radians(angle)*min(1,t/2);q=Rotation.from_rotvec(tangent*a).as_matrix();moved=xform(target,q,pivot-q@pivot+n*t)
      if volume(moved,fixed)>.001:hit=float(t);break
     assert hit is not None,(name,lift,'unblocked rock',angle)
     rocks.append(hit)
   record(f'rock_{name}_lift_{lift}',dict(paths=len(rocks),first_contacts_mm=rocks))


def plates():
 ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
 results=[]
 for row in META['plates']:
  path=DEST/row['file']
  with zipfile.ZipFile(path) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
  assert root.attrib['unit']=='millimeter';objects={};names=[]
  for obj in root.findall('m:resources/m:object',ns):
   v=np.array([[float(a.attrib[k]) for k in ['x','y','z']] for a in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
   faces=np.array([[int(a.attrib[k]) for k in ['v1','v2','v3']] for a in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
   assert faces.min()>=0 and faces.max()<len(v);objects[obj.attrib['id']]=(obj.attrib['name'],v)
  bounds=[]
  for item in root.findall('m:build/m:item',ns):
   name,v=objects[item.attrib['objectid']];t=np.array(list(map(float,item.attrib['transform'].split()))).reshape(4,3);v=v@t[:3]+t[3]
   b=np.array([v.min(axis=0),v.max(axis=0)]);assert b.min()>-.005 and np.max(b)<256.001
   for prior in bounds:assert not np.all(np.minimum(prior[1,:2],b[1,:2])-np.maximum(prior[0,:2],b[0,:2])>0)
   bounds.append(b);names.append(name)
  assert names==row['objects'];results.append(dict(file=row['file'],objects=names,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 record('plates',results)
 for row in META['orientation_options']:
  with zipfile.ZipFile(DEST/row['file']) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
  obj=root.find('m:resources/m:object',ns)
  v=np.array([[float(a.attrib[k]) for k in ['x','y','z']] for a in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
  faces=np.array([[int(a.attrib[k]) for k in ['v1','v2','v3']] for a in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
  alternate=trimesh.Trimesh(v,faces,process=False);assert alternate.is_watertight and alternate.is_winding_consistent
  t=np.array(row['mechanism_to_print']);v=(v-t[:,3])@t[:,:3]
  normal=trimesh.load(DEST/MAN[row['name']]['file'],force='mesh');t=np.array(MAN[row['name']]['mechanism_to_print']);original=(normal.vertices-t[:,3])@t[:,:3]
  assert np.array_equal(faces,normal.faces)
  difference=float(np.linalg.norm(v-original,axis=1).max());assert difference<1e-10
  assert row['first_layer_0_16_mm_area_mm2']>4
  record('orientation_'+row['name'],dict(max_vertex_distance_mm=difference))

{'motion':motion,'assembly':assembly,'hardware':hardware_check,'retention':retention,'plates':plates}[MODE]()
record('_completion',dict(passed=True,mode=MODE))
