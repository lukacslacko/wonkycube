"""Family-ordered F -> E -> W -> C assembly, keeping every captured foot."""
from design import *
def run():
 parts={f:load(CACHE/f'raw-{f}.npz') for f in 'CWEF'};report=[]
 for holder,receivers in [('C','WEF'),('W','EF'),('E','F')]:
  row=canonical(holder);n=np.array(row['direction']);body=parts[holder]
  if holder=='C':body=axle(body,n)
  tool=downward_sweep(body^mf.Manifold.sphere(33.2,SEG),-n,.03).as_original().simplify(.005)
  tools=[xform(tool,mapping(row['signature'],r['signature'])) for r in ROWS if r['family']==holder]
  for f in receivers:
   old=parts[f];s=main(subtract(old,tools),.05);loss=(old-s)^mf.Manifold.sphere(FOOT_LIMITS[f],SEG)
   assert loss.volume()<.03,(holder,f,'captured foot loss',loss.volume())
   rec=dict(inserted_family=holder,receiving_family=f,removed_volume_mm3=old.volume()-s.volume(),captured_foot_limit_mm=FOOT_LIMITS[f],captured_foot_removed_mm3=loss.volume())
   print('RECEIVER',rec,flush=True);report.append(rec);parts[f]=s.as_original().simplify(.003)
 for f,s in parts.items():save(s,CACHE/f'prepared-{f}.npz')
 (CACHE/'assembly-clearance.json').write_text(json.dumps(report,indent=2)+'\n')
 for name,s in clipped(expand(parts)).items():save(s,CACHE/'prepared'/(name+'.npz'))
if __name__=='__main__':run()
