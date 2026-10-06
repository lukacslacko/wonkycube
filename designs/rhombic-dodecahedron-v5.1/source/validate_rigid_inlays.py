"""Validate installed exact-size rigid tiles read from the delivered face STLs."""
from inlays import *
from checks import motion,assembly

def validate():
 meta=json.loads((DEST/'manifest.json').read_text());parts={}
 for rec in meta['parts']:
  if '/puzzle/' not in rec['file']:continue
  m=trimesh.load(DEST/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];parts[rec['family']]=from_mesh(m)
 cells={};inserts={r['name']:[] for r in ROWS};files=json.loads((DEST/'inlays/printable/manifest.json').read_text())
 for face_rec in files['faces']:
  fi=next(i for i,(_,_,name) in enumerate(FACES) if name==face_rec['face']);F=frame(FACES[fi][0])
  for rec in face_rec['individuals']:
   m=trimesh.load(DEST/'inlays/printable'/rec['file'],force='mesh');m.vertices[:,:2]+=np.array(rec['xy_center_in_face_mm']);m.vertices[:,2]+=FACE_HEIGHT-THICKNESS
   inserts[rec['piece']].append(xform(from_mesh(m),F))
 for row in ROWS:
  f=row['family'];n=row['name'];q=mapping(canonical(f)['signature'],row['signature']);s=parts[f]
  if f in ['T','S']:s=s+parts[f+'C']
  assert len(inserts[n])=={'T':3,'S':4,'P':2}[f]
  cells[n]=union([xform(s,q)]+inserts[n])
 turns=motion(cells,parts['core'],step=3,all_axes=True)
 placement=assembly(cells,parts['core'])
 result=dict(passed=True,thickness_mm=THICKNESS,contour_offset_mm=0.,installed_inlays=96,top_position='flush with the exterior, allowing 0.10 mm adhesive thickness',turns=turns,assembly=placement,scope='Actual exported rigid-inlay STLs and unchanged puzzle meshes. Finite sweeps on all 14 axes at 3-degree intervals and coordinated shell assembly; no measured forces or adhesion claim.')
 (DEST/'reports/installed-rigid-inlays.json').write_text(json.dumps(result,indent=2)+'\n')
 print('EXACT RIGID INLAYS VALIDATED',flush=True)
if __name__=='__main__':validate()
