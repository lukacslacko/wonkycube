"""Quantify remaining internal corner capture, including simultaneous neighbor separation.

This is a geometric sensitivity study, not a force/elastic-pop simulation.
"""
from conical_design import *
import sys,hashlib
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());parts={};inner={}
for row in meta['parts']:
 if not row['file'].startswith('stl/puzzle/'):continue
 m=trimesh.load(DEST/row['file'],force='mesh');t=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 parts[row['name']]=from_mesh(m);inner[row['name']]=parts[row['name']]^mf.Manifold.sphere(31.2,SEG)
records=[]
for row in (r for r in ROWS if r['family']=='K'):
 name=row['name'];n=np.array(row['direction']);target=inner[name];f=frame(n)
 contact_parts=[]
 for other in ROWS:
  if other['name']==name:continue
  v=float((target.translate(2*n)^inner[other['name']]).volume())
  if v>.05:contact_parts.append(dict(name=other['name'],overlap_at_2mm_pull_mm3=v))
 assert len([r for r in contact_parts if r['name'][0] in ['V','H']])>=3,(name,contact_parts)
 for neighbor_shift in [0.,.20]:
  fixed=union([ss.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*(.10 if k.startswith('C') else neighbor_shift)) for k,ss in inner.items() if k not in [name,'core']]+[inner['core']])
  curve=[[float(d),max(0.,float((target.translate(d*n)^fixed).volume()))] for d in np.arange(0,6.001,.1)]
  blocked=[d for d,v in curve if v>.001];assert blocked and min(blocked)<1.2,(name,neighbor_shift,curve)
  assert max(v for d,v in curve)>10,(name,'little obstructing material',curve)
  # Thirteen directions, each checked past the whole shoulder. No inference
  # about paths that curve between these directions or elastic deformation.
  directions=[n]
  for slope in [.4,.9]:
   for phi in np.arange(0,360,60):
    d=n+slope*(np.cos(np.radians(phi))*f[:,0]+np.sin(np.radians(phi))*f[:,1]);directions.append(d/np.linalg.norm(d))
  hits=[]
  for direction in directions:
   hit=next((float(d) for d in np.arange(.1,10.01,.1) if (target.translate(d*direction)^fixed).volume()>.001),None)
   assert hit is not None,(name,neighbor_shift,'unobstructed direction');hits.append(hit)
  rec=dict(name=name,whole_part_volume_mm3=parts[name].volume(),internal_volume_mm3=target.volume(),screwed_center_lift_mm=.10,other_floating_parts_radial_shift_mm=neighbor_shift,retainers=contact_parts,radial_obstruction_curve=curve,angled_pull_first_contacts_mm=hits)
  records.append(rec);print('CORNER CAPTURE',name,neighbor_shift,'first',min(blocked),'peak',max(v for d,v in curve),flush=True)
(DEST/'reports/corner-capture.json').write_text(json.dumps(dict(passed=True,manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),checks=records,scope=__doc__),indent=2))
