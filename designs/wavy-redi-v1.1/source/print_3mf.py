import zipfile, xml.etree.ElementTree as ET
NS="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("",NS)

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
   ET.SubElement(vs,q('vertex'),dict(zip(['x','y','z'],[f'{x:.9g}' for x in v])))
  for f in m.faces:ET.SubElement(ts,q('triangle'),dict(zip(['v1','v2','v3'],map(str,f))))
  x,y,z=translation
  ET.SubElement(build,q('item'),{'objectid':str(idx),'transform':f'1 0 0 0 1 0 0 0 1 {x:.6f} {y:.6f} {z:.6f}'})
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
  z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
  z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
