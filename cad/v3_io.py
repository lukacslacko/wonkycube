"""Mesh export and print-orientation helpers for the prototype."""

from mechanism import *

import zipfile, xml.etree.ElementTree as ET

from matplotlib.textpath import TextPath

NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'

ET.register_namespace('',NS)

def collapse_export_slits(candidate):
 """Collapse only near-collinear boundary loops no longer than 0.002 mm.

 Float32 can flatten a tiny arc into a line, leaving a long edge opposite
 several collinear short edges. This is a collapsed slit, not a real hole.
 Move its vertices by at most 0.002 mm; never cap a finite-area opening.
 """
 edges=candidate.edges_unique[np.bincount(candidate.edges_unique_inverse)==1]
 if not len(edges):return candidate
 adjacency={}
 for a,b in edges:
  adjacency.setdefault(int(a),set()).add(int(b));adjacency.setdefault(int(b),set()).add(int(a))
 unseen=set(adjacency);groups=[]
 while unseen:
  todo=[unseen.pop()];group=[]
  while todo:
   a=todo.pop();group.append(a)
   for b in adjacency[a]:
    if b in unseen:unseen.remove(b);todo.append(b)
  groups.append(group)
 c=candidate.copy();changed=False
 for ids in groups:
  if any(len(adjacency[i])!=2 for i in ids):continue
  points=c.vertices[ids];center=points.mean(axis=0);d=points-center
  if np.linalg.norm(np.ptp(points,axis=0))>.002:continue
  _,_,vh=np.linalg.svd(d,full_matrices=False)
  if np.linalg.norm(d-(d@vh[0])[:,None]*vh[0],axis=1).max()>1e-6:continue
  c.vertices[ids]=center.astype(np.float32).astype(float);changed=True
 if changed:
  c.merge_vertices(digits_vertex=8);c.update_faces(c.nondegenerate_faces());c.update_faces(c.unique_faces());c.remove_unreferenced_vertices()
 return c

def clean_mesh(m):
 # Boolean intersections may contain topologically harmless sub-micron
 # slivers. STL float32 welding collapses them. Quantize far below printing
 # resolution, weld, and explicitly remove only degenerate/duplicate faces.
 for simplification in [0,.002]:
  source=m if not simplification else mesh(from_mesh(m).simplify(simplification))
  for digits in [6,5,4,3]:
   candidate=source.copy();candidate.vertices=np.round(candidate.vertices,digits).astype(np.float32).astype(float)
   candidate.merge_vertices(digits_vertex=8)
   candidate.update_faces(candidate.nondegenerate_faces());candidate.update_faces(candidate.unique_faces())
   candidate.remove_unreferenced_vertices()
   if candidate.is_watertight and candidate.is_winding_consistent:return candidate
   repaired=collapse_export_slits(candidate)
   if repaired.is_watertight and repaired.is_winding_consistent:return repaired
 raise ValueError('Could not produce a closed STL mesh within 0.002 mm simplification and 0.001 mm quantization')

def write_stl(s,path):clean_mesh(mesh(s)).export(path)

def label_shape(text,height=3.2,depth=.5):
 p=TextPath((0,0),text,size=height)
 contours=p.to_polygons()
 return mf.CrossSection(contours,mf.FillRule.EvenOdd).extrude(depth)

def stand():
 base=mf.Manifold.cylinder(4,32,32,128)
 body=mf.Manifold.cylinder(32,8,8,96)
 taper=mf.Manifold.cylinder(4,8,4.6,96).translate([0,0,32])
 neck=mf.Manifold.cylinder(34,4.6,4.6,96).translate([0,0,36])
 bore=mf.Manifold.cylinder(72,1.7,1.7,64)
 cb=mf.Manifold.cylinder(55,3.1,3.1,64)
 return union([base,body,taper,neck])-union([bore,cb])

def print_orient(s,kind,Rcube,n=None):
 m=clean_mesh(mesh(s))
 if kind in ('edge','corner'):
  # Place the largest surviving original exterior cube face on the bed.
  best=None
  for j in range(3):
   for sign in [-1,1]:
    normal=Rcube[:,j]*sign
    hit=np.min(m.triangles@normal,axis=1)>39.999
    area=m.area_faces[hit].sum()
    if best is None or area>best[0]:best=(area,normal)
  if best[0]<=1:raise ValueError('No exterior printing face')
  R=Rotation.align_vectors([[0,0,-1]],[best[1]])[0].as_matrix()
 elif kind=='core':R=frame(-AXES[0]).T
 elif kind=='cap':R=frame(n).T
 else:R=np.eye(3)
 v=m.vertices@R.T
 if kind in ('edge','corner'):
  # Turn the flat bed face in-plane to leave room for support/brim margins.
  target=np.array([112,72] if kind=='edge' else [112,112])
  best=None
  for angle in np.arange(0,180,.5):
   rz=Rotation.from_euler('z',angle,degrees=True).as_matrix()
   bounds=np.ptp(v@rz.T,axis=0)[:2]
   cost=max(bounds/target)
   if best is None or cost<best[0]:best=(cost,rz)
  R=best[1]@R;v=m.vertices@R.T
 shift=-np.r_[((v.min(axis=0)+v.max(axis=0))/2)[:2],v[:,2].min()]
 m.vertices=v+shift
 return clean_mesh(m),matrix(R,shift).tolist()

def q(n):return '{'+NS+'}'+n

def save_3mf(path,objects):
 # Standard geometry-only 3MF, deliberately without unverified slicer profiles.
 model=ET.Element(q('model'),{'unit':'millimeter','xml:lang':'en-US'})
 md=ET.SubElement(model,q('metadata'),{'name':'Title'});md.text=path.stem
 resources=ET.SubElement(model,q('resources'));build=ET.SubElement(model,q('build'))
 for idx,(name,m,translation) in enumerate(objects,1):
  obj=ET.SubElement(resources,q('object'),{'id':str(idx),'type':'model','name':name})
  geo=ET.SubElement(obj,q('mesh'));vs=ET.SubElement(geo,q('vertices'));ts=ET.SubElement(geo,q('triangles'))
  for v in m.vertices:
   ET.SubElement(vs,q('vertex'),dict(zip(['x','y','z'],[f'{x:.6f}' for x in v])))
  for f in m.faces:ET.SubElement(ts,q('triangle'),dict(zip(['v1','v2','v3'],map(str,f))))
  x,y,z=translation
  ET.SubElement(build,q('item'),{'objectid':str(idx),'transform':f'1 0 0 0 1 0 0 0 1 {x:.6f} {y:.6f} {z:.6f}'})
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
