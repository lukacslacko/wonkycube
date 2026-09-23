"""Round exterior rims without changing washer lands or internal rail geometry."""
from redi_design import *

def exterior(s,radius=OUTER_ROUND,simplify_seed=False):
 s=s.as_original().simplify(.005)
 kernel=mf.Manifold.sphere(radius,16)
 protected=s^mf.Manifold.sphere(INNER_LIMIT,128)
 seed=s.minkowski_difference(kernel)+protected
 if simplify_seed:seed=seed.as_original().simplify(.005)
 return main(seed.minkowski_sum(kernel)^s)

if __name__=='__main__':
 t=time.time();cube=xform(mf.Manifold.cube([SIDE]*3,True),R)
 canonical={k:load(OUT/f'canonical-{k}.npz') for k in ['C','E']}
 ref={'C':[7],'E':EDGES[-1]};changes=[]
 for row in ROWS:
  name=row['name'];target=OUT/'final'/(name+'.npz')
  if len(sys.argv)>1 and name not in sys.argv[1:]:continue
  if target.exists():continue
  q=mapping(ref[name[0]],row['signature']);s=xform(canonical[name[0]],q)^cube
  raw=load(OUT/'raw'/(name+'.npz'))^cube
  if name[0]=='C':raw=finish_hardware(raw,np.array(row['direction']))
  # Petal profiles have costly offset topology. Simplify only the rounding
  # tool seed by 5 microns, then intersect with the unmodified part.
  mask=exterior(raw,simplify_seed=name[0]=='E');result=main(s^mask)
  save(result,target)
  count=8 if name[0]=='C' else 12;opposite=f'{name[0]}{count+1-int(name[1:]):02}'
  save(xform(result,-np.eye(3)),OUT/'final'/(opposite+'.npz'))
  record=dict(name=name,triangles=result.num_tri(),volume_mm3=result.volume(),outer_rounding_removed_mm3=s.volume()-result.volume())
  changes.append(record);print('finish',record,'seconds',time.time()-t,flush=True)
 if (len(sys.argv)==1 or 'core' in sys.argv[1:]) and not (OUT/'final/core.npz').exists():
  # Round only exposed tips of the arms. Preserve every root and bearing.
  s=load(OUT/'core.npz').as_original().simplify(.005);kernel=mf.Manifold.sphere(.45,16)
  protected=s^mf.Manifold.sphere(34,128)
  result=main(((s.minkowski_difference(kernel)+protected).minkowski_sum(kernel))^s)
  save(result,OUT/'final/core.npz');print('core finished',time.time()-t,flush=True)
 (OUT/('surface-finish'+('-'+sys.argv[1] if len(sys.argv)>1 else '')+'.json')).write_text(json.dumps(changes,indent=2))
