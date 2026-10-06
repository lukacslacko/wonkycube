"""Audit real spherical bearing faces and capture by screwed centers alone."""
from checks import *
def run():
 cells=get('printed');records=[]
 for f in ORBITS:
  m=mesh(cells[canonical(f)['name']]);rs=np.linalg.norm(m.triangles,axis=2);centers=m.triangles_center;radial=centers/np.linalg.norm(centers,axis=1)[:,None];dot=np.einsum('ij,ij->i',m.face_normals,radial)
  for radius,label,sign in [(SHOULDER_R-BODY_GAP/2,'foot outer bearing',1),(SHOULDER_R+BODY_GAP/2+TRACK_EXTRA,'collar inner bearing',-1),(COLLAR_OUTER_R+BODY_GAP/2,'groove outer wall',-1),(COLLAR_OUTER_R-BODY_GAP/2-TRACK_EXTRA,'collar outer bearing',1)]:
   selected=(np.max(abs(rs-radius),axis=1)<.025)&(dot*sign>.999)
   area=float(m.area_faces[selected].sum())
   if area>.01:records.append(dict(family=f,surface=label,nominal_radius_mm=radius,area_mm2=area,triangles=int(selected.sum()),maximum_normal_deviation_from_radial_degrees=float(np.degrees(np.arccos(np.clip((dot*sign)[selected],-1,1))).max())))
 for r in records:print('SPHERICAL BEARING',r,flush=True)
 for f in ['T','S']:assert any(r['family']==f and r['surface']=='collar inner bearing' and r['area_mm2']>10 for r in records)
 assert any(r['family']=='P' and r['surface']=='foot outer bearing' and r['area_mm2']>10 for r in records)
 row=canonical('P');s0=cells[row['name']]^mf.Manifold.sphere(SHOULDER_R-.015,SEG);n0=np.array(row['direction']);probes=[]
 for axis in [0,8]:
  for angle in np.linspace(0,120 if axis<8 else 90,5):
   q=Rotation.from_rotvec(AXES[axis]*np.radians(angle)).as_matrix();s=xform(s0,q);n=q@n0;F=frame(n)
   # Only the fixed-to-core centers count; neighboring floating shells do not.
   fixed=union([(xform(cells[r['name']],q) if axis in r['signature'] else cells[r['name']]).translate(np.array(r['direction'])*.15) for r in ROWS[:14]])
   directions=[n]+[unit(n+slope*(np.cos(t)*F[:,0]+np.sin(t)*F[:,1])) for slope in [.35,.7] for t in np.arange(6)*np.pi/3]
   found=[hit(s,fixed,d,np.arange(.1,3.01,.1)) for d in directions]
   assert all(x is not None and x['distance_mm']<1.51 for x in found),('spherical foot escape',axis,angle,found)
   probes.append(dict(axis=axis,angle_degrees=float(angle),center_lift_mm=.15,contacts=found))
   print('INNER FOOT CAPTURE',axis,angle,max(x['distance_mm'] for x in found),flush=True)
 result=dict(passed=True,shoulder_radius_mm=SHOULDER_R,collar_outer_radius_mm=COLLAR_OUTER_R,nominal_gap_per_bearing_face_mm=BODY_GAP+TRACK_EXTRA,assembly_relief_applied=False,records=records,inner_foot_capture=probes,scope='Measured individual bearing-face areas, not simultaneous contact areas or load ratings. Finite extraction rays of the inner petal foot against screwed centers only, with 0.15 mm center lift; not a proof against all elastic escape paths.')
 (DEST/'reports/spherical-retention.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
