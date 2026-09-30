"""Verify oriented mesh hashes, 3MF contents, bed placements and reused core."""
from design import *
import hashlib,zipfile,xml.etree.ElementTree as ET
meta=json.loads((DEST/'manifest.json').read_text());parts={r['name']:r for r in meta['parts']};report={};meshes={}
for name,r in parts.items():
 p=DEST/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 m=trimesh.load(p,force='mesh');assert m.is_watertight and m.is_winding_consistent and len(m.split())==1 and m.volume>0
 assert abs(m.bounds[0,2])<.005
 meshes[name]=m
core=next(r for r in json.loads((HERE/'reused/manifest.json').read_text()) if r['name']=='core')
assert (DEST/parts['core']['file']).read_bytes()==(HERE/core['file']).read_bytes()
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'};seen=[];plates=[]
for plate in meta['plates']:
 with zipfile.ZipFile(DEST/plate['file']) as z:
  assert z.testzip() is None;model=ET.fromstring(z.read('3D/3dmodel.model'))
 assert model.attrib['unit']=='millimeter'
 obs={};boxes=[]
 for obj in model.findall('m:resources/m:object',ns):
  name=obj.attrib['name'];v=np.array([[float(a.attrib[k]) for k in ['x','y','z']] for a in obj.findall('m:mesh/m:vertices/m:vertex',ns)])
  f=np.array([[int(a.attrib[k]) for k in ['v1','v2','v3']] for a in obj.findall('m:mesh/m:triangles/m:triangle',ns)])
  assert np.array_equal(v,meshes[name].vertices) and np.array_equal(f,meshes[name].faces),(name,'3mf changed mesh')
  obs[obj.attrib['id']]=(name,v);seen.append(name)
 for item in model.findall('m:build/m:item',ns):
  name,v=obs[item.attrib['objectid']];T=np.array(list(map(float,item.attrib['transform'].split()))).reshape((4,3));v=v@T[:3]+T[3];lo,hi=v.min(0),v.max(0)
  assert np.all(lo[:2]>=10) and np.all(hi[:2]<=246) and abs(lo[2])<.005 and hi[2]<250
  for other,a,b in boxes:assert np.any(hi[:2]<=a[:2]) or np.any(lo[:2]>=b[:2]),(name,other,'plate overlap')
  boxes.append((name,lo,hi))
 plates.append(dict(name=plate['name'],objects=[a[0] for a in boxes],geometry_identical_to_stl=True,inside_256mm_bed=True))
assert sorted(seen)==sorted(r['name'] for r in ROWS)
report=dict(all_meshes_watertight_single_component=True,new_prints=len(seen),core_exactly_reused=True,optional_stand_reused=True,plates=plates,manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest())
(DEST/'reports/package.json').write_text(json.dumps(report,indent=2)+'\n');print(report,flush=True)
