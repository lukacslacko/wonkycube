"""Round center flange outlines along radial lines, preserving spherical lands."""
from design import *
from ridge_rounding import cutter

def cone(angle,offset):
 a=np.radians(angle);p=mf.CrossSection([[[0,0],[130*np.sin(a),130*np.cos(a)],[0,150]]])
 p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=32)
 if offset<0:p=p+mf.CrossSection.square([1,120],False).translate([0,1])
 return p.revolve(SEG)

def soften_flange(s,f):
 own=canonical(f)['signature'][0];a=AXES[own];records=[];tools=[]
 ca=np.cos(np.radians(NECK_ANGLES[f]));otherfamily='S' if f=='T' else 'T';cb=np.cos(np.radians(NECK_ANGLES[otherfamily]))
 for other,b in enumerate(AXES):
  if (other<8)==(own<8) or a@b<.5:continue
  A=np.array([a,b]);d0=A.T@np.linalg.solve(A@A.T,[ca,cb]);k=np.cross(a,b);k/=np.linalg.norm(k)
  assert d0@d0<1
  for sign in [-1,1]:
   d=d0+sign*np.sqrt(1-d0@d0)*k
   inward=(a-ca*d)/np.linalg.norm(a-ca*d)-(b-cb*d)/np.linalg.norm(b-cb*d);inward/=np.linalg.norm(inward)
   side=np.cross(d,inward);F=np.array([inward,side,d])
   ref=mf.Manifold.sphere(90,SEG)^xform(cone(NECK_ANGLES[f],-BODY_GAP/2),frame(a))
   ref=ref-xform(cone(NECK_ANGLES[otherfamily],BODY_GAP/2+TRACK_EXTRA),frame(b))
   tool,data=cutter(ref,F,FLANGE_OUTLINE_RADIUS,False)
   assert tool is not None
   tools.append(tool.as_original().simplify(.002))
   records.append(dict(axes=[int(own),int(other)],radial_direction=d.tolist(),frame=F.tolist(),sections=data))
   print('FLANGE OUTLINE',f,other,sign,len(data),flush=True)
 rounded=main(subtract(s,tools),.01).as_original().simplify(.002)
 report=dict(radius_mm=FLANGE_OUTLINE_RADIUS,corner_count=len(records),removed_volume_mm3=float(s.volume()-rounded.volume()),method='Transverse circular fillets swept along radial flange-end corners; broad concentric spherical bearing lands remain.',corners=records)
 (CACHE/f'flange-rounding-{f}.json').write_text(json.dumps(report,indent=2)+'\n')
 print('FLANGE OUTLINE REMOVED',f,report['removed_volume_mm3'],flush=True)
 return rounded
