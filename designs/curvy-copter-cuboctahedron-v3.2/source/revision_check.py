"""Check radial outline fillets and the accepted unchanged v3.1 parts."""
from retention_v2 import *
from section_connectivity import polygons
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
BASE=Path(os.environ.get('CUBOCTA_V3_REFERENCE','outputs/natural-cuboctahedron-45deg-72mm-spherical-v3'))
ACCEPTED=Path(os.environ.get('CUBOCTA_V31_REFERENCE','outputs/natural-cuboctahedron-45deg-72mm-spherical-v3.1'))
def read_base(folder):
 meta=json.loads((folder/'manifest.json').read_text());out={}
 for rec in meta['parts']:
  if '/puzzle/' not in rec['file']:continue
  m=trimesh.load(folder/rec['file'],force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];out[rec['family']]=from_mesh(m)
 return meta,out

def outline_radius(poly,point):
 p=poly if poly.geom_type=='Polygon' else min(poly.geoms,key=lambda x:x.distance(point))
 curve=p.exterior;station=curve.project(point)
 a,b,c=np.array([curve.interpolate((station+t)%curve.length).coords[0] for t in [-.35,0,.35]])
 ab=b-a;ac=c-a;twice_area=abs(ab[0]*ac[1]-ab[1]*ac[0])
 return float(np.linalg.norm(ab)*np.linalg.norm(c-b)*np.linalg.norm(ac)/(2*twice_area))

def run():
 _,old=read_base(BASE);accepted,_=read_base(ACCEPTED);meta,new=read_base(DEST);reuse=[]
 for f in ['P','K','core']:
  a=next(r for r in accepted['parts'] if r['family']==f and '/puzzle/' in r['file']);b=next(r for r in meta['parts'] if r['family']==f and '/puzzle/' in r['file'])
  assert a['sha256']==b['sha256'],(f,'changed');reuse.append(dict(family=f,sha256=b['sha256'],byte_identical_to_v3_1=True))
 rounding=json.loads((CACHE/'flange-rounding.json').read_text());samples=[]
 for rec in rounding['corners']:
  F=np.array(rec['frame']);local=xform(new['C'],F);sections=rec['sections'];stations=np.array([p['station_mm'] for p in sections]);centers=np.array([p['center'] for p in sections])
  for z in [29.,30.5,32.]:
   center=np.array([np.interp(z,stations,centers[:,j]) for j in range(2)]);target=Point(center-[CENTER_FLANGE_END_ROUNDING,0]);poly=unary_union(polygons(local.slice(z)))
   radius=outline_radius(poly,target);distance=float(poly.exterior.distance(target)) if poly.geom_type=='Polygon' else min(p.exterior.distance(target) for p in poly.geoms)
   assert 1.15<radius<1.25,(rec['axes'],z,radius)
   assert distance<.025,(rec['axes'],z,distance)
   samples.append(dict(axes=rec['axes'],station_mm=z,measured_outline_radius_mm=radius,measurement_arc_spacing_mm=.35,distance_from_expected_circle_mm=distance))
 removed=old['C']-new['C'];added=new['C']-old['C'];outside=removed-mf.Manifold.sphere(35,SEG)
 assert added.volume()<.10,('unexpected added center volume',added.volume())
 assert outside.volume()<.04,('unexpected exterior alteration',outside.volume())
 m=mesh(new['C']);v=m.vertices[np.linalg.norm(m.vertices,axis=1)>35.];exterior_deviation=float(trimesh.proximity.closest_point(mesh(old['C']),v)[1].max());assert exterior_deviation<.012,('exterior deviation',exterior_deviation)
 report=dict(version=RELEASE_VERSION,unchanged_parts=reuse,flange_outline=rounding,final_stl_outline_measurements=samples,compared_with_original_v3_center=dict(removed_volume_mm3=float(removed.volume()),added_volume_mm3=float(added.volume()),removed_outside_R35_mm3=float(outside.volume()),added_volume_allowance_mm3=.10,outside_removed_allowance_mm3=.04,mesh_simplification_tolerance_mm=.005,sampled_exterior_deviation_mm=exterior_deviation),scope='R1.2 cylindrical-style outline rounding in planes perpendicular to each corner radial direction. Previous v3.1 0.95 mm whole-body rounding is absent. Unchanged parts checked by SHA256; finite geometry checks do not measure physical feel.')
 (DEST/'reports/revision-v3.2.json').write_text(json.dumps(report,indent=2)+'\n')
 print('REVISION CHECK',json.dumps({k:v for k,v in report.items() if k!='flange_outline'},indent=2),flush=True)
if __name__=='__main__':run()
