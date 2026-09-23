"""Checks use exported, reloaded STLs in mechanism coordinates."""
from redi_design import *
from shapely.geometry import Polygon,Point
import hashlib,zipfile,xml.etree.ElementTree as ET

MODE=sys.argv[1];DEST=Path(sys.argv[2]);START=time.time()
entries={r['name']:r for r in json.loads((DEST/'manifest.json').read_text())['parts']}
def printed(name):
 r=entries[name];path=DEST/r['file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
 m=trimesh.load(path,force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3]
 return from_mesh(m)
parts={r['name']:printed(r['name']) for r in ROWS};parts['core']=printed('core')
rows={r['name']:r for r in ROWS};report={}
def overlap(a,b):return max(0.,(a^b).volume())
def record(k,v):
 report[k]=v;(DEST/'reports'/f'{MODE}.json').write_text(json.dumps(report,indent=2));print(k,str(v)[:1200],flush=True)
hardware_all=union([p for n in AXES for p in hardware(n)])
LIMIT=.003
record('_inputs',{name:r['sha256'] for name,r in entries.items()})

if MODE=='motion':
 angles=np.unique(np.r_[0,.375,.75,1.125,1.5,np.arange(2,120,2),np.arange(3.37,120,6),120])
 for axis,n in enumerate(AXES):
  names=[r['name'] for r in ROWS if axis in r['signature']]
  moving=union([parts[k] for k in names]);fixed=union([s for k,s in parts.items() if k not in names]+[hardware_all])
  vals=[[float(a),overlap(xform(moving,Rotation.from_rotvec(n*np.radians(a)).as_matrix()),fixed)] for a in angles]
  record(f'axis_{axis+1}',dict(samples=vals,worst=max(vals,key=lambda v:v[1])))
  assert max(v for a,v in vals)<LIMIT
 state={r['name']:(parts[r['name']],tuple(r['signature'])) for r in ROWS}
 for step,axis in enumerate([0,3,5,1,7,2,4,6,0,2,7,5]):
  names=[k for k,(s,sig) in state.items() if axis in sig]
  moving=union([state[k][0] for k in names]);fixed=union([s for k,(s,sig) in state.items() if k not in names]+[parts['core'],hardware_all])
  vals=[[float(a),overlap(xform(moving,Rotation.from_rotvec(AXES[axis]*np.radians(a)).as_matrix()),fixed)] for a in np.r_[0,np.arange(5.37,120,6),120]]
  record(f'scramble_{step+1}',dict(axis=axis+1,samples=vals,worst=max(vals,key=lambda v:v[1])))
  assert max(v for a,v in vals)<LIMIT
  q=Rotation.from_rotvec(AXES[axis]*np.radians(120)).as_matrix()
  for k in names:s,sig=state[k];state[k]=(xform(s,q),mapped(sig,q))

elif MODE=='assembly':
 # All retaining profiles are axially open (rho never decreases along the
 # meridian). A translated group stays inside its own cut, while every
 # remaining piece is outside that cut. Sampling also checks hardware,
 # the spherical hub, finite tessellation, and the actual STL exports.
 p=np.array(profile());assert np.diff(p[:-2,0]).min()>-1e-8
 record('profile_axially_open',True)
 remaining=set(rows);groups=[]
 distances=np.r_[np.arange(0,5,.1),np.arange(5,15,.5),np.arange(15,61,2),80,96]
 for a in range(8):
  names=sorted(k for k in remaining if a in rows[k]['signature']);remaining.difference_update(names)
  moving=union([parts[k] for k in names]);fixed=union([parts[k] for k in remaining]+[parts['core']]+[p for i in range(a+1,8) for p in hardware(AXES[i])])
  vals=[[float(d),overlap(moving.translate(d*AXES[a]),fixed)] for d in distances]
  entry=dict(axis=a+1,pieces=names,worst=max(vals,key=lambda v:v[1]),samples=vals);record(f'remove_group_{a+1}',entry)
  assert max(v for d,v in vals)<LIMIT;groups.append(dict(axis=a+1,pieces=names))
 record('assembly_order',groups[::-1])

elif MODE=='retention':
 ball=mf.Manifold.sphere(30,128);n=np.array(rows['E12']['direction']);e=parts['E12']^ball
 vals=[]
 for lift in [0,.05,.10]:
  fixed=parts['C07'].translate(AXES[6]*lift)+parts['C08'].translate(AXES[7]*lift)+parts['core']
  assert overlap(e,fixed)<LIMIT,('invalid starting configuration',lift)
  for label,v in [('radial',n),('C07_axis',AXES[6]),('C08_axis',AXES[7])]:
   samples=[[float(d),overlap(e.translate(d*v),fixed)] for d in np.arange(0,6.001,.1)]
   contact=next((d for d,vv in samples if vv>LIMIT),None)
   row=dict(corner_lift_mm=lift,direction=label,first_contact_mm=contact,peak_overlap_mm3=max(vv for d,vv in samples));vals.append(row);assert contact is not None
 record('principal',vals)
 rocking=[];pivot=n*24
 for lift in [0,.05,.10]:
  fixed=parts['C07'].translate(AXES[6]*lift)+parts['C08'].translate(AXES[7]*lift)+parts['core']
  assert overlap(e,fixed)<LIMIT,('invalid starting configuration',lift)
  for axis in [np.array([0,0,1]),np.array([1,-1,0])/np.sqrt(2)]:
   for angle in [-10,-5,5,10]:
    hit=None
    for d in np.arange(0,6.001,.1):
     q=Rotation.from_rotvec(axis*np.radians(angle)*min(d/.8,1)).as_matrix()
     if overlap(xform(e,q,pivot-q@pivot+n*d),fixed)>LIMIT:hit=float(d);break
    rocking.append(dict(lift_mm=lift,axis=axis.tolist(),angle_deg=angle,first_contact_mm=hit));assert hit is not None
 record('rocking',rocking)
 all_edges=[]
 for row in ROWS[8:]:
  e=parts[row['name']]^ball;fixed=union([parts[f'C{i+1:02}'] for i in row['signature']]);n=np.array(row['direction'])
  samples=[[float(d),overlap(e.translate(d*n),fixed)] for d in np.arange(0,5.001,.1)]
  hit=next((d for d,v in samples if v>LIMIT),None);assert hit is not None
  all_edges.append(dict(name=row['name'],first_radial_contact_mm=hit))
 record('all_edges',all_edges)

elif MODE=='hardware':
 plastic=union(list(parts.values()));fit=[]
 # A 5.15 mm gauge verifies the entrance path. Actual 5.5 mm nuts press into
 # the final 5.25 mm seat; its deliberate 0.125 mm/side interference is
 # slightly reduced after the successful wavy print, not collision-free fit.
 gauge=hex_section(5.15).extrude(4).translate([0,0,NUT_ROOF-4])
 for i,n in enumerate(AXES):
  F=frame(n);local=xform(parts[f'C{i+1:02}'],F.T);s,w=hardware(n)
  ins=[[float(d),overlap(xform(gauge.translate([d,0,0]),F),parts['core'])] for d in np.arange(0,45.01,.5)]
  assert max(v for d,v in ins)<LIMIT
  seat=mf.CrossSection.circle(4.5,192)-mf.CrossSection.circle(1.81,128)
  missing=(seat-local.slice(SEAT-.06)).area();assert missing<.03,missing
  foot=mf.CrossSection.circle(FOOT_R-.02,128)-mf.CrossSection.circle(BORE_D/2+.02,128)
  missing_foot=(foot-local.slice(FOOT_PLANE+.06)).area();assert missing_foot<.03
  collar=mf.CrossSection.circle(ACCESS_D/2+1.15,192)-mf.CrossSection.circle(ACCESS_D/2+.02,192)
  collar_missing=max((collar-local.slice(z)).area() for z in [SEAT+.1,SEAT+.5,SEAT+.9]);assert collar_missing<.05
  screw_hit=overlap(s,plastic);washer_hit=overlap(w,plastic);assert max(screw_hit,washer_hit)<LIMIT
  driver=xform(mf.Manifold.cylinder(100,1.5,1.5,96).translate([0,0,SEAT+3]),F)
  assert overlap(driver,plastic)<LIMIT
  well_sweep=max(overlap(w.translate(d*n),plastic) for d in np.r_[np.arange(0,10,.25),np.arange(10,70,2)]);assert well_sweep<LIMIT
  fit.append(dict(axis=i+1,nut_gauge_insertion_worst=max(ins,key=lambda v:v[1]),nominal_nut_press_overlap_mm3=overlap(xform(nut_shape(),F),parts['core']),missing_washer_seat_mm2=missing,missing_bearing_foot_mm2=missing_foot,missing_collar_mm2=collar_missing,screw_overlap_mm3=screw_hit,washer_overlap_mm3=washer_hit,washer_insertion_overlap_mm3=well_sweep))
 record('axes',fit)
 record('stack_mm',dict(screw_length=20,washer_thickness=1,screw_tip=SEAT+1-20,washer_seat=SEAT,nut_roof=NUT_ROOF,nut_inner_face=NUT_ROOF-4,tip_past_nut=NUT_ROOF-4-(SEAT+1-20),bearing_plane=FOOT_PLANE,core_flat=CORE_PAD))
 screws=[hardware(n)[0] for n in AXES];hit=max(overlap(a,b) for a,b in itertools.combinations(screws,2));assert hit<LIMIT;record('screw_pair_overlap_mm3',hit)

elif MODE=='strength':
 from section_connectivity import polygons,check
 roots=[]
 for axis in range(3):
  F=np.roll(np.eye(3),axis,axis=1);local=xform(parts['core'],F)
  for sign in [-1,1]:
   checks=[]
   for z in np.arange(20,34.001,.025):
    sec=local.slice(sign*float(z))^mf.CrossSection.square([12,12],True)
    poly=next(p for p in polygons(sec) if p.contains(Point(0,0)))
    checks.append(dict(station_mm=sign*float(z),area_mm2=sec.area(),inscribed_diameter_mm=2*poly.boundary.distance(Point(0,0))))
   worst=min(checks,key=lambda p:p['inscribed_diameter_mm']);roots.append(dict(axis=axis,sign=sign,minimum=worst));assert worst['inscribed_diameter_mm']>2.8
 record('core_roots',roots)
 layer=[]
 for name in list(rows)+['core']:
  r=entries[name];s=from_mesh(trimesh.load(DEST/r['file'],force='mesh'))
  components=check(s);small=components[1:];total=sum(c['volume_mm3'] for c in small)
  record('layers_'+name,dict(layer_height_mm=.16,line_width_mm=.42,components=components,detached_estimated_mm3=total))
  assert total<.10,(name,small)

elif MODE=='ridges':
 from shapely.geometry import LineString
 from shapely.ops import unary_union
 from section_connectivity import polygons
 sections=json.loads((OUT/'ridge-sections.json').read_text())
 assert all(abs(r['fillet_radius_mm']-ROUND_R)<1e-10 for r in sections)
 direction=np.array(rows['E12']['direction']);bed_level=float((mesh(parts['E12']).vertices@direction).min())
 before=load(OUT/'edge-inner-rounded.npz').trim_by_plane(direction,bed_level+.04);measured=[]
 for row in sections[::16]:
  r=row['radius_from_center_mm'];angle=row['half_arc_angle_rad']
  if r<20.5 or r>28:continue
  uc=np.array(row['center_direction']);wc=np.array(row['side_direction']);F=np.array([-wc,[0,0,1],uc])
  level=r*np.cos(row['delta_rad'])
  actual=xform(parts['E12'],F).slice(float(level));raw=xform(before,F).slice(float(level))
  loops=actual.to_polygons()
  if not loops:continue
  boundary=unary_union([LineString(np.vstack([p,p[0]])) for p in loops]);available=unary_union(polygons(raw)).buffer(-.03)
  for angle_sample in np.linspace(-angle*.8,angle*.8,9):
   p=Point([-ROUND_R*np.cos(angle_sample),ROUND_R*np.sin(angle_sample)])
   if not available.contains(p):continue
   distance=boundary.distance(p)
   point3=-wc*p.x+np.array([0,0,1])*p.y+uc*level
   measured.append(dict(radius_from_center_mm=r,angle_rad=float(angle_sample),section_error_mm=float(distance),point_mm=point3.tolist()))
 assert len(measured)>25
 _,distances,_=trimesh.proximity.closest_point(mesh(parts['E12']),np.array([p['point_mm'] for p in measured]))
 for p,distance in zip(measured,distances):p['boundary_error_mm']=float(distance)
 maximum=float(distances.max());record('arc_measurements',measured);assert maximum<.025,maximum
 record('constant_radius_mm',ROUND_R);record('loft_stations',len(sections));record('inner_arc_samples',len(measured))
 record('maximum_measured_inner_arc_error_mm',maximum)
 record('scope','All spherical-section circle radii checked; 3D distances measured on inner arcs through r=28 mm, where the pre-fillet solid contains the target and above the intentional bed flat. Circle ends clipped by other surfaces are excluded.')

elif MODE=='exterior':
 # A finite rounding-tool cap formerly removed four exterior cube tips.
 # Check all eight vertices on the exported parts. Gentle R0.65 exterior
 # rounding remains intentional, so demand proximity, not a sharp vertex.
 meshes={name:mesh(s) for name,s in parts.items()}
 vertices=[]
 for signs in itertools.product([-1,1],repeat=3):
  cube_point=np.array(signs)*SIDE/2;point=R@cube_point;candidates=[]
  for name,m in meshes.items():
   bound=float(np.linalg.norm(m.vertices-point,axis=1).min())
   if bound>1:continue
   tris=m.triangles
   take=np.all(tris.min(axis=1)<=point+bound,axis=1)&np.all(tris.max(axis=1)>=point-bound,axis=1)
   local=trimesh.Trimesh(tris[take].reshape(-1,3),np.arange(3*take.sum()).reshape(-1,3),process=False)
   _,distance,_=trimesh.proximity.closest_point_naive(local,[point])
   candidates.append((float(distance[0]),name))
  assert candidates,('missing cube tip',signs)
  distance,name=min(candidates);assert distance<.85,(signs,name,distance)
  vertices.append(dict(cube_vertex_mm=cube_point.tolist(),piece=name,distance_mm=distance))
 record('cube_vertices',vertices)
 record('allowance_mm',.85)
 record('scope','All eight cube vertices approach the exported surface within 0.85 mm; intentional R0.65 exterior rounding is retained.')

elif MODE=='plates':
 results=[]
 for path in sorted((DEST/'plates').glob('*.3mf')):
  with zipfile.ZipFile(path) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
  ns={'m':root.tag.split('}')[0][1:]};assert root.attrib['unit']=='millimeter'
  objects={o.attrib['id']:o for o in root.findall('m:resources/m:object',ns)};bounds=[]
  for item in root.findall('m:build/m:item',ns):
   obj=objects[item.attrib['objectid']];v=np.array([[float(p.attrib[k]) for k in 'xyz'] for p in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
   t=np.array(list(map(float,item.attrib['transform'].split()))).reshape(4,3);v=v@t[:3]+t[3]
   assert v.min()>-.001 and v.max()<256;bounds.append(np.array([v.min(axis=0),v.max(axis=0)]))
  for a,b in itertools.combinations(bounds,2):assert np.any(np.minimum(a[1,:2],b[1,:2])-np.maximum(a[0,:2],b[0,:2])<0)
  results.append(dict(file=str(path.relative_to(DEST)),objects=len(objects),passed=True))
 record('plates',results)

record('_completion',dict(passed=True,seconds=time.time()-START))
