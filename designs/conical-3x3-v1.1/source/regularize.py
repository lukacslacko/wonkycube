"""Bounded mesh simplification before exterior finishing (millimetres)."""
from conical_design import *
records=[]
for f in ['C','E','K']:
 path=CACHE/'ridges-3'/(f+'.npz');s=load(path);a=main(s.as_original().simplify(.001))
 save(a,path)
 records.append(dict(family=f,tolerance_mm=.001,before_triangles=s.num_tri(),after_triangles=a.num_tri(),before_volume_mm3=s.volume(),after_volume_mm3=a.volume()))
 print('REGULARIZE',records[-1],flush=True)
(CACHE/'regularization.json').write_text(json.dumps(records,indent=2))
