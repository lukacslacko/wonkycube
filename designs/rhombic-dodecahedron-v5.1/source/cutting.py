"""Cut-only DXF/SVG/DWG sheets, with separate labelled assembly maps."""
from inlays import *
from shapely.affinity import translate
from shapely.geometry import box
import ezdxf,subprocess,os,html
from mesh_io import cleaned

COLORS=['#e5484d','#ff9470','#eea323','#f0d94c','#79bc4b','#27a083','#30b4c5','#4583cb','#6463bf','#ac68bd','#eb87ad','#e5ddd1']

def shape_path(p,svg=False):
 points=np.array(p.exterior.coords)[:-1]
 return 'M '+' L '.join(f'{x:.4f},{y:.4f}' for x,y in points)+' Z'

def write_sheet(stem,items,size=(82,82)):
 """items: (label, polygon). No text, registration marks or duplicate cuts."""
 stem.parent.mkdir(parents=True,exist_ok=True)
 # Cameo-friendly R13 ASCII with classic closed 2D POLYLINE entities.
 # Each outline is one continuous cut, not hundreds of independent lines.
 lines=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1012','9','$INSUNITS','70','4','9','$MEASUREMENT','70','1','0','ENDSEC','0','SECTION','2','ENTITIES']
 for label,p in items:
  assert p.is_valid and not p.interiors and p.area>0
  pts=np.array(p.exterior.coords)[:-1]
  lines+=['0','POLYLINE','100','AcDbEntity','8','CUT','100','AcDb2dPolyline','66','1','10','0','20','0','30','0','70','1']
  for a in pts:
   lines+=['0','VERTEX','100','AcDbEntity','8','CUT','100','AcDbVertex','100','AcDb2dVertex','10',f'{a[0]:.6f}','20',f'{a[1]:.6f}','30','0','70','0']
  lines+=['0','SEQEND','100','AcDbEntity','8','CUT']
 lines+=['0','ENDSEC','0','EOF'];stem.with_suffix('.dxf').write_text('\n'.join(lines)+'\n')
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{size[0]}mm" height="{size[1]}mm" viewBox="0 0 {size[0]} {size[1]}"><g transform="translate(0 {size[1]}) scale(1 -1)" fill="none" stroke="black" stroke-width="0.1">']
 for label,p in items:svg.append(f'<path d="{shape_path(p)}"/>')
 svg.append('</g></svg>');stem.with_suffix('.svg').write_text(''.join(svg))
 # Use a full R2000 document as the source for genuine DWG encoding.
 doc=ezdxf.new('R2000');doc.units=4;doc.header['$MEASUREMENT']=1;doc.layers.new('CUT')
 for label,p in items:doc.modelspace().add_lwpolyline(np.array(p.exterior.coords)[:-1],close=True,dxfattribs={'layer':'CUT'})
 tmp=CACHE/'dwg-source';tmp.mkdir(exist_ok=True);src=tmp/(stem.name+'.dxf');doc.saveas(src)
 imported=ezdxf.readfile(stem.with_suffix('.dxf'));ls=list(imported.modelspace());assert len(ls)==len(items) and all(e.dxftype()=='POLYLINE' and e.is_closed for e in ls)
 for e,(_,p) in zip(ls,items):assert Polygon([(v[0],v[1]) for v in e.points()]).hausdorff_distance(p)<.000002
 ext=unary_union([p for _,p in items]).bounds
 return dict(file=stem.name,path=stem.relative_to(DEST).as_posix(),contours=len(items),extents_mm=list(ext),width_mm=ext[2]-ext[0],height_mm=ext[3]-ext[1],dxf_closed_polyline_count=len(ls))

def verify_dwgs():
 import shutil
 report=json.loads((DEST/'reports/cutting-files.json').read_text())
 for rec in report:
  stem=DEST/rec['path'];dwg=CACHE/'dwg-output'/(stem.name+'.dwg');assert dwg.read_bytes()[:6]==b'AC1015'
  shutil.copy2(dwg,stem.with_suffix('.dwg'))
  back=CACHE/'dwg-output'/(stem.name+'-roundtrip.dxf')
  run=subprocess.run([str(Path(os.environ['DWG_TOOL_DIR'])/'dwg2dxf'),'-y','-o',str(back),str(dwg)],capture_output=True,text=True)
  assert run.returncode==0
  returned=ezdxf.readfile(back);audit=returned.audit();assert not audit.errors
  source=ezdxf.readfile(CACHE/'dwg-source'/(stem.name+'.dxf'))
  entities=list(returned.modelspace());initial=list(source.modelspace());assert len(entities)==len(initial)==rec['contours']
  # Converters may reorder entities; compare each complete closed polygon.
  original=[Polygon([(v[0],v[1]) for v in e.get_points()]) for e in initial]
  errors=[]
  for e in entities:
   assert e.dxftype()=='LWPOLYLINE' and e.closed
   q=Polygon([(v[0],v[1]) for v in e.get_points()]);best=min(range(len(original)),key=lambda i:q.hausdorff_distance(original[i]));err=q.hausdorff_distance(original.pop(best));assert err<.00001;errors.append(err)
  rec.update(dwg_roundtrip_max_error_mm=max(errors),dwg_encoding='AC1015 / AutoCAD 2000',converter='ODA File Converter 27.9',independent_reader='GNU LibreDWG 0.14 / ezdxf 1.4.4',audit_errors=0)
 (DEST/'reports/cutting-files.json').write_text(json.dumps(report,indent=2)+'\n')
 print('DWG VERIFIED',len(report),flush=True)

