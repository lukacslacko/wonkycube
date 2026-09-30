"""Checks on the actual exported STL meshes, with explicitly finite coverage."""
from design import *
from legacy_core import hardware, nut_shape, NUT_ROOF
import sys,hashlib
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else DEST
MODE=sys.argv[1] if len(sys.argv)>1 else 'motion'
META=json.loads((DEST/'manifest.json').read_text());MAN={r['name']:r for r in META['parts']}
BASE={r['name']:r for r in ROWS}
REPORT={'manifest_sha256':hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),'scope':'Finite rigid geometry checks; no physical force, friction or endurance measurement.'}

def read(name):
 rec=MAN[name];path=DEST/rec['file'];m=trimesh.load(path,force='mesh')
 assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['sha256']
 assert m.is_watertight and m.is_winding_consistent and m.volume>0 and len(m.split())==1,name
 t=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 return from_mesh(m)

PARTS={r['name']:read(r['name']) for r in ROWS};CORE=read('core')
BOLTS=[hardware(n)[0] for n in AXES];WASHERS=[hardware(n)[1] for n in AXES]
def volume(a,b):return max(0.,float((a^b).volume()))
def record(key,value):
 REPORT[key]=value;(DEST/'reports'/(MODE+'.json')).write_text(json.dumps(REPORT,indent=2));print(key,str(value)[:500],flush=True)

def turn(state,sigs,axis,depth,angles):
 n=AXES[axis];names=[k for k,sig in sigs.items() if sig[axis]>=depth]
 moving=union([state[k] for k in names]);fixed=union([s for k,s in state.items() if k not in names]+[CORE]+BOLTS+WASHERS)
 worst=[0.,0.]
 for angle in angles:
  q=Rotation.from_rotvec(np.radians(angle)*n).as_matrix();v=volume(xform(moving,q),fixed)
  if v>worst[1]:worst=[float(angle),v]
 assert worst[1]<.002,('turn collision',axis,depth,worst)
 return dict(axis=axis,depth=depth,steps=len(angles),worst=worst,moving=names)

def motion():
 sigs={r['name']:tuple(r['signature']) for r in ROWS}
 for axis in range(4):
  for depth in [1,2]:record(f'solved_{axis}_{depth}',turn(PARTS,sigs,axis,depth,np.arange(0,120.01,3)))
 state=PARTS.copy()
 sequence=[(0,1),(1,2),(2,1),(3,2),(1,1),(0,2),(3,1),(2,2),(0,1),(2,1),(1,2),(3,1),(2,2),(0,2),(3,2),(1,1)]
 for step,(axis,depth) in enumerate(sequence):
  record(f'scramble_{step}',turn(state,sigs,axis,depth,np.arange(0,120.01,10)))
  q=Rotation.from_rotvec(np.radians(120)*AXES[axis]).as_matrix()
  for k in state:
   if sigs[k][axis]>=depth:state[k]=xform(state[k],q);sigs[k]=mapped(sigs[k],q)
  assert sorted(sigs.values())==sorted(tuple(r['signature']) for r in ROWS)

def assembly():
 jig=read('assembly-stand');jighardware=union(list(hardware(AXES[0],28.5-SEAT)))
 fine=np.r_[np.arange(0,12.01,.20),np.arange(13,81,1)]
 def sweep(key,target,fixed,n):
  values=[[float(d),volume(target.translate(d*n),fixed)] for d in fine]
  worst=max(values,key=lambda v:v[1]);record(key,dict(samples=len(values),worst=worst))
  assert worst[1]<.002,(key,worst)
 # Every piece of one family can be inserted radially with every other
 # member of that family and all inner families already in place.
 for layer,family in enumerate('FEW'):
  for row in [r for r in ROWS if r['family']==family]:
   name=row['name'];fixed=union([s for k,s in PARTS.items() if k!=name and k[0] in 'FEW'[:layer+1]]+[CORE,jig,jighardware])
   sweep('insert_'+name,PARTS[name],fixed,np.array(row['direction']))
 for row in [r for r in ROWS if r['family']=='C']:
  name=row['name'];i=row['signature'].index(2)
  fixed=union([s for k,s in PARTS.items() if k!=name]+[CORE]+[h for j in range(1,4) if j!=i for h in [BOLTS[j],WASHERS[j]]]+([jig,jighardware] if i else []))
  sweep('insert_'+name,PARTS[name],fixed,np.array(row['direction']))
 fixed=union([s for k,s in PARTS.items() if k!='C01']+[CORE]+[h for j in range(1,4) for h in [BOLTS[j],WASHERS[j]]])
 sweep('stand_withdrawal',jig,fixed,AXES[0])
 record('order',['F01-F04','E01-E06','W01-W12','C02-C04','remove stand if used','C01'])

