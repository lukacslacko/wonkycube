"""Verify R3 transverse arcs and distinct edges on reloaded print files."""
from redi_design import *
from optimize_rotation import samples,flip
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
entries={r['name']:r for r in json.loads((DEST/'manifest.json').read_text())['parts']}
def printed(name):
 r=entries[name];m=trimesh.load(DEST/r['file'],force='mesh');t=np.array(r['mechanism_to_print']);m.vertices=(m.vertices-t[:,3])@t[:,:3]
 return m
def front(polys,z):
 ys=[]
 for p in polys:
  a=p;b=np.roll(p,-1,axis=0);dz=b[:,1]-a[:,1]
  ok=(abs(dz)>1e-10)&(np.minimum(a[:,1],b[:,1])-1e-8<=z)&(np.maximum(a[:,1],b[:,1])+1e-8>=z)
  ys.extend((a[ok,0]+(z-a[ok,1])*(b[ok,0]-a[ok,0])/dz[ok]).tolist())
 if not ys:raise ValueError('missing arc section')
 return min(ys)
t=time.time();sections=json.loads((OUT/'ridge-sections.json').read_text())
xs=np.array([r['x_mm'] for r in sections]);cys=np.array([r['circle_center_y_mm'] for r in sections]);angles=np.array([r['half_arc_angle_rad'] for r in sections])
assert all(r['radius_mm']==ROUND_R for r in sections), 'The cutter must not taper its radius.'
F=np.array([[0,1,0],[0,0,1],[1,0,0]]);swap=np.array([[0,1,0],[1,0,0],[0,0,-1]])
stations=np.r_[np.arange(INNER_R+.3,34*SCALE+.001,.125),35.5*SCALE,37.5*SCALE]
report=[];fail=[]
for row in ROWS:
 name=row['name']
 if name[0]!='E':continue
 q=mapping(EDGES[-1],row['signature']);m=printed(name);m.vertices=m.vertices@q;s=from_mesh(m)
 for label,transform in [('+X',np.eye(3)),('+Y',swap)]:
  local=xform(s,F@transform)
  for x in stations:
   cy=float(np.interp(x,xs,cys));a=float(np.interp(x,xs,angles));zs=ROUND_R*np.sin(np.linspace(-.8*a,.8*a,41));polys=local.slice(float(x)).to_polygons()
   ys=np.array([front(polys,z) for z in zs]);error=abs(np.hypot(ys-cy,zs)-ROUND_R)
   A=np.column_stack((ys,zs,np.ones_like(zs)));coeff=np.linalg.lstsq(A,-(ys*ys+zs*zs),rcond=None)[0]
   radius=float(np.sqrt(max(0,(coeff[0]**2+coeff[1]**2)/4-coeff[2])))
   # Near a track inflection the exposed circular arc shrinks almost to a
   # point. An unconstrained radius fit there is ill-conditioned: micron
   # mesh noise changes the fitted radius hugely. Always check distance to
   # the known R3 circle, and fit curvature only on adequately broad arcs.
   fit_resolved=a>=.5
   good=(not fit_resolved or abs(radius-ROUND_R)<.08) and error.max()<.04
   data=dict(name=name,ridge=label,x_mm=float(x),half_arc_angle_rad=a,radius_fit_resolved=bool(fit_resolved),fitted_radius_mm=radius,max_circle_error_mm=float(error.max()),passed=bool(good));report.append(data)
   if not good:fail.append(data)
 print(name,'ridge sections checked',flush=True)
result=dict(nominal_radius_mm=ROUND_R,known_circle_distance_limit_mm=.04,radius_fit_minimum_half_angle_rad=.5,sections=report,failures=fail,passed=not fail,seconds=time.time()-t)
(DEST/'reports/ridge-radii.json').write_text(json.dumps(result,indent=2))
assert not fail,fail[:8]
u=samples(15);frames=np.array(json.loads((HERE/'chosen_rotation.json').read_text())['edge_frames']);profiles=[]
for i,q in enumerate(frames):
 m=printed(f'E{i+1:02}');directions=np.concatenate((u,u@flip.T))@q.T
 locations,index,_=m.ray.intersects_location(np.zeros_like(directions),directions,multiple_hits=True)
 h=np.full(len(directions),np.nan)
 for ray in np.unique(index):h[ray]=np.linalg.norm(locations[index==ray],axis=1).max()
 profiles.append(h.reshape(2,-1));print('shape',i+1,'missed',np.isnan(h).sum(),flush=True)
h=np.array(profiles);valid=np.isfinite(h).all(axis=(0,1));assert valid.sum()>300;h=h[:,:,valid];pairs=[]
for i,j in itertools.combinations(range(12),2):
 rms=np.sqrt(np.mean((h[i,0]-h[j])**2,axis=1));pairs.append(dict(edges=[f'E{i+1:02}',f'E{j+1:02}'],minimum_rms_mm=float(rms.min())))
result=dict(common_directions=int(valid.sum()),proper_mounting_orientations=2,minimum_pair_rms_mm=min(r['minimum_rms_mm'] for r in pairs),pairs=pairs,passed=all(r['minimum_rms_mm']>.1 for r in pairs),scope='Sampled exterior difference in both proper lens orientations; mirrored shapes remain distinct. No new rotation optimization or arbitrary forced-fit claim.')
(DEST/'reports/edge-shapes.json').write_text(json.dumps(result,indent=2));assert result['passed'];print('PASS shapes',result['minimum_pair_rms_mm'],flush=True)
