"""Anchor-only petal capture; supported-corner and collective-motion probes.

Collision volume is a geometric obstruction metric, not a force rating. Tests
sample a finite set of rigid paths. Actual FDM retention needs the test patch.
"""
from hardware import *
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))

def load_parts():
 meta=json.loads((DEST/'manifest.json').read_text());parts={}
 for r in meta['parts']:
  if '/puzzle/' not in r['file']:continue
  m=trimesh.load(DEST/r['file'],force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];parts[r['family']]=from_mesh(m)
 cells={}
 for f in ORBITS:cells.update(replicate(parts[f],f))
 return cells,parts['core']

def curve(s,n,fixed,distances):
 return [[float(d),max(0.,float((s.translate(n*d)^fixed).volume()))] for d in distances]
def summary(c):return dict(first_contact_mm=next((d for d,v in c if v>.01),None),maximum_intersection_mm3=max(v for d,v in c),peak_at_mm=max(c,key=lambda p:p[1])[0])
def unit(v):return v/np.linalg.norm(v)
def retaining_foot(s):
 # Ignore the outer body and upper return entirely. With shifted supports
 # those can overlap initially and would create spurious "retention".
 # Using only the material below the spherical shoulder tests the foot.
 return s^mf.Manifold.sphere(SHOULDER_R,SEG)

