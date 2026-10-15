"""Laminated-paper cutting sheets with a removable A4 scaling rectangle."""
from inlays import *
from shapely.affinity import translate
from shapely.geometry import box
import ezdxf,subprocess,os,html,csv
from mesh_io import cleaned

COLORS=['#e64c45','#ff9744','#4cad66','#4b95d9','#f4d44f','#eeeeee','#8c76cd','#dc76b0','#47bfb8','#bc783f','#a8ce6a','#809abe','#cf8a75','#d7bc9a']

def shape_path(p,svg=False):
 points=np.array(p.exterior.coords)[:-1]
 return 'M '+' L '.join(f'{x:.4f},{y:.4f}' for x,y in points)+' Z'

def write_sheet(stem,items,size=(82,82)):
 """Center the unchanged mm-size inlays inside one removable A4 rectangle.

 The frame is a single closed entity on A4_FRAME_DELETE_BEFORE_CUTTING.
 It deliberately contributes to import bounds; remove it after scaling.
 """
 stem.parent.mkdir(parents=True,exist_ok=True)
 a4=(210.,297.);old_bounds=unary_union([p for _,p in items]).bounds
 dx=a4[0]/2-(old_bounds[0]+old_bounds[2])/2;dy=a4[1]/2-(old_bounds[1]+old_bounds[3])/2
 items=[(label,translate(p,dx,dy)) for label,p in items]
 outline=box(0,0,*a4);frame_layer='A4_FRAME_DELETE_BEFORE_CUTTING'
 entities=[(label,p,'CUT') for label,p in items]+[('A4 scaling frame',outline,frame_layer)]
 # Cameo-friendly R13 ASCII with classic closed 2D POLYLINE entities.
 # Each outline is one continuous cut, not hundreds of independent lines.
 lines=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1012','9','$INSUNITS','70','4','9','$MEASUREMENT','70','1','0','ENDSEC','0','SECTION','2','ENTITIES']
 for label,p,layer in entities:
  assert p.is_valid and not p.interiors and p.area>0
  pts=np.array(p.exterior.coords)[:-1]
  lines+=['0','POLYLINE','100','AcDbEntity','8',layer,'100','AcDb2dPolyline','66','1','10','0','20','0','30','0','70','1']
  for a in pts:
   lines+=['0','VERTEX','100','AcDbEntity','8',layer,'100','AcDbVertex','100','AcDb2dVertex','10',f'{a[0]:.6f}','20',f'{a[1]:.6f}','30','0','70','0']
  lines+=['0','SEQEND','100','AcDbEntity','8',layer]
 lines+=['0','ENDSEC','0','EOF'];stem.with_suffix('.dxf').write_text('\n'.join(lines)+'\n')
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="210mm" height="297mm" viewBox="0 0 210 297"><g id="CUT" transform="translate(0 297) scale(1 -1)" fill="none" stroke="black" stroke-width="0.1">']
 for label,p in items:svg.append(f'<path d="{shape_path(p)}"/>')
 svg.append('</g><g id="A4_FRAME_DELETE_BEFORE_CUTTING" fill="none" stroke="red" stroke-width="0.1"><rect x="0" y="0" width="210" height="297"/></g></svg>');stem.with_suffix('.svg').write_text(''.join(svg))
 # Use a full R2000 document as the source for genuine DWG encoding.
 doc=ezdxf.new('R2000');doc.units=4;doc.header['$MEASUREMENT']=1;doc.layers.new('CUT');doc.layers.new(frame_layer,dxfattribs={'color':1})
 for label,p,layer in entities:doc.modelspace().add_lwpolyline(np.array(p.exterior.coords)[:-1],close=True,dxfattribs={'layer':layer})
 tmp=CACHE/'dwg-source';tmp.mkdir(exist_ok=True);src=tmp/(stem.name+'.dxf');doc.saveas(src)
 imported=ezdxf.readfile(stem.with_suffix('.dxf'));ls=list(imported.modelspace());assert len(ls)==len(entities) and all(e.dxftype()=='POLYLINE' and e.is_closed for e in ls)
 for e,(_,p,layer) in zip(ls,entities):assert e.dxf.layer==layer and Polygon([(v[0],v[1]) for v in e.points()]).hausdorff_distance(p)<.000002
 ext=unary_union([p for _,p in items]).bounds
 assert outline.buffer(-5).contains(unary_union([p for _,p in items]))
 return dict(file=stem.name,path=stem.relative_to(DEST).as_posix(),contours=len(items),scaling_frame_count=1,scaling_frame_layer=frame_layer,extents_mm=[0.,0.,*a4],width_mm=a4[0],height_mm=a4[1],inlay_extents_mm=list(ext),inlay_width_mm=ext[2]-ext[0],inlay_height_mm=ext[3]-ext[1],dxf_closed_polyline_count=len(ls))

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
  entities=list(returned.modelspace());initial=list(source.modelspace());assert len(entities)==len(initial)==rec['contours']+rec['scaling_frame_count']
  # Converters may reorder entities; compare each complete closed polygon.
  original=[(e.dxf.layer,Polygon([(v[0],v[1]) for v in e.get_points()])) for e in initial]
  errors=[]
  for e in entities:
   assert e.dxftype()=='LWPOLYLINE' and e.closed
   q=Polygon([(v[0],v[1]) for v in e.get_points()]);best=min(range(len(original)),key=lambda i:q.hausdorff_distance(original[i][1]) if original[i][0]==e.dxf.layer else 1e9);layer,pg=original.pop(best);assert layer==e.dxf.layer;err=q.hausdorff_distance(pg);assert err<.00001;errors.append(err)
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
  # The optional easy set gives 0.05 mm clearance per side.
  # Choose one set; both fit the same plastic pockets.
  for variant,delta in [('easy',-.05)]:
   alt=[(name,p.buffer(delta,quad_segs=12).simplify(.008,preserve_topology=True)) for name,p in sheet]
   report.append(write_sheet(DEST/'inlays/fit-variants'/variant/(variant+'-'+label),alt))
  facemap.append(dict(id=label,normal=n.tolist(),color=COLORS[fi],inlays=[dict(piece=item['piece'],canonical_template=item['record_id'],cut_outline=coords(item['polygon'])) for item in pieces]))
  print('CUT FACE',label,len(pieces),flush=True)
 # Rectangular coupon: exact, 0.05 and 0.10 mm inset paper outlines.
 # Default is exact contour. Adhesive, not compression, secures laminate.
 pg=box(-7,-5,7,5).buffer(-.6).buffer(.6,quad_segs=12)
 coupon_height=DEPTH+1.9
 block=mf.Manifold.cube([20,16,coupon_height],False).translate([-10,-8,0])
 block=block-cross(pg).extrude(DEPTH+1).translate([0,0,1.9])
 cleaned(mesh(block)).export(DEST/'stl/fit-coupons/paper-pocket-test.stl')
 tests=[]
 for i,growth in enumerate([0.,-.05,-.10]):tests.append((f'per-side-{growth:+.2f}',translate(pg.buffer(growth,quad_segs=12),12+22*i,10)))
 report.append(write_sheet(DEST/'inlays/fit-test/paper-size-options',tests,(70,22)))
 report.append(write_sheet(DEST/'inlays/fit-test/calibration-20mm', [('20 mm square',box(0,0,20,20))],(20,20)))
 (DEST/'reference/inlay-faces.json').write_text(json.dumps(facemap,indent=2)+'\n')
 (DEST/'reports/cutting-files.json').write_text(json.dumps(report,indent=2)+'\n')
 (DEST/'reports/inlay-pockets.json').write_text((CACHE/'inlays.json').read_text())
 with (DEST/'inlays/sheet-dimensions.csv').open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['file','inlay_contours','removable_A4_frames','selection_width_mm','selection_height_mm','inlays_only_width_mm','inlays_only_height_mm'])
  for rec in report:writer.writerow([str(Path(rec['path']).relative_to('inlays'))+'.dxf',rec['contours'],1,f'{rec["width_mm"]:.6f}',f'{rec["height_mm"]:.6f}',f'{rec["inlay_width_mm"]:.6f}',f'{rec["inlay_height_mm"]:.6f}'])
 print('PAPER TOTAL',len(items),flush=True)

if __name__=='__main__':
 import sys
 verify_dwgs() if '--verify-dwg' in sys.argv else export_cutting()
