"""Package the full design and a small cutter-only download."""
from pathlib import Path
import argparse,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'designs/curvy-copter-cuboctahedron-v4.1'
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'dist');args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
tag='curvy-copter-cuboctahedron-v4.1'
def clean(p):return p.is_file() and p.name!='.DS_Store' and '__pycache__' not in p.parts
files=sorted(p for p in D.rglob('*') if clean(p))
full=args.output/(tag+'-full.zip')
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,tag+'/'+p.relative_to(D).as_posix())
cut=args.output/(tag+'-inlays.zip')
selected=sorted(p for p in (D/'inlays').rglob('*') if clean(p))
selected += [D/'LICENSE',D/'images/face-map.png',D/'images/face-map.svg',D/'reference/inlay-faces.json',D/'reports/cutting-files.json']
with zipfile.ZipFile(cut,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('README.txt','Curvy Copter cuboctahedron v4.1 - laminated-paper inlays\r\n\r\nStart with inlays/README.md (readable as text).\r\nUse DXF for Silhouette Studio Basic; SVG for Designer Edition or above.\r\nCheck each sheet against inlays/sheet-dimensions.csv before cutting.\r\nDefault faces/ outlines are exact pocket size; cut each face once.\r\nThe pocket depth is 0.5 mm including laminate and adhesive.\r\n\r\nBuild guide and full print package:\r\nhttps://github.com/lukacslacko/wonkycube/releases/tag/'+tag+'\r\n')
 for p in selected:z.write(p,p.relative_to(D).as_posix())
 z.writestr('SHA256SUMS.txt',''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(D).as_posix()+'\n' for p in selected))
for p in [full,cut]:
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  assert not any('.DS_Store' in n or '__pycache__' in n for n in z.namelist())
  print(p.name,p.stat().st_size,'bytes',len(z.namelist()),'entries')
(args.output/(tag+'-SHA256SUMS.txt')).write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in [full,cut]))