def run():
 cells,core_part=load_parts();reuse=None;reuse_inputs=None
 if os.environ.get('CUBOCTA_RETENTION_BASELINE'):
  bp=Path(os.environ['CUBOCTA_RETENTION_BASELINE']);oldmeta=json.loads((bp/'manifest.json').read_text());newmeta=json.loads((DEST/'manifest.json').read_text())
  import hashlib
  reuse_inputs={}
  assert oldmeta['instances']==newmeta['instances']
  for family in ['C','P','core']:
   oldrec=next(x for x in oldmeta['parts'] if x['family']==family and '/puzzle/' in x['file']);newrec=next(x for x in newmeta['parts'] if x['family']==family and '/puzzle/' in x['file'])
   oh=hashlib.sha256((bp/oldrec['file']).read_bytes()).hexdigest();nh=hashlib.sha256((DEST/newrec['file']).read_bytes()).hexdigest();assert oh==nh,(family,'not eligible for reuse')
   assert oldrec['mechanism_to_print']==newrec['mechanism_to_print'];reuse_inputs[family]=nh
  reuse=json.loads((bp/'reports/retention-spherical.json').read_text())
 items=[cells[r['name']] for r in ROWS];feet=[retaining_foot(s) for s in items];states=[('solved',np.tile(np.eye(3),(len(ROWS),1,1)))];seq=json.loads((HERE/'sequence.json').read_text());r=states[0][1].copy()
 for k,m in enumerate(seq['sequence']):
  q=Rotation.from_rotvec(np.radians(m['angle_degrees'])*AXES[m['axis']]).as_matrix();r[m['pieces']]=q@r[m['pieces']];states.append((f'jumble-step-{k+1}',r.copy()))
 a=canonical('C')['signature'][0]
 for angle in [35.26438968,90.,135.]:
  q=Rotation.from_rotvec(np.radians(angle)*AXES[a]).as_matrix();r=states[0][1].copy()
  for j,row in enumerate(ROWS):
   if a in row['signature']:r[j]=q
  states.append((f'axis-{a+1}-angle-{angle:g}',r))
 records=[];corner_records=[];detail=[];directions=[];collective=[]
 for label,r in states:
  posed=[xform(s,r[i]) for i,s in enumerate(items)]
  # Core stays fixed; centered screws lifted 0.15 mm for adjustment margin.
  anchors=union([s.translate(np.array(ROWS[i]['direction'])*.15) for i,s in enumerate(posed) if ROWS[i]['family']=='C']+[core_part])
  # Corner obstruction checked after giving ALL retaining petals 0.8 mm of
  # radial play, rather than treating them as immovable at their ideal seats.
  petals=union(s.translate((r[i]@ROWS[i]['direction'])*.8) for i,s in enumerate(posed) if ROWS[i]['family']=='P')
  ds=np.arange(0,6.01,.25)
  for i,row in enumerate(ROWS):
   if row['family']=='C':continue
   if row['family']=='P' and reuse is not None:
    records.append(next(x for x in reuse['petal_anchor_only'] if x['state']==label and x['name']==row['name']));continue
   fixed=anchors if row['family']=='P' else petals
   cc=curve(xform(feet[i],r[i]),r[i]@row['direction'],fixed,ds);assert cc[0][1]<.005,('initial foot overlap',label,row['name'],cc[0]);rec=dict(state=label,name=row['name'],**summary(cc),curve=cc)
   (records if row['family']=='P' else corner_records).append(rec)
  last=[x for x in records if x['state']==label];ck=[x for x in corner_records if x['state']==label]
  print('RETENTION',label,'P minimum peak',min(x['maximum_intersection_mm3'] for x in last),'K minpeak',min(x['maximum_intersection_mm3'] for x in ck),flush=True)
 # Several extraction directions with the anchors only, plus corner paths
 # against petals already given outward play. Independent of floating contact.
 state=states[0][1]
 for family in ['P','K']:
  if family=='P' and reuse is not None:
   directions.extend(x for x in reuse['directional_probes'] if x['family']=='P');continue
  row=canonical(family);n=np.array(row['direction']);F=frame(n);s=retaining_foot(cells[row['name']])
  fixed=union([v.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*(.15 if family=='P' else .8)) for k,v in cells.items() if k[0]==('C' if family=='P' else 'P')])
  dirs=[n]+[unit(n+slope*(np.cos(t)*F[:,0]+np.sin(t)*F[:,1])) for slope in [.35,.7,1.2] for t in np.arange(12)*np.pi/6]
  for j,d in enumerate(dirs):
   cc=curve(s,d,fixed,np.arange(0,8.01,.25));directions.append(dict(family=family,direction=d.tolist(),**summary(cc)))
  print('DIRECTIONS',family,'min',min(x['maximum_intersection_mm3'] for x in directions if x['family']==family),flush=True)
 # Nominal and lifted C curves plus sampled penetration into each anchor.
 row=canonical('P');s=retaining_foot(cells[row['name']]);n=np.array(row['direction'])
 if reuse is not None:detail=reuse['nominal_radial_detail']
 for lift in ([] if reuse is not None else [0,.15,.3]):
  cs={k:v.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*lift) for k,v in cells.items() if k[0]=='C'}
  cc=curve(s,n,union(cs.values()),np.arange(0,6.001,.05));ss=summary(cc);peak=s.translate(n*ss['peak_at_mm']);patches=[]
  for name,c in cs.items():
   hit=peak^c
   if hit.volume()<.001:continue
   hm=mesh(hit);cm=mesh(c);sample=np.vstack([hm.vertices,hm.triangles_center]);depth=trimesh.proximity.signed_distance(cm,sample)
   patches.append(dict(anchor=name,intersection_mm3=hit.volume(),sample_count=len(sample),sampled_maximum_penetration_mm=float(depth.max())))
  detail.append(dict(center_lift_mm=lift,curve=cc,**ss,patches=patches))
 # A common outward expansion of the loose shell, not one piece pinned by
 # artificially fixed floating neighbors. All floating mutual overlaps checked.
 fixed=union([s for k,s in cells.items() if k[0]=='C']+[core_part])
 for dist in [0,.25,.5,.75,1,1.5,2,3,4,5,6]:
  moving=[v.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*dist) for k,v in cells.items() if k[0]!='C'];u=union(moving)
  collective.append(dict(expansion_mm=dist,anchor_intersection_mm3=max(0.,(u^fixed).volume()),mutual_intersection_mm3=max(0.,sum(s.volume() for s in moving)-u.volume())))
 report=dict(reused_unchanged_petal_test_inputs_sha256=reuse_inputs,status='finite geometric checks; physical prototype untested',extraction_test_geometry='Only the floating material at radii <= 28.5 mm; no outer-body obstruction credited.',petal_anchor_lift_mm=.15,corner_support_petal_expansion_mm=.8,petal_anchor_only=records,corner_to_displaced_petals=corner_records,directional_probes=directions,nominal_radial_detail=detail,collective_expansion=collective,scope='No elastic material, force, fatigue or exhaustive path proof. Corner expansion is a sensitivity probe, not a proof bounding every petal motion.')
 (DEST/'reports/retention-spherical.json').write_text(json.dumps(report,indent=2)+'\n')
 assert all(x['maximum_intersection_mm3']>2 for x in records), 'Insufficient anchor obstruction in a sampled state'
 assert all(x['maximum_intersection_mm3']>5 for x in corner_records), 'Insufficient supported corner obstruction'
 assert all(x['maximum_intersection_mm3']>1 for x in directions), 'Weak straight extraction path'
 print('SPHERICAL RETENTION COMPLETE',flush=True)
if __name__=='__main__':run()
