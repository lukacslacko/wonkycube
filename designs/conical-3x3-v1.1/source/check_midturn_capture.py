import hashlib
"""Rigid extraction probes in intermediate quarter-turn configurations."""
from conical_design import *
import sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());parts={}
for row in meta['parts']:
 if row['name'] not in {r['name'] for r in ROWS}|{'core'}:continue
 m=trimesh.load(DEST/row['file'],force='mesh');t=np.array(row['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 parts[row['name']]=from_mesh(m)^mf.Manifold.sphere(30,SEG)
records=[]
for angle in [22.5,45,67.5]:
 q=Rotation.from_rotvec(AXES[0]*np.radians(angle)).as_matrix()
 state={r['name']:xform(parts[r['name']],q) if 0 in r['signature'] else parts[r['name']] for r in ROWS}
 for name in ['E01','K01']:
  row=next(r for r in ROWS if r['name']==name);n=q@row['direction'];f=frame(n);s=state[name]
  for lift in [0.,.10]:
   fixed=union([ss.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*lift) if k.startswith('C') else ss for k,ss in state.items() if k!=name]+[parts['core']])
   pulls=[n]
   for slope in [.4,.9]:
    for phi in np.arange(0,360,60):
     v=n+slope*(np.cos(np.radians(phi))*f[:,0]+np.sin(np.radians(phi))*f[:,1]);pulls.append(v/np.linalg.norm(v))
   hits=[]
   for v in pulls:
    hit=next((float(d) for d in np.arange(.1,10.01,.1) if (s.translate(v*d)^fixed).volume()>.001),None)
    assert hit is not None,(angle,name,lift,'escape');hits.append(hit)
   rec=dict(angle_deg=angle,name=name,center_lift_mm=lift,directions=len(pulls),contact_distances_mm=hits)
   records.append(rec);print('MIDTURN',rec,flush=True)
   (DEST/'reports/midturn-capture.json').write_text(json.dumps(dict(manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),passed=False,checks=records,scope='Sampled rigid pulls with independent center lift; no elastic force or exhaustive escape claim.'),indent=2))

assert len(records)==12
(DEST/'reports/midturn-capture.json').write_text(json.dumps(dict(manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),passed=True,checks=records,scope='Sampled rigid pulls with independent center lift; no elastic force or exhaustive escape claim.'),indent=2))
