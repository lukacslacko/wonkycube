"""Package only a completed, validated release, without caches or intermediates."""
from design import *
import hashlib,zipfile
def package():
 summary=json.loads((DEST/'reports/summary.json').read_text())
 assert summary['passed'] and summary['delivery_meshes_reloaded']
 assert (DEST/'reports/installed-inlays.json').is_file()
 printed_inlays=json.loads((DEST/'reports/printable-inlays.json').read_text())
 assert printed_inlays['passed'] and printed_inlays['total_inlays']==96 and printed_inlays['clearance_per_side_mm']==0
 assert json.loads((DEST/'reports/installed-rigid-inlays.json').read_text())['passed']
 assert len(printed_inlays['files'])==108
 for r in printed_inlays['files']:assert hashlib.sha256((DEST/r['file']).read_bytes()).hexdigest()==r['sha256']
 assert json.loads((DEST/'reports/spherical-retention.json').read_text())['passed']
 assert json.loads((DEST/'reports/assembly.json').read_text())['passed']
 cuts=json.loads((DEST/'reports/cutting-files.json').read_text())
 assert len(cuts)==38 and all(r['dwg_roundtrip_max_error_mm']<.00001 and r['audit_errors']==0 for r in cuts)
 meta=json.loads((DEST/'manifest.json').read_text())
 default=[r for r in meta['parts'] if '/puzzle/' in r['file']]
 assert sum(r['quantity'] for r in default)==53
 labels=[name for plate in meta['plates'] for name in plate['objects']]
 assert len(labels)==len(set(labels))==53
 assert set(labels)=={'core'}|{r['name'] for r in ROWS}|{r['name']+'-cap' for r in ROWS if r['family'] in ['T','S']}
 assert json.loads((DEST/'reports/cap-fit.json').read_text())['passed']
 for row in meta['parts']:
  assert hashlib.sha256((DEST/row['file']).read_bytes()).hexdigest()==row['sha256']
 for line in (DEST/'SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1)
  assert hashlib.sha256((DEST/name).read_bytes()).hexdigest()==digest,name
 out=DEST.parent/(DEST.name+'.zip')
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(DEST.rglob('*')):
   if p.is_file() and p.name!='.DS_Store' and '__pycache__' not in p.parts:z.write(p,DEST.name+'/'+p.relative_to(DEST).as_posix())
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 print('PACKAGED',out,round(out.stat().st_size/1e6,2),'MB',flush=True)
 addon=DEST.parent/'rhombic-dodecahedron-v5.1-printable-inlays-2mm.zip'
 root=DEST/'inlays/printable'
 with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file() and p.name!='.DS_Store' and '__pycache__' not in p.parts:z.write(p,'rhombic-dodecahedron-v5.1-printable-inlays-2mm/'+p.relative_to(root).as_posix())
 with zipfile.ZipFile(addon) as z:assert z.testzip() is None
 print('PRINTABLE INLAY DOWNLOAD',addon,round(addon.stat().st_size/1e6,2),'MB',flush=True)
if __name__=='__main__':package()
