import hashlib
"""Verify delivered fillet arcs through inner tracks and outer radial ridges."""
from conical_design import *
import sys
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
ENTRIES={r['name']:r for r in json.loads((DEST/'manifest.json').read_text())['parts']}
def printed(name):
 r=ENTRIES[name];m=trimesh.load(DEST/r['file'],force='mesh');t=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3];return m

def front(polys,z):
 values=[]
 for p in polys:
  a=p;b=np.roll(p,-1,axis=0);dz=b[:,1]-a[:,1]
  use=(abs(dz)>1e-10)&(np.minimum(a[:,1],b[:,1])-1e-7<=z)&(np.maximum(a[:,1],b[:,1])+1e-7>=z)
  values.extend((a[use,0]+(z-a[use,1])*(b[use,0]-a[use,0])/dz[use]).tolist())
 return min(values) if values else np.nan

sections=json.loads((CACHE/'ridges-3/sections.json').read_text());report=[];fail=[];occluded=0
for row in ROWS:
 name=row['name'];base=next(r for r in ROWS if r['family']==row['family']);q=mapping(base['signature'],row['signature'])
 delivered=from_mesh(printed(name));cad=load(CACHE/'final'/(name+'.npz'))
 for ridge,info in enumerate(sections[row['family']]):
  assert all(r['radius_mm']==3. for r in info['sections'])
  F=np.array(info['frame'])@q.T;local=xform(delivered,F);original=xform(cad,F)
  data=info['sections'];xs=np.array([r['station_mm'] for r in data]);centers=np.array([r['center'] for r in data]);angles=np.array([r['angles'] for r in data])
  for x in np.r_[np.arange(17.25,32.01,.25),34.,36.,38.,40.,42.,44.]:
   cy=np.interp(x,xs,centers[:,0]);cz=np.interp(x,xs,centers[:,1]);lo=np.interp(x,xs,angles[:,0]);hi=np.interp(x,xs,angles[:,1])
   if hi-lo<.03:occluded+=1;continue
   # Sample the middle 80% of the ARC, including asymmetric arcs. Scaling
   # each endpoint toward angle zero can instead sample within 0.0003 mm
   # of a track/fillet boundary. Tiny normal export changes there give an
   # arbitrarily large transverse section change at a grazing intersection.
   a=lo+(hi-lo)*np.linspace(.1,.9,25);zs=cz+3*np.sin(a);expected=cy-3*np.cos(a)
   p=local.slice(float(x)).to_polygons();basep=original.slice(float(x)).to_polygons()
   old=np.array([front(basep,z) for z in zs]);new=np.array([front(p,z) for z in zs]);available=np.isfinite(old)&(abs(old-expected)<.025)
   # Geometry may terminate at the cube, core cavity or another fillet. Choose
   # exposed arcs using pre-export CAD, never by the print mesh under test.
   if np.count_nonzero(available)<8:occluded+=1;continue
   err=abs(np.hypot(new[available]-cy,zs[available]-cz)-3)
   export_error=abs(new[available]-old[available]);good=bool(np.isfinite(err).all() and err.max()<.045 and export_error.max()<.025)
   datum=dict(name=name,ridge=ridge,station_mm=float(x),exposed_samples=int(available.sum()),max_circle_error_mm=float(np.nanmax(err)),max_export_profile_error_mm=float(np.nanmax(export_error)),passed=good)
   report.append(datum)
   if not good:fail.append(datum)
 print('RADII',name,'checked',sum(r['name']==name for r in report),flush=True)
result=dict(manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),nominal_radius_mm=3.,sections=report,occluded_or_terminated_sections=occluded,failures=fail,passed=not fail,scope='Constant R3 cutter sections through inner tracks and outer ridges; exposed-arc eligibility determined from pre-export CAD. Intersections with other fillets or exterior surfaces can terminate an arc.')
(DEST/'reports/ridge-radii.json').write_text(json.dumps(result,indent=2));assert not fail,fail[:6]
assert len(report)>500
