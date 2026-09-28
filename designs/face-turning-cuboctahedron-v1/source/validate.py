"""Checks reload delivered STL geometry; no physical strength claim is made."""
from hardware import *
from checks import assembly,motion,capture,hit,unit
from structure import inspect
from section_connectivity import check as layer_check
def report(name,data):
 (DEST/'reports'/name).write_text(json.dumps(data,indent=2)+'\n')
def validate():
 meta=json.loads((DEST/'manifest.json').read_text());parts={};printed={}
 for rec in meta['parts']:
  if '/puzzle/' not in rec['file']:continue
  m=trimesh.load(DEST/rec['file'],force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1
  printed[rec['family']]=from_mesh(m);T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];parts[rec['family']]=from_mesh(m)
 cells={}
 for f in ORBITS:cells.update(replicate(parts[f],f))
 c=parts['core']
 report('structure.json',[inspect(parts[f],f) for f in ['T','S']])
 report('assembly.json',assembly(cells,c))
 report('normal-turns.json',motion(cells,c,step=3,all_axes=True))
 report('retention.json',capture(cells,c))
 # Constrain small outward tilts as well as straight extraction rays.
 row=canonical('P');n=np.array(row['direction']);F=frame(n);s=cells[row['name']]
 fixed=union([p.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*.1) if k[0] in ['T','S'] else p for k,p in cells.items() if k!=row['name']]+[c]);rocks=[]
 for side in range(8):
  tangent=np.cos(side*np.pi/4)*F[:,0]+np.sin(side*np.pi/4)*F[:,1];found=None
  for angle in np.arange(.5,20.01,.5):
   q=Rotation.from_rotvec(tangent*np.radians(angle)).as_matrix();moved=xform(s,q,n*.3)
   vol=(moved^fixed).volume()
   if vol>.01:found=dict(degrees=float(angle),intersection_mm3=float(vol));break
  assert found is not None,('free rocking',side);rocks.append(dict(tangent=tangent.tolist(),contact=found))
 report('rocking.json',dict(initial_outward_translation_mm=.3,center_lift_mm=.1,probes=rocks,scope='Sampled tilts about puzzle origin; not an exhaustive escape search.'))
 # Repeated pieces must fit the ordinary-turn destination slots, including
 # the asymmetric triangle/square sides of each petal.
 closure=[]
 for ai,n in enumerate(AXES):
  angle=120 if ai<8 else 90;q=Rotation.from_rotvec(n*np.radians(angle)).as_matrix()
  worst=0.
  for row in ROWS:
   if ai not in row['signature']:continue
   sig=mapped(row['signature'],q);dest=next(r for r in ROWS if tuple(r['signature'])==sig)
   a=xform(cells[row['name']],q);b=cells[dest['name']];diff=abs((a-b).volume())+abs((b-a).volume());worst=max(worst,diff)
  assert worst<.4,('slot mismatch',ai,worst)
  closure.append(dict(axis=ai,maximum_symmetric_difference_mm3=worst))
 report('destination-fit.json',closure)
 nuts=[xform(nut(),frame(n)) for n in AXES];small=hex_section(5.15).extrude(4).translate([0,0,NUT_ROOF-4]);loads=[]
 for ai,n in enumerate(AXES):
  envelope=xform(small,frame(n));others=union([nn for j,nn in enumerate(nuts) if j!=ai]);worst=0.
  for d in np.linspace(0,36,73):worst=max(worst,(envelope.translate(frame(n)[:,0]*d)^(c+others)).volume())
  assert worst<.005,('nut path',ai,worst);loads.append(dict(axis=ai,test_nut_across_flats_mm=5.15,maximum_collision_mm3=float(worst)))
 report('nut-loading.json',loads)
 hw=[union(hardware(i)) for i in range(14)];worst=max(float((hw[i]^hw[j]).volume()) for i,j in itertools.combinations(range(14),2));assert worst<.005
 report('hardware.json',dict(pairs=91,maximum_collision_mm3=worst,washer_outer_diameter_mm=7,washer_thickness_mm=.5,screw='DIN912 M3x20',nut='DIN985 M3'))
 layers=[]
 for f,s in printed.items():
  for h,w in [(.16,.42),(.20,.45)]:
   cs=layer_check(s,h,w);scraps=[cc for cc in cs[1:] if cc['volume_mm3']>.03];print('LAYERS',f,h,cs[:5],flush=True)
   assert not scraps,('layer scraps',f,h,scraps);layers.append(dict(family=f,layer_height_mm=h,line_width_mm=w,components=cs))
 report('printability.json',layers)
 rec=next(r for r in meta['parts'] if r['family']=='stand');m=trimesh.load(DEST/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];tool=from_mesh(m)
 row=canonical('S');n=np.array(row['direction']);fixed=union([s for k,s in cells.items() if k!=row['name']]+[c]);worst=0.
 for d in np.r_[np.arange(0,6,.25),np.arange(6,100,2)]:worst=max(worst,(tool.translate(n*d)^fixed).volume())
 assert worst<.005,('stand',worst);report('stand.json',dict(replaces=row['name'],withdrawal_direction=n.tolist(),maximum_collision_mm3=float(worst)))
 # Optional stand is installed before the petals. Check its effect on all
 # petal insertion paths, since it breaks the assembly's cubic symmetry.
 insertions=[]
 for row in ROWS:
  if row['family']!='P':continue
  n=np.array(row['direction']);s=cells[row['name']];worst=0.
  for d in np.r_[np.arange(0,6,.25),np.arange(6,61,1)]:
   worst=max(worst,(s.translate(n*d)^tool).volume())
  assert worst<.005,('petal vs stand',row['name'],worst)
  insertions.append(dict(petal=row['name'],maximum_collision_mm3=float(worst)))
 report('stand-petal-insertion.json',insertions)
 center_insertions=[]
 for row in ROWS[:14]:
  if row['name']=='S01':continue
  n=np.array(row['direction']);s=cells[row['name']];worst=0.
  for d in np.r_[np.arange(0,6,.25),np.arange(6,61,1)]:
   worst=max(worst,(s.translate(n*d)^tool).volume())
  assert worst<.005,('center vs stand',row['name'],worst)
  center_insertions.append(dict(center=row['name'],maximum_collision_mm3=float(worst)))
 report('stand-center-insertion.json',center_insertions)
 report('summary.json',dict(passed=True,delivery_meshes_reloaded=True,surface_pieces=38,printed_puzzle_parts=39,axes_checked=14,turn_sample_step_degrees=3,washer_root_webs_checked=True,assembly_order=['24 petals','8 triangle centers and 6 square centers'],scope='Finite rigid CAD checks and layer-connectivity model. Physical print, torque, wear and elastic popping untested.'))
 print('VALIDATION COMPLETE',flush=True)
if __name__=='__main__':validate()
