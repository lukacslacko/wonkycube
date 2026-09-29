"""Round the four outline corners of the two center flange ends radially.

A constant-radius transverse circle is swept along each actual flange-corner
radial direction. Unlike a ball opening this does not round over the spherical
bearing shoulders, or reduce the broad contact faces of the collar.
"""
from design import *
from ridge_rounding import ridges,cutter

def cone(angle,offset):
 a=np.radians(angle);p=mf.CrossSection([[[0,0],[130*np.sin(a),130*np.cos(a)],[0,150]]])
 p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=32)
 if offset<0:p=p+mf.CrossSection.square([1,120],False).translate([0,1])
 return p.revolve(SEG)

def soften_flange(s):
 own=canonical('C')['signature'][0];records=[];tools=[]
 for i,j,F0 in ridges(canonical('C')):
  if own not in (i,j):continue
  other=j if i==own else i
  a,b=AXES[own],AXES[other];ca=np.cos(np.radians(NECK_ANGLE));cb=np.cos(np.radians(NECK_ANGLE))
  A=np.array([a,b]);d0=A.T@np.linalg.solve(A@A.T,[ca,cb]);k=np.cross(a,b);k/=np.linalg.norm(k)
  candidates=[d0+sgn*np.sqrt(1-d0@d0)*k for sgn in [-1,1]]
  d=max(candidates,key=lambda x:x@F0[2]);assert d@F0[2]>.95
  inward=(a-ca*d)/np.linalg.norm(a-ca*d)-(b-cb*d)/np.linalg.norm(b-cb*d);inward/=np.linalg.norm(inward)
  side=np.cross(d,inward);F=np.array([inward,side,d])
  # Reference the two genuine sides of this flange outline corner, without
  # spherical shoulders or exterior caps entering the transverse circle fit.
  ref=mf.Manifold.sphere(90,SEG)^xform(cone(NECK_ANGLE,-BODY_GAP/2),frame(a))
  ref=ref-xform(cone(NECK_ANGLE,BODY_GAP/2+TRACK_EXTRA),frame(b))
  tool,data=cutter(ref,F,CENTER_FLANGE_END_ROUNDING,False)
  assert tool is not None
  tools.append(tool.as_original().simplify(.002))
  records.append(dict(axes=[int(own),int(other)],radial_direction=d.tolist(),frame=F.tolist(),sections=data))
  print('FLANGE OUTLINE',own,other,len(data),flush=True)
 rounded=main(subtract(s,tools),.01).as_original().simplify(.002)
 removed=s-rounded;save(removed,CACHE/'center-flange-removed.npz')
 report=dict(radius_mm=CENTER_FLANGE_END_ROUNDING,corner_count=len(records),removed_volume_mm3=float(removed.volume()),method='Constant-radius transverse circular fillets along the four radial corners of the two flange ends; original spherical bearing rims and exterior shell preserved. No additional ball opening.',corners=records)
 (CACHE/'flange-rounding.json').write_text(json.dumps(report,indent=2)+'\n')
 print('FLANGE OUTLINE REMOVED',removed.volume(),flush=True)
 return rounded
