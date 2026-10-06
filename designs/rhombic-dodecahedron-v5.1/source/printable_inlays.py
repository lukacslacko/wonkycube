"""Rigid 2 mm inlays derived from the actual pocket contours, at exact nominal pocket size.

One STL and geometry-only 3MF per rhombic face, plus individual inserts.
No cut contour is enlarged for rigid plastic; foam compression is not reused.
"""
from inlays import *
from print_3mf import save_3mf, NS
from shapely.affinity import affine_transform,translate
import hashlib,zipfile,shutil,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPoly
from cutting import COLORS

CLEARANCE=0.0
PRINT_ROOT=DEST/'inlays/printable'

def run():
 for folder in ['faces','individual']:(PRINT_ROOT/folder).mkdir(parents=True,exist_ok=True)
 shutil.copy2(HERE/'LICENSE',PRINT_ROOT/'LICENSE')
 data=json.loads((DEST/'reports/inlay-pockets.json').read_text());records=data['records']
 meta=json.loads((DEST/'manifest.json').read_text());solids={};proof=[];instances=[];files=[]
 # Use the actual released main pieces and plugs, transformed back to mechanism coordinates.
 for rec in meta['parts']:
  if rec['family'] not in ORBITS+['TC','SC']:continue
  m=trimesh.load(DEST/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];solids[rec['family']]=from_mesh(m)
 for rec in records:
  pocket=polygon(rec['pocket']);pg=pocket if CLEARANCE==0 else pocket.buffer(-CLEARANCE,quad_segs=16)
  assert isinstance(pg,Polygon) and pg.is_valid and not pg.interiors and pg.area>10
  tile=cross(pg).extrude(THICKNESS)
  m=mesh(tile);temporary=trimesh.load(__import__('io').BytesIO(m.export(file_type='stl')),file_type='stl',force='mesh')
  assert temporary.is_watertight and temporary.is_winding_consistent and len(temporary.split())==1
  printed=from_mesh(temporary);normal=np.array(rec['frame'])[:,2]
  seated=xform(printed.translate([0,0,FACE_HEIGHT-DEPTH]),np.array(rec['frame']))
  flush=seated.translate(normal*.1)
  parent=solids[rec['family']]
  if rec['family'] in ['T','S']:parent=parent+solids[rec['family']+'C']
  collision=(flush^parent).volume()
  envelope=xform(cross(pocket).extrude(THICKNESS).translate([0,0,FACE_HEIGHT-THICKNESS]),np.array(rec['frame']))
  outside=(flush-envelope).volume();assert outside<.0001,(rec['id'],'nominal contour excess',outside)
  # Exported body meshes have bounded 0.005 mm simplification. At exact
  # nominal contact, tolerate only that boundary skin, not finite penetration.
  interior=cross(pg.buffer(-.006,quad_segs=16)).extrude(THICKNESS-.012).translate([0,0,FACE_HEIGHT-DEPTH+.006])
  interior=xform(interior,np.array(rec['frame']))
  beyond_skin=(interior.translate(normal*.1)^parent).volume();assert beyond_skin<.0001,(rec['id'],'penetration beyond mesh skin',beyond_skin)
  # Validate insertion of this inset audit probe; deliver the full exact tile.
  worst=0.
  for height in np.r_[np.arange(0,.401,.1),np.arange(.5,10.001,.5)]:worst=max(worst,(interior.translate(normal*height)^parent).volume())
  assert worst<.0001,(rec['id'],'insertion interference',worst)
  proof.append(dict(template=rec['id'],thickness_mm=THICKNESS,clearance_per_side_mm=CLEARANCE,plastic_collision_mm3=collision,outside_nominal_pocket_envelope_mm3=outside,boundary_mesh_skin_allowance_mm=.006,penetration_beyond_mesh_skin_mm3=beyond_skin,insertion_probe_collision_mm3=worst))
  for row in ROWS:
   if row['family']!=rec['family']:continue
   q=mapping(canonical(row['family'])['signature'],row['signature']);F=q@np.array(rec['frame']);fi=int(np.argmax([nn@F[:,2] for nn,_,_ in FACES]));normal,_,face=FACES[fi];target=frame(normal);A=target[:,:2].T@F[:,:2]
   assert np.linalg.det(A)>.999999,'Never mirror the visible inlay face.'
   facepoly=affine_transform(pg,[A[0,0],A[0,1],A[1,0],A[1,1],0,0])
   instances.append(dict(name=face+'-'+row['name'],face=face,face_index=fi,piece=row['name'],polygon=facepoly,template=rec['id']))
 assert len(instances)==96 and len({r['name'] for r in instances})==96
 def export_mesh(m,path,components):
  path.parent.mkdir(parents=True,exist_ok=True);m.export(path);m=trimesh.load(path,force='mesh');chunks=m.split(only_watertight=False)
  assert m.is_watertight and m.is_winding_consistent and len(chunks)==components and all(c.is_watertight and c.volume>0 for c in chunks),path
  assert abs(m.bounds[0,2])<1e-6 and abs(m.bounds[1,2]-THICKNESS)<1e-6
  files.append(dict(file=path.relative_to(DEST).as_posix(),components=components,watertight=True,thickness_mm=THICKNESS,volume_mm3=float(m.volume),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  return m
 faces=[]
 for fi,(_,_,face) in enumerate(FACES):
  items=sorted([r for r in instances if r['face']==face],key=lambda r:r['piece']);assert len(items)==8
  meshes=[];objects=[];placements=[]
  for r in items:
   # XY positions preserve the outside face view; Z=0 is the bed/back side.
   m=mesh(cross(r['polygon']).extrude(THICKNESS));mid=(m.bounds[0,:2]+m.bounds[1,:2])/2
   individual=m.copy();individual.vertices[:,:2]-=mid
   readback=export_mesh(individual,PRINT_ROOT/'individual'/face/(r['name']+'.stl'),1)
   restored=readback.copy();restored.vertices[:,:2]+=mid
   actual=region(from_mesh(restored).slice(1.));error=actual.hausdorff_distance(r['polygon']);assert error<.00001
   meshes.append(restored);objects.append((r['name'],restored,[128,128,0]));placements.append(dict(piece=r['piece'],file='individual/'+face+'/'+r['name']+'.stl',xy_center_in_face_mm=mid.tolist(),template=r['template'],contour_readback_error_mm=error))
  layout=export_mesh(trimesh.util.concatenate(meshes),PRINT_ROOT/'faces'/(face+'.stl'),8)
  assert np.max(np.ptp(layout.vertices,axis=0)[:2])<80
  for i,j in itertools.combinations(range(8),2):assert items[i]['polygon'].distance(items[j]['polygon'])>.5
  file3mf=PRINT_ROOT/'faces'/(face+'.3mf');save_3mf(file3mf,objects)
  with zipfile.ZipFile(file3mf) as z:
   root=ET.fromstring(z.read('3D/3dmodel.model'));assert root.attrib['unit']=='millimeter'
   rr=root.findall('{'+NS+'}resources/{'+NS+'}object');bb=root.findall('{'+NS+'}build/{'+NS+'}item');assert len(rr)==len(bb)==8
   for obj,it in zip(rr,bb):
    vertices=np.array([[float(v.attrib[k]) for k in ['x','y','z']] for v in obj.findall('{'+NS+'}mesh/{'+NS+'}vertices/{'+NS+'}vertex')]);t=np.array(list(map(float,it.attrib['transform'].split()))[-3:]);v=vertices+t
    assert np.all(v[:,:2]>10) and np.all(v[:,:2]<246) and abs(v[:,2].min())<1e-6 and abs(v[:,2].max()-THICKNESS)<1e-6
  faces.append(dict(face=face,pieces=[r['piece'] for r in items],stl='faces/'+face+'.stl',plate_3mf='faces/'+face+'.3mf',individuals=placements))
  print('PRINTABLE INLAYS',face,8,flush=True)
 # A flat placement map follows exactly the XY orientation of every face plate.
 fig,axes=plt.subplots(3,4,figsize=(12,11),facecolor='#fafaf8')
 for fi,(ax,(_,_,face)) in enumerate(zip(axes.flat,FACES)):
  for r in instances:
   if r['face']!=face:continue
   p=r['polygon'];ax.add_patch(PlotPoly(np.array(p.exterior.coords),facecolor=COLORS[fi],edgecolor='#32434b',lw=.55));center=p.representative_point();ax.text(center.x,center.y,r['piece'],ha='center',va='center',fontsize=8,color='#111827')
  ax.set(xlim=(-38,38),ylim=(-38,38),aspect='equal',title=face);ax.axis('off')
 fig.suptitle('Printable 2 mm inlays — eight separate inserts per face\nTop view matches the print plates and outside of the puzzle. Labels are on this map only.',fontsize=14)
 fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(PRINT_ROOT/'placement-map.png',dpi=150);plt.close(fig)
 report=dict(passed=True,thickness_mm=THICKNESS,clearance_per_side_mm=CLEARANCE,total_inlays=96,face_plates=12,templates=proof,files=files,faces=faces,scope='Reloaded STL dimensions, closure, connectivity and exact nominal pocket contours. Installed-fit/insertion probes allow only a 0.006 mm skin for body-mesh simplification at nominal contact. 3MF quantities/units/bed placement checked. Full exact-inlay motion is recorded separately in installed-rigid-inlays.json. The owner reports snug fit after cancelling the prior 0.15 mm clearance in the slicer.')
 (DEST/'reports/printable-inlays.json').write_text(json.dumps(report,indent=2)+'\n')
 (PRINT_ROOT/'manifest.json').write_text(json.dumps({k:report[k] for k in ['thickness_mm','clearance_per_side_mm','total_inlays','faces']},indent=2)+'\n')
 (PRINT_ROOT/'README.md').write_text('''# Printable 2 mm inlays

For the 76 mm vertex-turning rhombic dodecahedron, spherical v5.1 with 2.1 mm pockets. Mix these with the 2 mm foam inlays on any faces. The puzzle parts do not need reprinting.

Open **faces/F01.3mf** through **faces/F12.3mf** for the colors you want to print. Each file contains eight separate inlays for that rhombic face, positioned as viewed from outside. The matching **F01.stl–F12.stl** files contain the same eight disconnected inserts. Print each chosen face once, using either its STL or its 3MF. Do not print both. There is no connecting backing sheet or sprue.

For one replacement insert, use **individual/Fxx/Fxx-PieceID.stl**. The placement map identifies the destination pieces; the inlays themselves carry no printed labels. Keep each face's pieces together after removing them from the bed.

Print at **100% scale**, lying flat as supplied, with the visible side upward. On the P1S with a 0.4 mm nozzle, use your PLA profile, **0.20 mm layers and at least five top and five bottom layers** to make the 2 mm insert solid. No supports or brim are needed. Inspect the first-layer preview, keep elephant-foot compensation enabled, and print one face first to test the fit. The 3MF files contain geometry, not printer or filament presets.

The rigid inlays are **2.00 mm thick and exactly match the nominal pocket outline**, with **no size reduction or enlargement**. Set **XY contour compensation to 0.00 mm** for these files: do not add the earlier +0.15 mm correction. The owner found the nominal-size fit nicely snug; the reduced tiles were noticeably looser. A little glue remains optional. Without adhesive the top sits 0.10 mm below the plastic; use only a thin adhesive layer so it stays flush or recessed. Do not force a tight insert: remove any first-layer burr and test again. Foam and plastic can share the same puzzle without changing its turning geometry.

On screwed centers, an inlay bridges the main piece and central plug. Finish screw adjustment before gluing it. Avoid glue in the key socket and moving seams; removal of an inlay may be needed for later screw access. The cutting sheets remain the foam versions and should not be used to size rigid plastic.

`manifest.json` lists face contents and individual file mappings. Geometry checks cover the exported STLs, nominal contour fidelity, insertion and installed motion. The full puzzle is reported to build very well and turn smoothly. Nominal-size inlay fit was demonstrated by applying +0.15 mm contour compensation to the previous reduced tiles; these exports directly use the original pocket contour, without requiring that slicer correction. Exact regenerated toolpaths were not separately reprinted.
''')
 meta['printable_inlays']=dict(total=96,thickness_mm=THICKNESS,clearance_per_side_mm=CLEARANCE,xy_contour_compensation_mm=0.0,face_plates='inlays/printable/faces',individual_stls='inlays/printable/individual',placement_map='inlays/printable/placement-map.png',instructions='inlays/printable/README.md')
 (DEST/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('PRINTABLE INLAYS COMPLETE',len(files),'STLs',flush=True)
if __name__=='__main__':run()
