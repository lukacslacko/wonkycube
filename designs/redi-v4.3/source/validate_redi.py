"""Motion, loading, hardware, and capture checks on delivered, reloaded STLs."""
from redi_design import *
import hashlib,zipfile,xml.etree.ElementTree as ET

MODE=sys.argv[1] if len(sys.argv)>1 else 'motion'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else WORK/'release'
entries={r['name']:r for r in json.loads((DEST/'manifest.json').read_text())['parts']}
def printed(name):
 r=entries[name];path=DEST/r['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
 m=trimesh.load(path,force='mesh');t=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 return from_mesh(m)
parts={r['name']:printed(r['name']) for r in ROWS};parts['core']=printed('core')
report={};start=time.time();hw=union([s for n in AXES for s in hardware(n)])
def record(key,value):
 report[key]=value;(DEST/'reports'/f'{MODE}.json').write_text(json.dumps(report,indent=2))
 print(key,value if not isinstance(value,list) or len(value)<5 else f'{len(value)} records',flush=True)
def overlap(a,b):return max(0.,(a^b).volume())

if MODE=='motion':
 for axis,n in enumerate(AXES):
  moving=union([parts[r['name']] for r in ROWS if axis in r['signature']])
  fixed=union([parts[r['name']] for r in ROWS if axis not in r['signature']]+[parts['core'],hw])
  vals=[(ang,overlap(xform(moving,Rotation.from_rotvec(n*np.radians(ang)).as_matrix()),fixed)) for ang in range(0,121,3)]
  record('axis_'+str(axis+1),dict(samples=vals,worst=max(vals,key=lambda p:p[1])))
  assert max(v for a,v in vals)<.003,('turn',axis,max(vals,key=lambda p:p[1]))
 state={r['name']:(parts[r['name']],tuple(r['signature'])) for r in ROWS}
 for step,axis in enumerate([0,3,5,1,7,2,4,6,0,2,7,5]):
  names=[name for name,(s,sig) in state.items() if axis in sig]
  moving=union([state[name][0] for name in names]);fixed=union([s for name,(s,sig) in state.items() if name not in names]+[parts['core'],hw])
  vals=[(ang,overlap(xform(moving,Rotation.from_rotvec(AXES[axis]*np.radians(ang)).as_matrix()),fixed)) for ang in range(0,121,6)]
  record('scramble_'+str(step+1),dict(axis=axis+1,samples=vals,worst=max(vals,key=lambda p:p[1])))
  assert max(v for a,v in vals)<.003,('scramble',step,max(vals,key=lambda p:p[1]))
  q=Rotation.from_rotvec(AXES[axis]*np.radians(120)).as_matrix()
  for name in names:s,sig=state[name];state[name]=(xform(s,q),mapped(sig,q))

elif MODE=='assembly':
 distances=np.r_[np.arange(0,10.001,.25),np.arange(11,65,1),[72,80,96,120]]
 placed=[parts['core']]
 for family in ['E','C']:
  for row in [r for r in ROWS if r['name'].startswith(family)]:
   name=row['name'];n=np.array(row['direction'])
   fixed=union(placed+[parts[r['name']] for r in ROWS if r['name'].startswith(family) and r['name']!=name])
   vals=[(float(d),overlap(parts[name].translate(d*n),fixed)) for d in distances]
   record('insert_'+name,max(vals,key=lambda p:p[1]));assert max(v for d,v in vals)<.003,(name,max(vals,key=lambda p:p[1]))
  placed.extend(parts[r['name']] for r in ROWS if r['name'].startswith(family))
 support=printed('assembly-stand');fixed=union([p for name,p in parts.items() if name!='C01'])
 vals=[(float(d),overlap(support.translate(d*AXES[0]),fixed)) for d in distances]
 record('stand_withdrawal',max(vals,key=lambda p:p[1]));assert max(v for d,v in vals)<.003
 vals=[]
 for row in ROWS:
  if row['name'].startswith('E'):
   vals.extend((row['name'],float(d),overlap(parts[row['name']].translate(d*np.array(row['direction'])),support)) for d in distances)
 record('stand_during_edge_loading',max(vals,key=lambda p:p[2]));assert max(v for name,d,v in vals)<.003
 screw,washer=hardware(AXES[0],STAND_SEAT-SEAT)
 stand_hardware_overlap=overlap(screw+washer,support+parts['core'])
 record('stand_hardware',dict(washer_seat_mm=STAND_SEAT,screw_tip_mm=STAND_SEAT+1-20,tip_past_nut_mm=NUT_ROOF-4-(STAND_SEAT+1-20),overlap_mm3=stand_hardware_overlap))
 assert stand_hardware_overlap<.003 and NUT_ROOF-4-(STAND_SEAT+1-20)>.75

elif MODE=='hardware':
 bare=core(False);nut=nut_shape();allplastic=union(list(parts.values()));fit=[]
 for i,n in enumerate(AXES):
  f=frame(n);c=parts[f'C{i+1:02}'];local=xform(c,f.T);s,w=hardware(n)
  vals=[(float(d),overlap(xform(nut.translate([d,0,0]),f),bare)) for d in np.arange(0,30.001,.25)]
  assert max(v for d,v in vals)<.003
  nutcapture=overlap(xform(nut.translate([0,0,.5]),f),bare);assert nutcapture>1
  washer=mf.CrossSection.circle(4.5,192)-mf.CrossSection.circle(1.81,144)
  missingseat=(washer-local.slice(SEAT-.05)).area();assert missingseat<.01,missingseat
  foot=mf.CrossSection.circle(FOOT_R-.02,144)-mf.CrossSection.circle(BORE_D/2+.02,144)
  missingfoot=(foot-local.slice(FOOT_PLANE+.05)).area();assert missingfoot<.01,missingfoot
  collar=mf.CrossSection.circle(ACCESS_D/2+1.2,192)-mf.CrossSection.circle(ACCESS_D/2+.01,192)
  missingcollar=max((collar-local.slice(z)).area() for z in np.arange(SEAT+.05,SEAT+1,.2));assert missingcollar<.03,missingcollar
  driver=xform(mf.Manifold.cylinder(100,1.5,1.5,96).translate([0,0,SEAT+3]),f)
  driveroverlap=overlap(driver,allplastic);assert driveroverlap<.003
  screwcollision=overlap(s,allplastic);washercollision=overlap(w,allplastic);assert max(screwcollision,washercollision)<.003
  washersweep=max(overlap(w.translate(n*d),allplastic) for d in np.r_[np.arange(0,8,.25),np.arange(8,61,2)]);assert washersweep<.003
  fit.append(dict(axis=i+1,nut_insertion_worst=max(vals,key=lambda p:p[1]),nut_capture_overlap_mm3=nutcapture,crush_rib_overlap_mm3=overlap(xform(nut,f),parts['core']),missing_washer_seat_mm2=missingseat,missing_bearing_foot_mm2=missingfoot,missing_1_2_mm_collar_mm2=missingcollar,driver_overlap_mm3=driveroverlap,screw_overlap_mm3=screwcollision,washer_overlap_mm3=washercollision,washer_loading_overlap_mm3=washersweep))
 record('axes',fit)
 screws=[hardware(n)[0] for n in AXES];pair=max(overlap(a,b) for a,b in itertools.combinations(screws,2));assert pair<.003
 record('screw_pair_overlap_mm3',pair)
 record('bearing_clamp',[(d,overlap(parts['C01'].translate(-d*AXES[0]),parts['core'])) for d in [0,.05,.10,.11,.15]])
 record('stack_mm',dict(core_radius=CORE_R,core_flat=CORE_PAD,foot=FOOT_PLANE,washer_seat=SEAT,washer_thickness=1,head_underside=SEAT+1,screw_tip=SEAT+1-20,nut_roof=NUT_ROOF,nut_inner_face=NUT_ROOF-4,tip_past_nut=NUT_ROOF-4-(SEAT+1-20)))

elif MODE=='retention':
 inner=mf.Manifold.sphere(INNER_WORK,192)
 e=parts['E12']^inner;a=AXES[7];b=AXES[6];n=(a+b)/np.linalg.norm(a+b)
 principal=[]
 for name,axis,other in [('C08',a,b),('C07',b,a)]:
  for lift in [0,.10,.25]:
   c=parts[name].translate(axis*lift)
   for label,vec in [('radial',n),('own_axis',axis),('other_axis',other)]:
    vals=[(float(d),overlap(e.translate(vec*d),c)) for d in np.arange(0,8.001,.1)]
    first=next((d for d,v in vals if v>.001),None)
    principal.append(dict(retainer=name,corner_lift_mm=lift,direction=label,first_contact_mm=first,peak_overlap_mm3=max(v for d,v in vals)))
 record('principal',principal);assert all(p['first_contact_mm'] is not None for p in principal)
 rocking=[];pivot=n*(28*SCALE)
 for lift in [0,.10,.25]:
  fixed=union([parts['C08'].translate(a*lift),parts['core']])
  for label,axis in [('toward_corners',np.cross(n,[0,0,1])),('sideways',np.array([0,0,1]))]:
   axis=axis/np.linalg.norm(axis)
   for angle in [-10,-5,0,5,10]:
    for dname,vec in [('radial',n),('other_axis',b)]:
     first=None
     for distance in np.arange(0,8.001,.1):
      q=Rotation.from_rotvec(axis*np.radians(angle)*min(distance/.8,1)).as_matrix()
      if overlap(xform(e,q,pivot-q@pivot+vec*distance),fixed)>.001:first=float(distance);break
     rocking.append(dict(corner_lift_mm=lift,rock_axis=label,angle_deg=angle,pull_direction=dname,first_contact_mm=first))
 record('rocking',rocking);assert all(p['first_contact_mm'] is not None for p in rocking)
 all_edges=[]
 for row in ROWS:
  if row['name'][0]!='E':continue
  s=parts[row['name']]^inner;direction=np.array(row['direction']);hits=[]
  for axis in row['signature']:
   c=parts[f'C{axis+1:02}'];vals=[(float(d),overlap(s.translate(direction*d),c)) for d in np.arange(0,6.001,.1)]
   hits.append(next((d for d,v in vals if v>.001),None))
  all_edges.append(dict(name=row['name'],first_radial_contact_each_retainer_mm=hits));assert None not in hits
 record('all_edges',all_edges)

elif MODE=='plates':
 checks=[]
 for path in sorted((DEST/'plates').glob('*.3mf')):
  with zipfile.ZipFile(path) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
  ns={'m':root.tag.split('}')[0][1:]};assert root.attrib['unit']=='millimeter'
  objects={o.attrib['id']:o for o in root.findall('m:resources/m:object',ns)};bounds=[]
  for item in root.findall('m:build/m:item',ns):
   obj=objects[item.attrib['objectid']];v=np.array([[float(p.attrib[k]) for k in 'xyz'] for p in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
   fs=np.array([[int(p.attrib[k]) for k in ['v1','v2','v3']] for p in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
   assert fs.min()>=0 and fs.max()<len(v)
   t=np.array(list(map(float,item.attrib['transform'].split()))).reshape(4,3);v=v@t[:3]+t[3]
   assert v.min()>-.001 and v.max()<256
   bounds.append(np.array([v.min(axis=0),v.max(axis=0)]))
  for aa,bb in itertools.combinations(bounds,2):assert np.any(np.minimum(aa[1,:2],bb[1,:2])-np.maximum(aa[0,:2],bb[0,:2])<0)
  checks.append(dict(file=str(path.relative_to(DEST)),objects=len(objects),passed=True,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 record('plates',checks)

record('_completion',dict(passed=True,seconds=time.time()-start))
print('PASS',MODE,time.time()-start,flush=True)
