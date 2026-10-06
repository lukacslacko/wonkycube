from inlays import *
from checks import motion,assembly
from hardware import core

def validate():
 records=json.loads((CACHE/'inlays.json').read_text())['records'];checks=[];cells={}
 for f in ORBITS:
  printed=load(CACHE/f'printed-{f}.npz');bare=load(CACHE/f'bare-{f}.npz');foam=[]
  if f in ['T','S']:printed=printed+load(CACHE/f'printed-{f}C.npz')
  for rec in records:
   if rec['family']!=f:continue
   s=fitted(rec);normal=np.array(rec['frame'])[:,2]
   # Check the higher, flush position with a 0.1 mm glue allowance occupied.
   flush=s.translate(normal*.1)
   overlap=(flush^printed).volume();excess=flush-bare;outside=excess.volume()
   # The 0.005 mm mesh simplification can perturb a nominal flat face.
   # Permit only that thin external skin; never leakage through a side wall.
   skin_depth=0. if outside<1e-8 else float(FACE_HEIGHT-np.min(mesh(excess).vertices@normal))
   assert overlap<.01 and skin_depth<.006,(rec['id'],overlap,outside,skin_depth)
   checks.append(dict(id=rec['id'],foam_to_printed_plastic_overlap_mm3=overlap,foam_outside_unrecessed_body_mm3=outside,external_mesh_skin_depth_mm=skin_depth))
   foam.append(flush)
  cells.update(replicate(union([printed]+foam),f))
 c=load(CACHE/'printed-core.npz')
 result=dict(foam_thickness_mm=THICKNESS,glue_allowance_mm=.1,checks=checks,turns=motion(cells,c,step=3),assembly=assembly(cells,c),scope='Flush, compressed foam envelopes. Actual foam compliance, thickness and adhesive are not simulated.')
 (DEST/'reports/installed-inlays.json').write_text(json.dumps(result,indent=2)+'\n')
 print('INSTALLED INLAYS PASS',flush=True)
if __name__=='__main__':validate()
