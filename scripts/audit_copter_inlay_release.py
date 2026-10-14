"""Audit published v4.1 delivery hashes, cutter sheets and the solving guide."""
from pathlib import Path
import ast,csv,hashlib,json,re
from urllib.parse import unquote
import numpy as np,trimesh,ezdxf
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'designs/curvy-copter-cuboctahedron-v4.1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pub=json.loads((D/'publication.json').read_text());meta=json.loads((D/'manifest.json').read_text())
 assert digest(D/'manifest.json')==pub['manifest_sha256']
 for group in ['delivery_geometry_sha256','geometry_source_sha256','original_report_sha256']:
  for path,sha in pub[group].items():assert digest(D/path)==sha,path
 actual={p.relative_to(D).as_posix() for p in D.rglob('*') if p.suffix.lower() in {'.stl','.3mf','.svg','.dxf','.dwg'}}
 assert actual==set(pub['delivery_geometry_sha256'])
 assert sum(p['quantity'] for p in meta['parts'])==57
 for r in meta['parts']:assert digest(D/r['file'])==r['sha256']
 assert digest(D/'stl/puzzle/core.stl')==digest(ROOT/'designs/curvy-copter-cuboctahedron-v3.2/stl/puzzle/core.stl')
 meshes=0
 for p in (D/'stl').rglob('*.stl'):
  m=trimesh.load(p,force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1,p
  assert abs(m.bounds[0,2])<.0001,p;meshes+=1
 cuts=json.loads((D/'reports/cutting-files.json').read_text());dims={r['file']:r for r in csv.DictReader((D/'inlays/sheet-dimensions.csv').open())}
 assert len(cuts)==len(dims)==30;exact=0
 for rec in cuts:
  stem=D/rec['path'];doc=ezdxf.readfile(stem.with_suffix('.dxf'));entities=list(doc.modelspace())
  assert len(entities)==rec['contours']
  pts=[]
  for e in entities:
   assert e.dxftype()=='POLYLINE' and e.is_closed
   pp=np.array(list(e.points()))[:,:2];assert Polygon(pp).is_valid;pts.extend(pp)
  pp=np.array(pts);width,height=np.ptp(pp,axis=0);row=dims[rec['path'].removeprefix('inlays/')+'.dxf']
  assert abs(width-float(row['selection_width_mm']))<2e-6
  assert abs(height-float(row['selection_height_mm']))<2e-6
  assert int(row['contours'])==len(entities)
  assert stem.with_suffix('.dwg').read_bytes()[:6]==b'AC1015'
  assert rec['audit_errors']==0 and rec['dwg_roundtrip_max_error_mm']<1e-5
  if '/faces/' in rec['path']:exact+=len(entities)
 assert exact==104
 for name in ['summary','rounding-regression','package-audit']:assert json.loads((D/'reports'/f'{name}.json').read_text())['passed']
 assert (D/'LICENSE').read_bytes()==(ROOT/'LICENSE').read_bytes()
 checks={}
 for line in (D/'SHA256SUMS').read_text().splitlines():
  h,n=line.split('  ',1);assert digest(D/n)==h,n;checks[n]=h
 allfiles={p.relative_to(D).as_posix() for p in D.rglob('*') if p.is_file() and p.name not in ['SHA256SUMS','.DS_Store'] and '__pycache__' not in p.parts}
 assert allfiles==set(checks)
 g=ROOT/'docs/solving/triangular-prism';v=json.loads((g/'pdf-validation.json').read_text())
 assert digest(ROOT/v['pdf'])==v['sha256'] and v['pages']==9
 alg=json.loads((g/'algorithms.json').read_text());assert len(alg['tables']['H'])==len(alg['tables']['K'])==20
 for p in list((D/'source').glob('*.py'))+list(g.glob('*.py')):ast.parse(p.read_text(),filename=str(p))
 for p in ROOT.rglob('*.md'):
  if any(x.startswith('.') for x in p.relative_to(ROOT).parts):continue
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith(('#','mailto:')):continue
   target=unquote(target.split('#')[0]);assert not target or (p.parent/target).exists(),(p,target)
 assert not any(p.stat().st_size>=100*1024**2 for p in D.rglob('*') if p.is_file())
 print(f'PASS: {len(actual)} unchanged geometry/cut files, {meshes} reloaded STL solids, 57 puzzle parts, 104 exact inlays, 30 sized cutting sheets, guide hash and local links.')
if __name__=='__main__':main()
