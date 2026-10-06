from hardware import *
from shapely.geometry import LineString,Point
def inspect(s,f):
 n=np.array(canonical(f)['direction']);F=frame(n);local=mesh(s);local.vertices=local.vertices@F
 tri=local.triangles;rho=np.linalg.norm(tri[:,:,:2],axis=2);seat=SEATS[f]
 bore=np.max(abs(rho-1.8),axis=1)<.02
 well=(np.max(abs(rho-WELL_R),axis=1)<.02)&(np.min(tri[:,:,2],axis=1)>seat-.02)
 flat=np.max(abs(tri[:,:,2]-seat),axis=1)<.02
 external=local.submesh([~(bore|well|flat)],append=True)
 # Step 0.03 mm into material to avoid an ambiguous ray along the faceted bore.
 # Report this slightly smaller conservative thickness without adding it back.
 t=np.arange(720)*2*np.pi/720;points=np.c_[(WELL_R+.03)*np.cos(t),(WELL_R+.03)*np.sin(t),np.full(720,seat-.02)]
 nearest,distance,_=trimesh.proximity.closest_point(external,points);minimum=float(distance.min())
 # Ensure the measured rim-to-exterior segment is a real solid web.
 i=int(np.argmin(distance));samples=points[i]+np.linspace(.03,.97,21)[:,None]*(nearest[i]-points[i])
 assert local.contains(samples).all(),('web crosses a void',f)
 out=dict(family=f,washer_root_minimum_web_mm=minimum,washer_seat_mm=seat,screw_tip_mm=seat+WASHER_H-20,
  screw_beyond_nut_mm=NUT_ROOF-4-(seat+WASHER_H-20),head_outer_coordinate_mm=seat+WASHER_H+3,
  outside_face_coordinate_mm=VERTEX_RADIUS*np.sqrt(3)/2 if f=='T' else VERTEX_RADIUS,foot_annular_wall_mm=FOOT_R-1.8)
 print('STRUCTURE',out,flush=True)
 assert minimum>1.5,out
 # Check the full central stem as well as the washer ledge. An apparently
 # sound washer root can conceal a thin bore wall farther toward the core.
 local_solid=xform(s,F.T);webs=[]
 for z in np.arange(FOOT_PLANE+.02,seat-.02,.1):
  boundaries=[]
  for p in local_solid.slice(z).to_polygons():
   if np.max(abs(np.linalg.norm(p,axis=1)-1.8))<.005:continue
   boundaries.append(LineString(np.vstack([p,p[0]])).distance(Point(0,0))-1.8)
  webs.append([min(boundaries),float(z)])
 minimum_stem=min(webs)
 assert minimum_stem[0]>1.25,('thin central stem',f,minimum_stem)
 out['bore_wall_minimum_mm']=minimum_stem[0];out['bore_wall_minimum_height_mm']=minimum_stem[1]
 assert out['screw_beyond_nut_mm']>=1 and out['head_outer_coordinate_mm']<out['outside_face_coordinate_mm']
 return out
if __name__=='__main__':
 import sys
 stage=sys.argv[1] if len(sys.argv)>1 else 'printed'
 results=[inspect(load(CACHE/f'{stage}-{f}.npz'),f) for f in ['T','S']]
 (CACHE/'structure.json').write_text(json.dumps(results,indent=2)+'\n')
