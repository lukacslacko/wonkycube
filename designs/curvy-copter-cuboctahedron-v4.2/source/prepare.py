"""Start with v3.2 delivered mesh geometry and complete its missing fillet halves."""
from design import *
import hashlib
from rounding_repair import repair
def prepare():
 meta=json.loads((HERE/'fixed-baseline/manifest.json').read_text());checks=[];rounding=[]
 for rec in meta['parts']:
  if '/puzzle/' not in rec['file']:continue
  p=HERE/'fixed-baseline'/Path(rec['file']).name
  assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
  m=trimesh.load(p,force='mesh');T=np.array(rec['mechanism_to_print']);m.vertices=(m.vertices-T[:,3])@T[:,:3]
  s=from_mesh(m);f=rec['family'];save(s,CACHE/f'baseline-{f}.npz')
  if f in ['C','K']:
   s,recfix=repair(s,f);rounding.append(recfix)
  save(s,CACHE/f'mechanism-{f}.npz')
  if f=='C':
   # Only refill the driver well above the head. The whole central surface
   # is pocketed first, then separated into the base and a small keyed plug.
   n=np.array(canonical('C')['direction']);ball=mf.Manifold.sphere(.45,24)
   rounded=outer().minkowski_difference(ball).minkowski_sum(ball)^outer()
   fill=xform(mf.Manifold.cylinder(50,4.815,4.815,SEG).translate([0,0,35.9]),frame(n))^rounded
   s=main(s+fill)
  save(s,CACHE/f'bare-{f}.npz');checks.append(dict(family=f,sha256=rec['sha256']))
 (CACHE/'baseline.json').write_text(json.dumps(checks,indent=2)+'\n')
 (CACHE/'rounding-repair.json').write_text(json.dumps(rounding,indent=2)+'\n')
if __name__=='__main__':prepare()
