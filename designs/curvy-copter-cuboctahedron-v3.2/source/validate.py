"""Validate reloaded delivery meshes; reports state the finite sampling scope."""
from hardware import *
from checks import assembly,unit
from section_connectivity import check as layer_check
from scipy.spatial import cKDTree
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
def validate():
 meta=json.loads((DEST/'manifest.json').read_text());cells={};parts={}
 for r in meta['parts']:
  if '/puzzle/' not in r['file']:continue
  m=trimesh.load(DEST/r['file'],force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];parts[r['family']]=from_mesh(m)
 for row in ROWS:cells[row['name']]=xform(parts[row['family']],mapping(canonical(row['family'])['signature'],row['signature']))
 c=parts['core'];report={};report['assembly']=dict(status='Insertion sequence not validated; full spherical shoulders retained by user request.',instruction='Assemble the floating shell with the axial centers loose or absent. Do not assume the previous straight petal insertion path works.',source='User explicitly preferred preserving retention to further insertion-path work.')
 (DEST/'reports/assembly.json').write_text(json.dumps(report['assembly'],indent=2)+'\n')
 # Every family is replicated by exact cube rotations, but all twelve axes
 # are tested because the nut loading channels break some core symmetries.
 hardware_all=union([ss for n in AXES for ss in hardware(n)])
 fixed_mechanism=c+hardware_all;motions=[]
 for a,n in enumerate(AXES):
  selected={r['name'] for r in ROWS if a in r['signature']};move=union([v for k,v in cells.items() if k in selected]);stay=union([v for k,v in cells.items() if k not in selected]+[fixed_mechanism]);worst=[0,0]
  for angle in np.arange(0,181,3):
   q=Rotation.from_rotvec(n*np.radians(angle)).as_matrix();vol=(xform(move,q)^stay).volume()
   if vol>worst[1]:worst=[int(angle),float(vol)]
  print('FULL TURN',a,worst,flush=True);motions.append(dict(axis=a,sample_step_degrees=3,worst=worst));assert worst[1]<.005
 (DEST/'reports/normal-turns.json').write_text(json.dumps(motions,indent=2)+'\n')
 seq=json.loads((HERE/'sequence.json').read_text());r=np.tile(np.eye(3),(44,1,1));items=[cells[x['name']] for x in ROWS];jumbles=[];states=[]
 for step,m in enumerate(seq['sequence']):
  chosen=set(m['pieces']);moving=union([xform(items[i],r[i]) for i in chosen]);fixed=union([xform(items[i],r[i]) for i in range(44) if i not in chosen]+[fixed_mechanism]);worst=[0,0]
  for angle in np.linspace(0,m['angle_degrees'],49):
   q=Rotation.from_rotvec(np.radians(angle)*AXES[m['axis']]).as_matrix();v=(xform(moving,q)^fixed).volume()
   if v>worst[1]:worst=[float(angle),float(v)]
  q=Rotation.from_rotvec(np.radians(m['angle_degrees'])*AXES[m['axis']]).as_matrix();r[list(chosen)]=q@r[list(chosen)];states.append(r.copy())
  jumbles.append(dict(step=step+1,axis=m['axis'],angle_degrees=m['angle_degrees'],samples=49,worst=worst));print('JUMBLE',step+1,worst,flush=True);assert worst[1]<.005
 (DEST/'reports/jumbling.json').write_text(json.dumps(jumbles,indent=2)+'\n')
 # Nut insertion checks use a smaller geometric envelope to separate the
 # intended final press fit from obstruction by another installed nut.
 reused_nut_test=False
 if os.environ.get('CUBOCTA_RETENTION_BASELINE'):
  bp=Path(os.environ['CUBOCTA_RETENTION_BASELINE']);oldmeta=json.loads((bp/'manifest.json').read_text())
  import hashlib
  oldrec=next(x for x in oldmeta['parts'] if x['file']=='stl/puzzle/core.stl');newrec=next(x for x in meta['parts'] if x['file']=='stl/puzzle/core.stl')
  assert hashlib.sha256((bp/oldrec['file']).read_bytes()).hexdigest()==hashlib.sha256((DEST/newrec['file']).read_bytes()).hexdigest()
  assert oldmeta['instances']==meta['instances']
  loads=json.loads((bp/'reports/nut-loading.json').read_text());reused_nut_test=True
 if not reused_nut_test:
  nuts=[xform(nut(),frame(n)) for n in AXES];loads=[]
  small=hex_section(5.15).extrude(4).translate([0,0,NUT_ROOF-4.])
  for a,n in enumerate(AXES):
   envelope=xform(small,frame(n));others=union([nn for j,nn in enumerate(nuts) if j!=a]);worst=0
   for distance in np.linspace(0,36,73):worst=max(worst,(envelope.translate(frame(n)[:,0]*distance)^(c+others)).volume())
   assert worst<.005,('nut path',a,worst);loads.append(dict(axis=a,test_nut_af_mm=5.15,maximum_collision_mm3=worst))
 (DEST/'reports/nut-loading.json').write_text(json.dumps(loads,indent=2)+'\n')
 layers=[]
 for row in meta['parts']:
  if '/puzzle/' not in row['file']:continue
  s=from_mesh(trimesh.load(DEST/row['file'],force='mesh'))
  for h,w in [(.16,.42),(.20,.45)]:
   comps=layer_check(s,h,w);scraps=[c for c in comps[1:] if c['volume_mm3']>.03];print('LAYERS',row['family'],h,comps[:4],flush=True)
   assert not scraps,('print scraps',row['family'],h,scraps);layers.append(dict(family=row['family'],layer_height_mm=h,line_width_mm=w,components=comps))
 (DEST/'reports/printability.json').write_text(json.dumps(layers,indent=2)+'\n')
 (DEST/'reports/summary.json').write_text(json.dumps(dict(passed=True,delivery_files_reloaded=True,assembly_validated=False,normal_turn_checks=len(motions),jumbling_steps=len(jumbles),source_scope='Finite motion and mesh checks passed; insertion sequence and physical print/torque not validated.'),indent=2)+'\n')
 print('VALIDATION COMPLETE',flush=True)
if __name__=='__main__':validate()
