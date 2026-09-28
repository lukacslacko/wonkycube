from design import *
from ridge_rounding import rounded_cells
def finish():
 cells=get('relieved');smooth={};logs=[]
 for f in ORBITS:
  row=canonical(f);s=cells[row['name']].as_original().simplify(.004)
  if f=='P':s=main(s-stem_sweep(),.01)
  r=.55 if f=='P' else .45;ball=mf.Manifold.sphere(r,20);t=time.time()
  if (CACHE/f'soft-{f}.npz').exists():rounded=load(CACHE/f'soft-{f}.npz')
  else:
   pieces=sorted((s.minkowski_difference(ball).minkowski_sum(ball)^s).decompose(),key=lambda c:c.volume(),reverse=True)
   scraps=[c for c in pieces[1:] if c.volume()>1e-8]
   assert sum(c.volume() for c in scraps)<3 and all(c.volume()<1 for c in scraps),('detached material',f,[c.volume() for c in scraps])
   rounded=pieces[0]
   (CACHE/(f+'-morphology-trim.json')).write_text(json.dumps([dict(volume_mm3=c.volume(),bounds_mm=mesh(c).bounds.tolist()) for c in scraps],indent=2)+'\n')
  print('SOFTEN',f,s.volume()-rounded.volume(),round(time.time()-t,1),flush=True)
  smooth.update(replicate(rounded,f));save(rounded,CACHE/f'soft-{f}.npz');logs.append(dict(family=f,rounding_mm=r,removed_volume_mm3=s.volume()-rounded.volume()))
 ridged=rounded_cells(smooth)
 for f in ORBITS:
  row=canonical(f);s=ridged[row['name']]
  if f!='P':s=axle(s,np.array(row['direction']),f)
  save(s.as_original().simplify(.005),CACHE/f'final-{f}.npz')
 (CACHE/'rounding.json').write_text(json.dumps(logs,indent=2)+'\n')
if __name__=='__main__':finish()
