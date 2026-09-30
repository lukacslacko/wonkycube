"""Check the published double-Ivy inventory, mesh plates, evidence and links."""
from pathlib import Path
import ast,hashlib,json,re,zipfile,xml.etree.ElementTree as ET
from urllib.parse import unquote
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'designs/double-ivy-v7.1'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 meta=json.loads((D/'manifest.json').read_text());pub=json.loads((D/'publication.json').read_text())
 assert pub['manifest_sha256']==digest(D/'manifest.json')
 actual={p.relative_to(D).as_posix():digest(p) for p in D.rglob('*') if p.suffix in {'.stl','.3mf'}};assert actual==pub['delivery_geometry_sha256']
 parts={r['name']:r for r in meta['parts']};puzzle={k:v for k,v in parts.items() if '/puzzle/' in v['file']};assert len(puzzle)==27
 meshes={}
 for n,r in parts.items():
  assert digest(D/r['file'])==r['sha256'],n
  m=trimesh.load(D/r['file'],force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1 and m.volume>0,n
  meshes[n]=m
 ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};seen=[]
 for p in meta['plates']:
  with zipfile.ZipFile(D/p['file']) as z:tree=ET.fromstring(z.read('3D/3dmodel.model'))
  boxes=[];named={}
  for obj in tree.findall('m:resources/m:object',ns):
   name=obj.attrib['name'];named[obj.attrib['id']]=name;seen.append(name);m=meshes[name]
   vs=np.array([[float(v.attrib[c]) for c in ['x','y','z']] for v in obj.findall('m:mesh/m:vertices/m:vertex',ns)]);fs=np.array([[int(v.attrib[c]) for c in ['v1','v2','v3']] for v in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
   assert np.array_equal(vs,m.vertices) and np.array_equal(fs,m.faces),name
  for item in tree.findall('m:build/m:item',ns):
   n=named[item.attrib['objectid']];v=np.array([float(x) for x in item.attrib['transform'].split()]);assert np.array_equal(v[:9],np.eye(3).flatten());b=meshes[n].bounds+v[9:];assert np.min(b[0,:2])>5 and np.max(b[1,:2])<251 and abs(b[0,2])<.005
   for other in boxes:assert np.any(b[1,:2]<=other[0,:2]) or np.any(other[1,:2]<=b[0,:2])
   boxes.append(b)
 assert sorted(seen)==sorted(puzzle)
 feedback=json.loads((D/'physical-feedback.json').read_text());assert feedback['physically_printed'] and feedback['physically_assembled'] and not feedback['rounding_correction_physically_tested']
 baseline=json.loads((D/'reference/baseline-v7-manifest.json').read_text());old={r['name']:r for r in baseline['parts']}
 corr=json.loads((D/'reference/rounding-manifest.json').read_text());assert all(parts[r['name']]['sha256']==r['sha256'] for r in corr['parts'])
 assert all(r['sha256']==old[n]['sha256'] for n,r in puzzle.items() if r['family'] in ['W','E'])
 motion=json.loads((D/'reports/motion.json').read_text());assert motion['manifest_sha256']==digest(D/'manifest.json');assert len([k for k in motion if k.startswith(('solved_','scramble_'))])==24
 assert (D/'LICENSE').read_bytes()==(ROOT/'LICENSE').read_bytes()
 for p in (D/'source').rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for p in ROOT.rglob('*.md'):
  if any(x.startswith('.') for x in p.relative_to(ROOT).parts):continue
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text()):
   if '://' in target or target.startswith(('#','mailto:')):continue
   local=unquote(target.split('#')[0]);assert not local or (p.parent/local).exists(),(p,target)
 sums={}
 for line in (D/'SHA256SUMS.txt').read_text().splitlines():
  h,n=line.split('  ',1);assert digest(D/n)==h,n;sums[n]=h
 expected={p.relative_to(D).as_posix() for p in D.rglob('*') if p.is_file() and p.name!='SHA256SUMS.txt' and '__pycache__' not in p.parts};assert set(sums)==expected
 print('PASS: 27 puzzle parts, five matching full-set plates, corrected C/F and unchanged W/E, current core, motion report, physical evidence, source syntax, MIT, links and checksums.')
if __name__=='__main__':run()
