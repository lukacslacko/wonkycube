"""Check the rhombic-dodecahedron publication, exact inlays and retained archive."""
from pathlib import Path
import ast
import hashlib
import json
import re
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'designs/rhombic-dodecahedron-v5.1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((DESIGN/name).read_text())
def main():
 publication=read('publication.json');meta=read('manifest.json');feedback=read('physical-feedback.json')
 geometry={p.relative_to(DESIGN).as_posix():digest(p) for p in DESIGN.rglob('*') if p.suffix in ['.stl','.3mf']}
 assert geometry==publication['delivery_geometry_sha256']
 assert digest(DESIGN/'manifest.json')==publication['manifest_sha256']
 for key in ['geometry_source_sha256','unchanged_from_supplied_printed_design_sha256']:
  for name,sha in publication[key].items():assert digest(DESIGN/name)==sha,name
 puzzle=[r for r in meta['parts'] if '/puzzle/' in r['file']]
 assert {r['family']:r['quantity'] for r in puzzle}==dict(T=8,S=6,P=24,TC=8,SC=6,core=1)
 for row in meta['parts']:assert digest(DESIGN/row['file'])==row['sha256']
 assert feedback['physically_printed'] and feedback['physically_assembled'] and 'turns smoothly' in feedback['report']
 assert feedback['supplied_puzzle_stl_sha256']=={r['file']:r['sha256'] for r in puzzle}
 assert feedback['inlay_geometry']['published_clearance_per_side_mm']==0
 rigid=read('reports/printable-inlays.json')
 assert rigid['passed'] and rigid['clearance_per_side_mm']==0 and rigid['thickness_mm']==2
 assert len(rigid['files'])==108 and rigid['total_inlays']==96 and len(rigid['faces'])==12
 for row in rigid['files']:
  assert digest(DESIGN/row['file'])==row['sha256'] and row['thickness_mm']==2
  assert row['components']==(8 if '/faces/' in row['file'] else 1)
 for name in ['summary.json','spherical-retention.json','assembly.json','cap-fit.json','installed-rigid-inlays.json']:
  assert read('reports/'+name)['passed'],name
 assert len(read('reports/installed-rigid-inlays.json')['turns'])==14
 cuts=read('reports/cutting-files.json');assert len(cuts)==38 and all(r['audit_errors']==0 and r['dwg_roundtrip_max_error_mm']<.00001 for r in cuts)
 assert (DESIGN/'LICENSE').read_bytes()==(ROOT/'LICENSE').read_bytes()
 for p in (DESIGN/'source').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for path in ROOT.rglob('*.md'):
  if any(p.startswith('.') for p in path.relative_to(ROOT).parts):continue
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',path.read_text()):
   if '://' in target or target.startswith(('#','mailto:')):continue
   local=unquote(target.split('#')[0]);assert not local or (path.parent/local).exists(),(path,target)
 entries={}
 for line in (DESIGN/'SHA256SUMS.txt').read_text().splitlines():
  sha,name=line.split('  ',1);assert digest(DESIGN/name)==sha,name;entries[name]=sha
 actual={p.relative_to(DESIGN).as_posix() for p in DESIGN.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and '__pycache__' not in p.parts}
 assert actual==set(entries)
 readme=(ROOT/'README.md').read_text()
 assert 'face-turning-cuboctahedron' not in readme and 'Face-turning cuboctahedron' not in readme
 assert 'rhombic-dodecahedron-v5.1' in readme
 # The dual is retained as a complete unchanged design; the root showcase changes.
 old=ROOT/'designs/face-turning-cuboctahedron-v1';archive=json.loads((old/'publication.json').read_text())
 for name,sha in archive['delivery_geometry_sha256'].items():assert digest(old/name)==sha
 assert max(p.stat().st_size for p in DESIGN.rglob('*') if p.is_file())<100*1024**2
 print(f'PASS: {len(geometry)} STL/3MF files, 53 puzzle parts, 96 exact-size inlays, 14 axes, 38 DWGs, physical feedback, preserved dual geometry, local links and {len(entries)} checksums')
if __name__=='__main__':main()
