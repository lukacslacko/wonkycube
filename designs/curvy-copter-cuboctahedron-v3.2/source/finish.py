from design import *
from ridge_rounding import rounded_cells
from tip_trim import trim_corner
from flange_rounding import soften_flange
def finish():
 cells=get('relieved');smooth={};logs=[]
 for f in ORBITS:
  row=canonical(f);s=cells[row['name']].as_original().simplify(.004)
  # Subtractive opening rounds exposed rims and inner protrusions. The
  # flat axle bearing and washer seat are installed after these cuts.
  r=.45 if f!='C' else .35;ball=mf.Manifold.sphere(r,20)
  t=time.time()
  if (CACHE/f'soft-{f}.npz').exists():rounded=load(CACHE/f'soft-{f}.npz')
  else:
   pieces=sorted((s.minkowski_difference(ball).minkowski_sum(ball)^s).decompose(),key=lambda c:c.volume(),reverse=True)
   scraps=[c for c in pieces[1:] if c.volume()>1e-8]
   assert sum(c.volume() for c in scraps)<3 and all(c.volume()<1 for c in scraps),('large detached material',f,[c.volume() for c in scraps])
   (CACHE/(f+'-morphology-trim.json')).write_text(json.dumps([dict(volume_mm3=c.volume(),bounds_mm=mesh(c).bounds.tolist()) for c in scraps],indent=2)+'\n')
   rounded=pieces[0]
  print('SOFTEN',f,s.volume()-rounded.volume(),round(time.time()-t,1),flush=True)
  smooth.update(replicate(rounded,f));save(rounded,CACHE/f'soft-{f}.npz')
  logs.append(dict(family=f,edge_rounding_mm=r,removed_mm3=s.volume()-rounded.volume()))
 ridged=rounded_cells(smooth)
 for f in ORBITS:
  row=canonical(f);s=ridged[row['name']]
  if f=='C':s=axle(soften_flange(s),np.array(row['direction']))
  s=s.as_original().simplify(.005)
  if f=='K':
   # Preserve a 3.3 mm solid spine through the hidden waist. Added material
   # is a subset of the pre-fillet solid; visible edges retain their R2 cuts.
   n=np.array(row['direction'])
   protected=xform(mf.Manifold.cylinder(7,1.65,1.65,SEG).translate([0,0,28]),frame(n))
   s=main(s+(smooth[row['name']]^protected))
   (CACHE/'corner-neck.json').write_text(json.dumps(dict(protected_diameter_mm=3.3,axial_range_mm=[28,35],added_material='intersection of softened corner and cylinder; only hidden fillet loss restored'),indent=2)+'\n')
  if f=='K':s=trim_corner(s)
  save(s,CACHE/f'final-{f}.npz')
 (CACHE/'rounding.json').write_text(json.dumps(logs,indent=2)+'\n')
if __name__=='__main__':finish()