def hardware_check():
 for i,n in enumerate(AXES):
  name=f'C{i+1:02}';s=PARTS[name];bolt,washer=hardware(n);f=frame(n)
  assert volume(bolt,CORE)<.002 and volume(bolt,s)<.002 and volume(washer,s)<.002
  assert all(volume(bolt,b)<.002 for b in BOLTS[i+1:])
  assert all(volume(washer.translate(d*n),s)<.002 for d in np.arange(0,60,.5))
  ring=(mf.Manifold.cylinder(.2,4.45,4.45,96)-mf.Manifold.cylinder(.2,1.85,1.85,96)).translate([0,0,SEAT-.2])
  foot=(mf.Manifold.cylinder(.2,FOOT_R-.05,FOOT_R-.05,96)-mf.Manifold.cylinder(.2,1.85,1.85,96)).translate([0,0,FOOT_PLANE])
  assert (xform(ring,f)-s).volume()<.004 and (xform(foot,f)-s).volume()<.004
  key=xform(mf.Manifold.cylinder(100,1.45,1.45,48).translate([0,0,SEAT+1]),f)
  assert volume(key,s)<.002
  nut=xform(nut_shape(),f);fit=volume(nut,CORE)
  path=[[float(d),volume(nut.translate(f[:,0]*d),CORE)] for d in np.arange(0,20.01,.5)]
  assert max(v for d,v in path if d>=6)<.002 and 0<fit<8
  twists=[[a,volume(xform(nut_shape(),f@Rotation.from_euler('z',a,degrees=True).as_matrix()),CORE)] for a in [0,5,10,20,30]]
  assert twists[-1][1]>fit+1 and volume(nut.translate(.5*n),CORE)>fit+1
  rod=mf.Manifold.cylinder(35,1.5,1.5,64);rod=xform(rod,np.array([[0,0,1],[0,1,0],[-1,0,0]]),[3.25,0,NUT_ROOF-2])
  assert volume(xform(rod,f),CORE)<.002
  # A generous washer collar protects the root from the large access well.
  collar=(mf.Manifold.cylinder(2,5.4,5.4,96)-mf.Manifold.cylinder(2,1.85,1.85,96)).translate([0,0,SEAT-2])
  collar_missing=float((xform(collar,f)-s).volume())
  assert collar_missing<.005,(name,'washer collar',collar_missing)
  upper=(mf.Manifold.cylinder(2.6,6.25,6.25,96)-mf.Manifold.cylinder(2.6,4.9,4.9,96)).translate([0,0,SEAT])
  upper_missing=float((xform(upper,f)-s).volume());assert upper_missing<.005,(name,'upper access wall',upper_missing)
  record(name,dict(nut_interference_mm3=fit,nut_loading=path,twist_interference_mm3=twists,washer_collar_min_height_mm=2,washer_collar_outer_diameter_mm=10.8,upper_access_wall_mm=1.6))
 record('stack',dict(core_radius=CORE_R,bearing=CORE_PAD,foot=FOOT_PLANE,washer_seat=SEAT,screw_tip=SEAT+1-20,nut_inner=NUT_ROOF-4,tip_beyond_nut=(NUT_ROOF-4)-(SEAT+1-20)))

