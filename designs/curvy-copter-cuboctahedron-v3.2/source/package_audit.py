"""Check final plate quantities, bed bounds and exact STL geometry reuse."""
from hardware import *
from print_3mf import q
import zipfile,xml.etree.ElementTree as ET,hashlib
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
def run():
 meta=json.loads((DEST/'manifest.json').read_text());parts={}
 for r in meta['parts']:
  p=DEST/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
  if '/puzzle/' in r['file']:parts[r['family']]=trimesh.load(p,force='mesh')
 report=[];total={f:0 for f in parts}
 for relative in [r['file'] for r in meta['plates']]+['start-here/retention-test-7-pieces.3mf','start-here/upgrade-test-6-pieces.3mf','start-here/centers-only-test-3-pieces.3mf','start-here/centers-only-full-12-pieces.3mf']:
  with zipfile.ZipFile(DEST/relative) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
  assert root.get('unit')=='millimeter';objects={o.get('id'):o for o in root.find(q('resources')).findall(q('object'))};bounds=[];records=[]
  for item in root.find(q('build')).findall(q('item')):
   obj=objects[item.get('objectid')];name=obj.get('name');family='core' if name=='core' else name[0];geo=obj.find(q('mesh'))
   v=np.array([[float(p.get(k)) for k in ['x','y','z']] for p in geo.find(q('vertices'))]);f=np.array([[int(p.get(k)) for k in ['v1','v2','v3']] for p in geo.find(q('triangles'))]);ref=parts[family]
   assert np.array_equal(v,ref.vertices) and np.array_equal(f,ref.faces),(relative,name,'geometry differs from STL')
   t=np.array([float(x) for x in item.get('transform').split()]);assert np.array_equal(t[:9],[1,0,0,0,1,0,0,0,1]);pos=v+t[9:];lo,hi=pos.min(0),pos.max(0);assert np.all(lo[:2]>0) and np.all(hi[:2]<256) and abs(lo[2])<.005
   for a,b in bounds:assert np.any(hi[:2]<=a[:2]) or np.any(lo[:2]>=b[:2]),(relative,name,'print bounding boxes overlap')
   bounds.append((lo,hi));records.append(dict(name=name,family=family))
   if relative.startswith('plates/'):total[family]+=1
  report.append(dict(file=relative,objects=records,exact_stl_geometry=True,inside_256mm_bed=True,overlapping_xy_bounding_boxes=False))
 assert total=={'C':12,'P':24,'K':8,'core':1},total
 (DEST/'reports/package-audit.json').write_text(json.dumps(dict(total_full_set=total,plates=report),indent=2)+'\n');print('PACKAGE AUDIT',total,flush=True)
if __name__=='__main__':run()