def instance_inlays():
 records=json.loads((CACHE/'inlays.json').read_text())['records'];out=[]
 for row in ROWS:
  q=mapping(canonical(row['family'])['signature'],row['signature'])
  for rec in records:
   if rec['family']!=row['family']:continue
   old=np.array(rec['frame']);F=q@old;n=F[:,2]
   faceindex=int(np.argmax([n@normal for normal,h,label in FACES]));normal,h,label=FACES[faceindex];assert n@normal>.999999
   target=frame(normal);p=polygon(rec['cut']);v=np.c_[np.array(p.exterior.coords)[:-1],np.full(len(p.exterior.coords)-1,h)]@F.T
   facepoly=Polygon(v@target[:,:2]);out.append(dict(piece=row['name'],face=label,face_index=faceindex,polygon=facepoly,solid=xform(fitted(rec),q),record_id=rec['id']))
 return out

def export_cutting():
 for path in ['inlays/faces','inlays/fit-test','images','reports','reference','stl/fit-coupons']:(DEST/path).mkdir(parents=True,exist_ok=True)
 items=instance_inlays();report=[];facemap=[]
 for fi,(n,h,label) in enumerate(FACES):
  pieces=[item for item in items if item['face']==label];sheet=[(item['piece'],translate(item['polygon'],41,41)) for item in pieces]
  report.append(write_sheet(DEST/'inlays/faces'/label,sheet))
  # Full alternative cut sets match the small coupon's other two sizes.
  # Plastic pockets remain identical; choose one cut set, not all three.
  for variant,delta in [('easy',-.08),('firm',.08)]:
   alt=[(name,p.buffer(delta,quad_segs=12).simplify(.008,preserve_topology=True)) for name,p in sheet]
   report.append(write_sheet(DEST/'inlays/fit-variants'/variant/(variant+'-'+label),alt))
  facemap.append(dict(id=label,normal=n.tolist(),color=COLORS[fi],inlays=[dict(piece=item['piece'],canonical_template=item['record_id'],cut_outline=coords(item['polygon'])) for item in pieces]))
  print('CUT FACE',label,len(pieces),flush=True)
 # Rectangular coupon: one nominal pocket, three foam cut sizes to choose
 # the smallest that grips without bowing. Actual puzzle nominal = +0.04/side.
 pg=box(-7,-5,7,5).buffer(-.6).buffer(.6,quad_segs=12)
 coupon_height=DEPTH+1.9
 block=mf.Manifold.cube([20,16,coupon_height],False).translate([-10,-8,0])
 block=block-cross(pg).extrude(DEPTH+1).translate([0,0,1.9])
 cleaned(mesh(block)).export(DEST/'stl/fit-coupons/foam-pocket-test.stl')
 tests=[]
 for i,growth in enumerate([-.04,.04,.12]):tests.append((f'per-side-{growth:+.2f}',translate(pg.buffer(growth,quad_segs=12),12+22*i,10)))
 report.append(write_sheet(DEST/'inlays/fit-test/foam-size-options',tests,(70,22)))
 report.append(write_sheet(DEST/'inlays/fit-test/calibration-20mm', [('20 mm square',box(0,0,20,20))],(20,20)))
 (DEST/'reference/inlay-faces.json').write_text(json.dumps(facemap,indent=2)+'\n')
 (DEST/'reports/cutting-files.json').write_text(json.dumps(report,indent=2)+'\n')
 (DEST/'reports/inlay-pockets.json').write_text((CACHE/'inlays.json').read_text())
 print('FOAM TOTAL',len(items),flush=True)

if __name__=='__main__':
 import sys
 verify_dwgs() if '--verify-dwg' in sys.argv else export_cutting()
