"""Area on the six cube planes lost specifically to assembly relief."""
from design import *
report={}
for f in 'WEF':
 lost=load(CACHE/f'raw-{f}.npz')-load(CACHE/f'prepared-{f}.npz')
 bysize={}
 for size in [68,70,72,74]:
  cube=xform(mf.Manifold.cube([size]*3,True),R);total=0.;records={}
  for row in [r for r in ROWS if r['family']==f]:
   piece=xform(lost,mapping(canonical(f)['signature'],row['signature']))^cube;m=mesh(piece);a=0
   for j in range(3):
    for sign in [-1,1]:
     n=R[:,j]*sign;hit=(m.face_normals@n>.9999)&(np.min(m.triangles@n,axis=1)>size/2-.001);a+=float(m.area_faces[hit].sum())
   records[row['name']]=a;total+=a
  bysize[str(size)]=dict(total_area_mm2=total,by_piece=records);print('SKIN LOSS',f,size,total,flush=True)
 report[f]=bysize
(WORK/'skin-check.json').write_text(json.dumps(report,indent=2)+'\n')
