"""Measure retained spherical contact faces from the actual delivered STLs."""
from retention_v2 import *
def run():
 cells,_=load_parts();records=[]
 for f in ORBITS:
  m=mesh(cells[canonical(f)['name']]);v=m.triangles;rs=np.linalg.norm(v,axis=2);centers=m.triangles_center;radial=centers/np.linalg.norm(centers,axis=1)[:,None];dot=np.einsum('ij,ij->i',m.face_normals,radial)
  inner_offset=BODY_GAP/2+(PETAL_WALL_EXTRA if f=='P' else 0)
  for radius,label,sign in [(SHOULDER_R-inner_offset,'foot outer bearing',1),(SHOULDER_R+BODY_GAP/2+TRACK_EXTRA,'collar inner bearing',-1),(COLLAR_OUTER_R+inner_offset,'outer return',-1),(COLLAR_OUTER_R-BODY_GAP/2-TRACK_EXTRA,'outer return',1)]:
   selected=(np.max(abs(rs-radius),axis=1)<.025)&(dot*sign>.999)
   area=float(m.area_faces[selected].sum())
   if area>.01:records.append(dict(family=f,surface=label,nominal_radius_mm=radius,area_mm2=area,triangles=int(selected.sum()),maximum_normal_deviation_from_radial_degrees=float(np.degrees(np.arccos(np.clip((dot*sign)[selected],-1,1))).max())))
 for r in records:print('SPHERICAL BEARING',r,flush=True)
 assert any(r['family']=='C' and r['surface']=='collar inner bearing' and r['area_mm2']>10 for r in records)
 assert any(r['family']=='P' and r['surface']=='foot outer bearing' and r['area_mm2']>10 for r in records)
 assert any(r['family']=='P' and r['surface']=='collar inner bearing' and r['area_mm2']>5 for r in records)
 assert any(r['family']=='K' and r['surface']=='foot outer bearing' and r['area_mm2']>5 for r in records)
 (DEST/'reports/spherical-shoulders.json').write_text(json.dumps(dict(radius_mm=SHOULDER_R,collar_outer_radius_mm=COLLAR_OUTER_R,meridian_step_angle_degrees=.25,assembly_relief_applied=False,records=records,scope='Area of near-spherical triangles in each individual part; not the simultaneously contacting area or a force rating.'),indent=2)+'\n')
if __name__=='__main__':run()
