import hashlib
"""Check fixed-width printable layer connectivity on the exported orientations."""
from section_connectivity import *
import sys,hashlib
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());report=[]
for row in meta['parts']:
 if row['file'].split('/')[1]!='puzzle':continue
 m=trimesh.load(DEST/row['file'],force='mesh');s=from_mesh(m)
 tests=[]
 for h,w in [(.16,.42),(.20,.45)]:
  components=check(s,h,w);scraps=[c for c in components[1:] if c['volume_mm3']>.03]
  assert not scraps,(row['name'],h,w,scraps)
  tests.append(dict(layer_height_mm=h,line_width_mm=w,components=components))
 report.append(dict(name=row['name'],tests=tests));print('LAYERS',row['name'],flush=True)
 (DEST/'reports/printability.json').write_text(json.dumps(dict(manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),passed=False,checks=report,scope='Fixed-width layer geometry, not Bambu toolpaths or a strength test.'),indent=2))

assert len(report)==33
(DEST/'reports/printability.json').write_text(json.dumps(dict(manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),passed=True,checks=report,scope='Fixed-width layer geometry, not Bambu toolpaths or a strength test.'),indent=2))
