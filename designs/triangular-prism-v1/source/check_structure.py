"""Geometric wall and hardware-envelope checks; not material strength analysis."""
from conical_design import *
import sys,hashlib
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());records=[]
for r in (r for r in ROWS if r['family']=='C'):
 rec=next(p for p in meta['parts'] if p['name']==r['name']);m=trimesh.load(DEST/rec['file'],force='mesh');t=np.array(rec['mechanism_to_print']);m.vertices=((m.vertices-t[:,3])@t[:,:3])@frame(r['direction']);s=from_mesh(m)
 # A continuous annulus around the screw through the whole load-bearing stalk.
 results=[]
 for radius in [2.6,2.7,2.8,2.9,3.0]:
  ann=(mf.Manifold.cylinder(SEAT-FOOT_PLANE-.1,radius,radius,120)-mf.Manifold.cylinder(SEAT-FOOT_PLANE-.1,1.82,1.82,120)).translate([0,0,FOOT_PLANE+.05])
  missing=(ann-s).volume();results.append([radius,float(missing)])
 assert results[0][1]<.01,(r['name'],'thin stalk',results)
 # The access-well rim to any nearby exterior, excluding the bores themselves.
 tri=m.triangles;rr=np.linalg.norm(tri[:,:,:2],axis=2)
 mask=(rr.min(axis=1)>4.85)&(tri[:,:,2].min(axis=1)>23)&(tri[:,:,2].max(axis=1)<SEAT+.15)
 root=m.submesh([np.flatnonzero(mask)],append=True,repair=False)
 angles=np.linspace(0,2*np.pi,720,endpoint=False);pts=np.c_[4.8*np.cos(angles),4.8*np.sin(angles),np.full(len(angles),SEAT)]
 near,dist,_=trimesh.proximity.closest_point(root,pts);j=int(np.argmin(dist));web=float(dist[j]);assert web>1.25,(r['name'],'well web',web)
 assert m.contains(np.linspace(pts[j],near[j],21)[1:-1]).all()
 b=np.array(r['direction'])@R;headgap=float(np.min(SIDE/2-(SEAT+4)*abs(b)-2.75*np.sqrt(1-b*b)))
 assert headgap>0.5
 records.append(dict(name=r['name'],stalk_test_radius_mm=results,minimum_sampled_well_root_web_mm=web,well_point=pts[j].tolist(),root_point=near[j].tolist(),minimum_head_to_cube_mm=headgap))
 print('STRUCTURE',records[-1],flush=True)
record=dict(passed=True,manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),centers=records,scope='Continuous screw-stalk annulus, sampled washer-well root web, nominal screw head clearance. No strength or fatigue rating.')
(DEST/'reports/structure.json').write_text(json.dumps(record,indent=2))
