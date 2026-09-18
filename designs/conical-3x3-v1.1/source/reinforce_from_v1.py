"""Make compatible C-only replacements from the actual v1 print meshes.

Material is added inside the old washer well. The bearing foot, exterior,
retention surfaces, core, and floating pieces are preserved. The separate
standard CAD build uses SEAT=28.8 to reproduce the intended geometry afresh.
"""
from conical_design import *
from mesh_io import cleaned
from print_3mf import save_3mf
from section_connectivity import check
import hashlib,shutil,xml.etree.ElementTree as ET,zipfile,sys
V1=Path(sys.argv[1]);DEST=Path(sys.argv[2]);assert V1.resolve()!=DEST.resolve()
shutil.copytree(V1,DEST,dirs_exist_ok=True)
for folder in ['reports','images']:
 shutil.rmtree(DEST/folder);(DEST/folder).mkdir()
shutil.copy2(V1/'manifest.json',DEST/'reference/v1-manifest.json')
shutil.copy2(V1/'reports/export-fidelity.json',DEST/'reference/v1-export-fidelity.json')
meta=json.loads((DEST/'manifest.json').read_text());meta['version']='wonky-conical-3x3-70-v1.1';meta['washer_seat_mm']=SEAT
rows={r['name']:r for r in meta['parts']};new_meshes={};changes=[]
for rr in ROWS:
 name=rr['name'];row=rows[name];m=trimesh.load(V1/row['file'],force='mesh');T=np.array(row['mechanism_to_print']);original=m.copy();m.vertices=(m.vertices-T[:,3])@T[:,:3];old=from_mesh(m)
 if rr['family']=='C':
  # Small overlap below the old floor and outside its wall avoids coincident
  # seams when combining nominal CAD cylinders with quantized old STL vertices.
  lower=27.25
  filler=mf.Manifold.cylinder(SEAT-lower,4.9,4.9,128).translate([0,0,lower])
  bore=mf.Manifold.cylinder(100,1.8,1.8,96)
  new=main((old+xform(filler-bore,frame(rr['direction'])))-xform(bore,frame(rr['direction'])))
  removed=(old-new).volume();added=(new-old).volume();assert abs(removed)<.001 and 90<added<96,(name,removed,added)
  save(new,CACHE/'final'/(name+'.npz'))
  pm=mesh(new.simplify(.001));pm.vertices=pm.vertices@T[:,:3].T+T[:,3];pm=cleaned(pm);pm.export(DEST/row['file'])
  reread=trimesh.load(DEST/row['file'],force='mesh');assert reread.is_watertight and reread.is_winding_consistent and len(reread.split())==1
  row.update(sha256=hashlib.sha256((DEST/row['file']).read_bytes()).hexdigest(),dimensions_mm=np.ptp(reread.vertices,axis=0).tolist(),volume_mm3=float(reread.volume),triangles=len(reread.faces),cleanup=pm.metadata.get('cleanup',{}),first_layer_0_16_mm_area_mm2=float(from_mesh(reread).slice(.16).area()))
  new_meshes[name]=reread
  changes.append(dict(name=name,added_material_mm3=float(added),removed_material_mm3=float(removed),old_sha256=hashlib.sha256((V1/row['file']).read_bytes()).hexdigest(),new_sha256=row['sha256']))
  print('REINFORCE',changes[-1],flush=True)
 else:
  save(old,CACHE/'final'/(name+'.npz'));assert (V1/row['file']).read_bytes()==(DEST/row['file']).read_bytes()
# Regenerate the optional dimensional coupon for the raised washer seat.
row=rows['rotor-fit'];m=cleaned(mesh(rotor_coupon()));T=np.column_stack([np.eye(3),np.array([0.,0.,-FOOT_PLANE])]);m.vertices=m.vertices+T[:,3];m=cleaned(m);m.export(DEST/row['file']);new_meshes['rotor-fit']=m
row.update(mechanism_to_print=T.tolist(),sha256=hashlib.sha256((DEST/row['file']).read_bytes()).hexdigest(),dimensions_mm=np.ptp(m.vertices,axis=0).tolist(),volume_mm3=float(m.volume),triangles=len(m.faces),cleanup=m.metadata.get('cleanup',{}),first_layer_0_16_mm_area_mm2=float(from_mesh(m).slice(.16).area()))
# Keep all existing plate placements, changing only meshes that changed.
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
for plate in meta['plates']:
 if not set(plate['objects'])&set(new_meshes):continue
 with zipfile.ZipFile(V1/plate['file']) as z:root=ET.fromstring(z.read('3D/3dmodel.model'))
 names={o.attrib['id']:o.attrib['name'] for o in root.findall('m:resources/m:object',ns)};items=[]
 for item in root.findall('m:build/m:item',ns):
  name=names[item.attrib['objectid']];values=np.array(list(map(float,item.attrib['transform'].split()))).reshape(4,3);assert np.allclose(values[:3],np.eye(3));items.append((name,new_meshes.get(name,trimesh.load(DEST/rows[name]['file'],force='mesh')),values[3]))
 save_3mf(DEST/plate['file'],items)
assembly=[]
for rr in ROWS+[dict(name='core')]:
 row=rows[rr['name']];m=trimesh.load(DEST/row['file'],force='mesh');T=np.array(row['mechanism_to_print']);m.vertices=((m.vertices-T[:,3])@T[:,:3])@R;assembly.append((row['name'],m,[0,0,0]))
save_3mf(DEST/'reference/DO-NOT-PRINT-solved.3mf',assembly)
(DEST/'manifest.json').write_text(json.dumps(meta,indent=2))
unchanged=[]
for row in meta['parts']:
 if row['name'].startswith(('E','K')) or row['name']=='core':
  assert (V1/row['file']).read_bytes()==(DEST/row['file']).read_bytes();unchanged.append(row['name'])
(DEST/'reports/revision.json').write_text(json.dumps(dict(passed=True,manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),changes=changes,unchanged_puzzle_parts=unchanged,washer_seat_old_mm=27.3,washer_seat_new_mm=SEAT),indent=2))
print('UNCHANGED',unchanged,flush=True)