def retention():
 inner={k:s^mf.Manifold.sphere(35,SEG) for k,s in PARTS.items()}
 for row in ROWS:
  name=row['name']
  if name[0]=='C':continue
  n=np.array(row['direction']);fixed=union([s for k,s in inner.items() if k!=name])
  contact=next((float(t) for t in np.arange(.05,3.01,.05) if volume(inner[name].translate(t*n),fixed)>.002),None)
  assert contact is not None and contact<=1.25,(name,contact)
  record('radial_'+name,dict(first_contact_mm=contact))
 for name in ['W01','E01','F01']:
  row=BASE[name];n=np.array(row['direction']);f=frame(n);target=inner[name];pivot=n*26
  for lift in [0,.1,.25]:
   fixed=union([s.translate(np.array(BASE[k]['direction'])*lift) if k[0]=='C' else s for k,s in inner.items() if k!=name]+[CORE]);dirs=[n]
   for slope in [.3,.7,1.2]:
    for a in np.arange(0,360,60):
     tangent=f[:,0]*np.cos(np.radians(a))+f[:,1]*np.sin(np.radians(a));d=n+slope*tangent;dirs.append(d/np.linalg.norm(d))
   hits=[]
   for d in dirs:
    hit=next((float(t) for t in np.arange(.1,10.01,.2) if volume(target.translate(t*d),fixed)>.002),None)
    assert hit is not None,(name,lift,'escape',d);hits.append(hit)
   rocks=[]
   for tangent in [f[:,0],f[:,1]]:
    for a in [-10,-5,5,10]:
     hit=None
     for t in np.arange(.1,10.01,.2):
      q=Rotation.from_rotvec(tangent*np.radians(a)*min(1,t/2)).as_matrix()
      if volume(xform(target,q,pivot-q@pivot+n*t),fixed)>.002:hit=float(t);break
     assert hit is not None,(name,lift,'rock escape',a);rocks.append(hit)
   record(f'pulls_{name}_lift{lift}',dict(translation_contacts_mm=hits,rock_contacts_mm=rocks))

def midturn():
 # Check the intended holder family directly at each turn phase, using only
 # the captured foot. The family hierarchy then leads to a screw by design.
 feet={k:s^mf.Manifold.sphere(FOOT_LIMITS[k[0]],SEG) for k,s in PARTS.items() if k[0]!='C'}
 bodies={k:s^mf.Manifold.sphere(33.2,SEG) for k,s in PARTS.items()}
 for depth in [1,2]:
  moving=[r['name'] for r in ROWS if r['signature'][0]>=depth]
  for angle in np.arange(0,120.01,10):
   q=Rotation.from_rotvec(np.radians(angle)*AXES[0]).as_matrix();state={k:xform(s,q) if k in moving else s for k,s in bodies.items()}
   holders={f:union(s for k,s in state.items() if k[0]==f) for f in 'CWE'};records={}
   for name,foot in feet.items():
    n=np.array(BASE[name]['direction']);target=xform(foot,q) if name in moving else foot;n=q@n if name in moving else n
    holder={'W':'C','E':'W','F':'E'}[name[0]];fixed=holders[holder]
    trace=[[float(t),volume(target.translate(t*n),fixed)] for t in np.arange(0,2.01,.1)]
    hit=next((t for t,v in trace if v>.002),None);peak=max(v for t,v in trace)
    assert hit is not None and hit<1.1 and peak>5,(depth,angle,name,hit,peak)
    records[name]=dict(holder_family=holder,first_contact_mm=hit,peak_obstruction_mm3=peak)
   record(f'capture_{depth}_{angle:g}',dict(pieces=records,all_feet_captured_by_intended_family=True))

def printability():
 from section_connectivity import check
 for row in ROWS:
  rec=MAN[row['name']];s=from_mesh(trimesh.load(DEST/rec['file'],force='mesh'))
  for height,width in [(.16,.42),(.20,.45)]:
   result=check(s,height,width)
   record(f"{row['name']}_{height}",result)
   assert len(result)==1,(row['name'],'printable islands',height,result)

def feet():
 for row in ROWS:
  name=row['name'];f=row['family']
  if f=='C':continue
  radius=FOOT_LIMITS[f];holder={'W':'C','E':'W','F':'E'}[f]
  foot=PARTS[name]^mf.Manifold.sphere(radius,SEG);n=np.array(row['direction'])
  assert foot.volume()>30
  values=[]
  for lift in [0,.15,.30]:
   fixed=union(s.translate(lift*np.array(BASE[k]['direction'])) for k,s in PARTS.items() if k[0]==holder)
   trace=[[float(d),volume(foot.translate(d*n),fixed)] for d in np.arange(0,3.01,.1)]
   hit=next((d for d,v in trace if v>.002),None);peak=max(v for d,v in trace)
   assert hit is not None and hit<1.2 and peak>20,(name,lift,hit,peak)
   values.append(dict(support_outward_shift_mm=lift,first_contact_mm=hit,peak_obstruction_mm3=peak))
  record(name,dict(foot_radius_mm=radius,foot_volume_mm3=foot.volume(),held_by=holder,pulls=values))
 record('scope','Isolated retaining feet against displaced supporting family; no exterior surfaces counted. Finite geometric obstruction, not a force prediction.')

{'motion':motion,'assembly':assembly,'hardware':hardware_check,'retention':retention,'midturn':midturn,'printability':printability,'feet':feet}[MODE]()
record('_completion',dict(passed=True,mode=MODE))
