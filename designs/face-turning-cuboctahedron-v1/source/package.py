"""Package only a completed, validated release, without caches or intermediates."""
from design import *
import hashlib,zipfile
def package():
 summary=json.loads((DEST/'reports/summary.json').read_text())
 assert summary['passed'] and summary['delivery_meshes_reloaded']
 meta=json.loads((DEST/'manifest.json').read_text())
 default=[r for r in meta['parts'] if '/puzzle/' in r['file']]
 assert sum(r['quantity'] for r in default)==39
 labels=[name for plate in meta['plates'] for name in plate['objects']]
 assert len(labels)==len(set(labels))==39
 assert set(labels)=={'core'}|{r['name'] for r in ROWS}
 for row in meta['parts']:
  assert hashlib.sha256((DEST/row['file']).read_bytes()).hexdigest()==row['sha256']
 for line in (DEST/'SHA256SUMS.txt').read_text().splitlines():
  digest,name=line.split('  ',1)
  assert hashlib.sha256((DEST/name).read_bytes()).hexdigest()==digest,name
 out=DEST.with_suffix('.zip')
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(DEST.rglob('*')):
   if p.is_file():z.write(p,DEST.name+'/'+p.relative_to(DEST).as_posix())
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 print('PACKAGED',out,round(out.stat().st_size/1e6,2),'MB',flush=True)
if __name__=='__main__':package()
