from design import *
from ridge_fit import cutter
from ridges import ridges

def canonical_finish():
 records={}
 for f in 'CWEF':
  row=canonical(f);s=load(CACHE/f'prepared-{f}.npz').as_original().simplify(.003)
  soft_path=CACHE/f'soft-{f}.npz'
  if soft_path.exists():s=load(soft_path)
  else:
   ball=mf.Manifold.sphere(.30,20);rounded=(s.minkowski_difference(ball).minkowski_sum(ball))^s
   s=main(rounded,.2).as_original().simplify(.004);save(s,soft_path)
  outpath=CACHE/f'rounded-{f}.npz';recordpath=CACHE/f'ridges-{f}.json'
  if outpath.exists() and recordpath.exists():records[f]=json.loads(recordpath.read_text());continue
  tools=[];rec=[]
  for a,b,F in ridges(row):
   tool,data=cutter(s,F,2.,f in ['C','F'])
   if tool is None:continue
   tools.append(tool.as_original().simplify(.002));rec.append(dict(boundaries=[a,b],frame=F.tolist(),sections=data))
   print('RIDGE',f,a,b,len(data),flush=True)
  rounded=subtract(s,tools);chunks=sorted(rounded.decompose(),key=lambda c:c.volume(),reverse=True);scraps=sum(abs(c.volume()) for c in chunks[1:]);assert scraps<3,(f,'detached material',scraps)
  rounded=chunks[0].as_original().simplify(.003);save(rounded,outpath);recordpath.write_text(json.dumps(rec,indent=2)+'\n');records[f]=rec
  print('ROUNDED',f,'removed',s.volume()-rounded.volume(),'scraps',scraps,flush=True)
 (CACHE/'ridge-sections.json').write_text(json.dumps(records,indent=2)+'\n')

def outer_mask(s):
 # Use the unrelieved exterior reference for this mask. Receiving grooves
 # already have internal rounding; including their hidden channels here
 # needlessly complicates a whole-solid Minkowski operation.
 # All retaining surfaces end below R31.6; avoid altering that region when
 # softening only the exposed edges of the 72 mm rotated cube.
 full=(s+mf.Manifold.sphere(33.1,48)).as_original().simplify(.006)
 ball=mf.Manifold.sphere(.6,16);result=(full.minkowski_difference(ball).minkowski_sum(ball))^full
 return main(result,1.)

def pieces():
 rounded=expand({f:load(CACHE/f'rounded-{f}.npz') for f in 'CWEF'});skin_reference=expand({f:load(CACHE/f'raw-{f}.npz') for f in 'CWEF'})
 for row in ROWS:
  name=row['name'];path=CACHE/'final'/(name+'.npz')
  if path.exists():continue
  print('PART',name,flush=True);body=skin_reference[name]^outer();mask=outer_mask(body)
  s=(rounded[name]^outer())^mask;s=main(s,.1)
  if row['family']=='C':s=axle(s,np.array(row['direction']))
  s=s.as_original().simplify(.004);save(s,path);print('PART DONE',name,s.num_tri(),s.volume(),flush=True)
if __name__=='__main__':
 canonical_finish();pieces()
