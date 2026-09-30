from design import *
meta=json.loads((HERE/'reused/manifest.json').read_text());r=next(r for r in meta if r['name']=='core');m=trimesh.load(HERE/r['file'],force='mesh');t=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3];core=from_mesh(m)
pads={f:load(CACHE/f'guide-{f}.npz') for f in 'WE'};report={'support':[],'strength':{}}
for axis in range(4):
 for depth in [1,2]:
  records=[]
  for angle in range(0,121,3):
   q=Rotation.from_rotvec(np.radians(angle)*AXES[axis]).as_matrix()
   for row in ROWS:
    if row['family'] not in pads or row['signature'][axis]<depth:continue
    f=row['family'];pose=q@mapping(canonical(f)['signature'],row['signature']);n=q@np.array(row['direction']);p=xform(pads[f],pose)
    volumes=[max(0.,(p.translate(-d*n)^core).volume()) for d in [.25,.4,.6]];first=next((d for d,v in zip([.25,.4,.6],volumes) if v>.002),None)
    assert first is not None and first<=.4,(axis,depth,angle,row['name'],first,volumes)
    records.append(dict(name=row['name'],angle_degrees=angle,first_contact_mm=first,overlap_at_0_25_mm3=volumes[0],overlap_at_0_4_mm3=volumes[1]))
  worst=max(records,key=lambda x:x['first_contact_mm']);rec=dict(axis=axis,depth=depth,positions=len(records),worst=worst,min_overlap_at_0_25_mm3=min(x['overlap_at_0_25_mm3'] for x in records),weakest=min(records,key=lambda x:x['overlap_at_0_25_mm3']))
  report['support'].append(rec);print('SUPPORT',rec,flush=True)
for f in 'WE':
 body=load(CACHE/'guided'/(canonical(f)['name']+'.npz'))^mf.Manifold.sphere(BASE_RADII[f]+2.,SEG)
 eroded=body.minkowski_difference(mf.Manifold.sphere(.6,20));parts=sorted(eroded.decompose(),key=lambda s:s.volume(),reverse=True)
 contact=(parts[0]^mf.Manifold.sphere(20.7,96)).volume();connection=(parts[0]-mf.Manifold.sphere(BASE_RADII[f]+.2,96)).volume()
 assert contact>.2 and connection>1,(f,'pad neck',contact,connection)
 report['strength'][f]=dict(erosion_radius_mm=.6,connected_near_core_volume_mm3=contact,connected_outer_attachment_volume_mm3=connection)
 print('PAD NECK',f,report['strength'][f],flush=True)
report['scope']='Finite tests of guide pads against the exact original core, including its nut-slot openings. Non-retaining pads; actual capture remains at the four ordered layers. Morphological neck probe is not a force/fatigue simulation.'
(DEST/'reports/guide-pads.json').write_text(json.dumps(report,indent=2)+'\n')
