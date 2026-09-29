from stress_jumbling import *
p=ExactPuzzle();states=np.tile(np.eye(3),(44,1,1));items=[load(CACHE/'printed'/(r['name']+'.npz')) for r in ROWS];theta=np.degrees(np.arccos(1/3))
for a,angle in [(2,theta),(7,theta-180)]:
 chosen=dict(p.legal(states))[a];q=Rotation.from_rotvec(AXES[a]*np.radians(angle)).as_matrix();states[chosen]=q@states[chosen]
chosen=set(dict(p.legal(states))[0]);report=[]
for angle in [30,60,90,120,150,180]:
 q=Rotation.from_rotvec(AXES[0]*np.radians(angle)).as_matrix();solids=[xform(s,(q@states[i]) if i in chosen else states[i]) for i,s in enumerate(items)];bounds=[np.array(s.bounding_box()).reshape(2,3) for s in solids]
 for i in chosen:
  for j in set(range(44))-chosen:
   if np.any(bounds[i][1]<bounds[j][0]) or np.any(bounds[j][1]<bounds[i][0]):continue
   intersection=solids[i]^solids[j];vol=intersection.volume()
   if vol>.001:
    m=mesh(intersection);r=np.linalg.norm(m.vertices,axis=1);print(angle,ROWS[i]['name'],ROWS[j]['name'],vol,r.min(),r.max(),m.bounds.tolist(),flush=True)
    report.append(dict(angle=angle,moving=ROWS[i]['name'],fixed=ROWS[j]['name'],volume_mm3=vol,radii_mm=[float(r.min()),float(r.max())]))
(WORK/'collision-analysis.json').write_text(json.dumps(report,indent=2)+'\n')
