"""Geometric corner waist measurements, not a stress/fatigue simulation."""
from hardware import *
from section_connectivity import polygons
from shapely.geometry import Point
DEST=Path(os.environ.get('CUBOCTA_RELEASE',WORK/'release'))
def run():
 meta=json.loads((DEST/'manifest.json').read_text());r=next(r for r in meta['parts'] if r['family']=='K');m=trimesh.load(DEST/r['file'],force='mesh');T=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3];s=xform(from_mesh(m),frame(canonical('K')['direction']).T);records=[]
 for z in np.arange(23.,38.,.05):
  ps=polygons(s.slice(float(z)));center=next((p for p in ps if p.covers(Point(0,0))),None);assert center is not None
  records.append(dict(radial_station_mm=float(z),connected_center_area_mm2=float(center.area),centered_inscribed_radius_mm=float(center.boundary.distance(Point(0,0)))))
 report=dict(minimum_centered_solid_diameter_mm=2*min(r['centered_inscribed_radius_mm'] for r in records),minimum_connected_cross_section_mm2=min(r['connected_center_area_mm2'] for r in records),sampling_mm=.05,range_mm=[23,38],records=records,scope='Minimum sampled centered solid disk and connected neck cross-section, not a material strength rating.')
 assert report['minimum_centered_solid_diameter_mm']>3.25
 (DEST/'reports/corner-neck.json').write_text(json.dumps(report,indent=2)+'\n');print('CORNER NECK', {k:v for k,v in report.items() if k!='records'},flush=True)
if __name__=='__main__':run()
