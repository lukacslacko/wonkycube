"""Audit all delivered geometry, cut sets and geometry-only 3MF plates."""
from design import *
from shapely.geometry import Polygon
import ezdxf,xml.etree.ElementTree as ET,zipfile,hashlib,re
def run():
 meta=json.loads((DEST/'manifest.json').read_text());stls=[]
 for p in sorted((DEST/'stl').rglob('*.stl')):
  m=trimesh.load(p,force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1,(p,'bad mesh')
  assert abs(m.bounds[0,2])<.0001,(p,'not on bed',m.bounds[0,2])
  stls.append(dict(file=p.relative_to(DEST).as_posix(),components=1,closed=True,volume_mm3=float(m.volume)))
 for r in meta['parts']:
  assert hashlib.sha256((DEST/r['file']).read_bytes()).hexdigest()==r['sha256']
 ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};plates=[]
 for p in list((DEST/'plates').glob('*.3mf'))+list((DEST/'start-here').glob('*.3mf')):
  with zipfile.ZipFile(p) as z:tree=ET.fromstring(z.read('3D/3dmodel.model'))
  assert tree.attrib['unit']=='millimeter';objs={o.attrib['id']:o for o in tree.findall('m:resources/m:object',ns)};boxes=[]
  for item in tree.findall('m:build/m:item',ns):
   o=objs[item.attrib['objectid']];v=np.array([[float(e.attrib[c]) for c in ['x','y','z']] for e in o.findall('m:mesh/m:vertices/m:vertex',ns)]);tt=np.array([float(x) for x in item.attrib['transform'].split()]);t=tt[9:12];lo,hi=v.min(axis=0)+t,v.max(axis=0)+t
   assert min(lo[:2])>=0 and max(hi[:2])<=256 and abs(lo[2])<1e-4,(p,o.attrib['name'],lo,hi)
   for name,bl,bh in boxes:assert not np.all(np.minimum(hi[:2],bh[:2])>np.maximum(lo[:2],bl[:2])),(p,'overlapping plate boxes',name,o.attrib['name'])
   boxes.append((o.attrib['name'],lo,hi))
  plates.append(dict(file=p.relative_to(DEST).as_posix(),objects=len(boxes),inside_256mm_bed=True,no_xy_bounding_box_overlap=True))
 exact=[]
 for p in sorted((DEST/'inlays/faces').glob('*.dxf')):
  doc=ezdxf.readfile(p);items=list(doc.modelspace());assert all(e.dxftype()=='POLYLINE' and e.is_closed for e in items)
  assert len(items)==(8 if p.stem.startswith('S') else 7)
  for e in items:assert Polygon([(q[0],q[1]) for q in e.points()]).is_valid
  exact.append(dict(face=p.stem,contours=len(items)))
 assert len(exact)==14 and sum(r['contours'] for r in exact)==104
 cutting=json.loads((DEST/'reports/cutting-files.json').read_text())
 assert len(cutting)==30 and all(r.get('dwg_roundtrip_max_error_mm',100)<1e-5 for r in cutting)
 for r in cutting:
  for ext in ['.svg','.dxf','.dwg']:assert (DEST/(r['path']+ext)).is_file()
 reports=['summary','normal-turns','jumbling','jumbling-walk','capture','plug-fit','preserved-mechanism','layer-connectivity','assembly','paper-backing']
 for name in reports:assert (DEST/'reports'/(name+'.json')).is_file()
 assert json.loads((DEST/'reports/summary.json').read_text())['passed']
 result=dict(passed=True,stls=stls,plates=plates,exact_face_cut_sets=exact,cutting_sheets_with_verified_svg_dxf_dwg=len(cutting),full_puzzle_printed_part_count=sum(r['quantity'] for r in meta['parts']),source='Independent package inventory and reload checks; detailed mechanism tests are separate reports.')
 (DEST/'reports/package-audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PACKAGE AUDIT PASSED',len(stls),'STLs,',len(plates),'plates, 104 inlays / 30 verified cutting sheets',flush=True)
if __name__=='__main__':run()
