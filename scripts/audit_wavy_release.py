"""Audit Wavy Redi release files and distinguish v1 feedback from v1.1 checks."""
from pathlib import Path
import ast, hashlib, json, re
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
DESIGN=ROOT/'designs/wavy-redi-v1.1'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 manifest=json.loads((DESIGN/'manifest.json').read_text())
 expected={p['name']:p['sha256'] for p in manifest['parts']}
 assert manifest['version']=='wavy-redi-v1.1'
 for p in manifest['parts']:assert digest(DESIGN/p['file'])==p['sha256'],p['name']
 assert len(expected)==22
 for mode in ['motion','assembly','retention','hardware','strength','ridges','plates','exterior']:
  report=json.loads((DESIGN/'reports'/f'{mode}.json').read_text())
  assert report['_completion']['passed'] and report['_inputs']==expected,mode
 feedback=json.loads((DESIGN/'physical-feedback.json').read_text())
 assert feedback['design']=='wavy-redi-v1' and not feedback['revision']['physically_tested']
 changed=[]
 for filename,previous in feedback['printed_part_sha256'].items():
  if digest(DESIGN/filename)!=previous:changed.append(Path(filename).stem)
 assert sorted(changed)==['E02','E04','E09','E11','core'],changed
 assert digest(DESIGN/'physical-feedback.json')==digest(DESIGN/'source/physical-feedback.json')
 assert (DESIGN/'LICENSE').read_bytes()==(ROOT/'LICENSE').read_bytes()
 for p in (DESIGN/'source').glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in ROOT.rglob('*.md'):
  if any(k.startswith('.') for k in p.relative_to(ROOT).parts):continue
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith(('#','mailto:')):continue
   local=unquote(target.split('#')[0]);assert not local or (p.parent/local).exists(),(p,target)
 sums=DESIGN/'SHA256SUMS.txt';listed={}
 for line in sums.read_text().splitlines():
  sha,name=line.split('  ',1);assert digest(DESIGN/name)==sha,name;listed[name]=sha
 files={p.relative_to(DESIGN).as_posix() for p in DESIGN.rglob('*') if p.is_file() and p!=sums and '__pycache__' not in p.parts}
 assert files==set(listed)
 publication=json.loads((DESIGN/'publication.json').read_text())
 assert publication['manifest_sha256']==digest(DESIGN/'manifest.json')
 print(f'PASS: 21 puzzle parts + coupon; 8 completed checks; exactly 5 replacement parts; source, links and {len(listed)} checksums')
if __name__=='__main__':main()
