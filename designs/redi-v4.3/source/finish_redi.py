"""Clip canonical internals to the wonky cube and round exposed outer lips."""
from redi_design import *

def exterior(s):
 s=s.simplify(.002)
 kernel=mf.Manifold.sphere(OUTER_ROUND,24)
 protected=s^mf.Manifold.sphere(INNER_LIMIT,SEG)
 seed=s.minkowski_difference(kernel)+protected
 return main(seed.minkowski_sum(kernel)^s)

if __name__=='__main__':
 t=time.time();cube=xform(mf.Manifold.cube([SIDE]*3,True),R)
 canonical={f:load(OUT/f'canonical-{f}.npz') for f in ['C','E']}
 reference={'C':(7,),'E':EDGES[-1]}
 changes=[]
 for row in ROWS:
  name=row['name'];target=OUT/'final'/(name+'.npz')
  if target.exists() and name not in sys.argv[1:]:print(name,'cached',flush=True);continue
  q=mapping(reference[name[0]],row['signature'])
  s=xform(canonical[name[0]],q)^cube
  # v4.2 rounded the simpler raw exterior before adding the internal
  # lead-ins and R3 ridge cuts. Intersect with that exterior mask to preserve
  # the same operation order without an expensive opening of all fillets.
  raw=load(OUT/'raw'/(name+'.npz'))^cube
  if name[0]=='C':raw=finish_hardware(raw,np.array(row['direction']))
  mask=exterior(raw)
  result=main(s^mask)
  save(result,target)
  count=8 if name[0]=='C' else 12
  opposite=f'{name[0]}{count+1-int(name[1:]):02}'
  save(xform(result,-np.eye(3)),OUT/'final'/(opposite+'.npz'))
  changes.append(dict(name=name,volume_mm3=result.volume(),triangles=result.num_tri(),removed_outer_mm3=s.volume()-result.volume()))
  print(changes[-1],time.time()-t,flush=True)
 (OUT/'surface-finish.json').write_text(json.dumps(changes,indent=2))
