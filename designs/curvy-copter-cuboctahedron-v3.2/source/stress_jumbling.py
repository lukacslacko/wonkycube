from hardware import *
from arc_engine import Puzzle
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
class ExactPuzzle(Puzzle):
 def __init__(self):
  self.f={'key':'cubocta'};self.v=CONFIG;self.U=AXES.copy();self.alpha=np.pi/4;self.h=1/np.sqrt(2);self.N=44;self.axes=self.U.copy();self.seeds=np.array([p['seed'] for p in CONFIG['pieces']]);self.seeds/=np.linalg.norm(self.seeds,axis=1)[:,None];self.masks=[-1]+[p['mask'] for p in CONFIG['pieces']];self.lookup={m:i for i,m in enumerate(self.masks[1:])};self.arcs=None;self.extent_cache={};self.arc_arrays={}
 def locate(self,p):
  p=np.asarray(p)/np.linalg.norm(p);m=sum(1<<int(i) for i in np.flatnonzero(self.U@p>self.h+1e-11));return self.lookup.get(m,-1)
def run():
 reuse=None
 if os.environ.get('CUBOCTA_RETENTION_BASELINE'):
  bp=Path(os.environ['CUBOCTA_RETENTION_BASELINE']);oldmeta=json.loads((bp/'manifest.json').read_text());newmeta=json.loads((DEST/'manifest.json').read_text());assert oldmeta['instances']==newmeta['instances']
  import hashlib
  for family in ['C','P','core']:
   o=next(x for x in oldmeta['parts'] if x['family']==family and '/puzzle/' in x['file']);n=next(x for x in newmeta['parts'] if x['family']==family and '/puzzle/' in x['file'])
   assert hashlib.sha256((bp/o['file']).read_bytes()).hexdigest()==hashlib.sha256((DEST/n['file']).read_bytes()).hexdigest()
  reuse=json.loads((bp/'reports/jumbling-walk.json').read_text());assert reuse['passed']
 p=ExactPuzzle();rng=np.random.default_rng(2709);states=np.tile(np.eye(3),(44,1,1));stage=os.environ.get('CUBOCTA_STRESS_STAGE','printed')
 if stage=='printed':
  items=[load(CACHE/'printed'/(r['name']+'.npz')) for r in ROWS];fixed_mechanism=load(CACHE/'printed-core.npz')+union([s for n in AXES for s in hardware(n)])
 else:
  cells=get(stage);items=[cells[r['name']] for r in ROWS];fixed_mechanism=mf.Manifold()
 theta=np.degrees(np.arccos(1/3));last=-1;report=[];retention=[]
 for k in range(48):
  legal=dict(p.legal(states));choices=[a for a in legal if a!=last] or list(legal);a=int(rng.choice(choices));angle=float(rng.choice([theta,-theta,180.,180-theta,theta-180.]));chosen=set(legal[a]);last=a
  moving=union([xform(items[i],states[i]) for i in chosen]);still=union([xform(items[i],states[i]) for i in range(44) if i not in chosen]+[fixed_mechanism]);worst=0.
  for fraction in np.linspace(0,1,7):
   q=Rotation.from_rotvec(AXES[a]*np.radians(angle*fraction)).as_matrix();worst=max(worst,(xform(moving,q)^still).volume())
  assert worst<.005,('jumble collision',k,a,angle,worst)
  q=Rotation.from_rotvec(AXES[a]*np.radians(angle)).as_matrix();states[list(chosen)]=q@states[list(chosen)]
  if stage=='printed' and k in [7,15,23,31,39,47]:
   posed=[xform(s,states[i]) for i,s in enumerate(items)]
   for i,row in enumerate(ROWS):
    if row['family']=='C':continue
    if row['family']=='P' and reuse is not None:
     retention.append(next(r for r in reuse['radial_extraction_probes'] if r['after_step']==k+1 and r['name']==row['name']));continue
    direction=states[i]@row['direction']
    family=row['family'];support_family='C' if family=='P' else 'P';lift=.15 if family=='P' else .8
    fixed=union([s.translate((np.array(ROWS[j]['direction']) if support_family=='C' else states[j]@ROWS[j]['direction'])*lift) for j,s in enumerate(posed) if ROWS[j]['family']==support_family])
    foot=posed[i]^mf.Manifold.sphere(SHOULDER_R,SEG)
    cc=[(float(d),max(0.,(foot.translate(direction*d)^fixed).volume())) for d in np.arange(0,6.01,.5)]
    assert cc[0][1]<.005,('initial foot overlap',k+1,row['name'],cc[0])
    peak=max(v for d,v in cc);found=next((d for d,v in cc if v>.01),None)
    assert peak>(2 if family=='P' else 5),('walk weak capture',k+1,row['name'],peak)
    retention.append(dict(after_step=k+1,name=row['name'],support_family=support_family,support_outward_displacement_mm=lift,radial_contact_mm=found,maximum_intersection_mm3=peak))
   print('WALK RETENTION',k+1,'anchor/support-specific probes passed',flush=True)
  report.append(dict(step=k+1,axis=a,angle_degrees=angle,moving_pieces=[ROWS[i]['name'] for i in sorted(chosen)],legal_axis_count=len(legal),samples=7,maximum_collision_mm3=worst));print('WALK',k+1,a,round(angle,3),len(legal),worst,flush=True)
  reportpath=(DEST/'reports/jumbling-walk.json') if stage=='printed' else WORK/(stage+'-jumbling-walk.json')
  reportpath.write_text(json.dumps(dict(seed=2709,completed_steps=k+1,passed=k==47,checks=report,radial_extraction_probes=retention,scope='One finite legal jumbling walk; sampled rigid extraction, not exhaustive state-space or escape-path coverage.'),indent=2)+'\n')
if __name__=='__main__':run()
