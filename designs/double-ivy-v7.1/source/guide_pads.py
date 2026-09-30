"""Non-retaining core bearing webs for E/W, below their ordered flanges."""
from design import *
GUIDE_RADIUS=5.0
GUIDE_INNER_R=19.4

def cone(angle,offset):
 a=np.radians(angle);p=mf.CrossSection([[[0,0],[120*np.sin(a),120*np.cos(a)],[0,150]]])
 p=p.offset(offset,join_type=mf.JoinType.Round,circular_segments=24)
 return p.revolve(SEG)

def make(f):
 row=canonical(f);n=np.array(row['direction']);height=BASE_RADII[f]+1.
 s=xform(mf.Manifold.cylinder(height,GUIDE_RADIUS,GUIDE_RADIUS,SEG),frame(n))-mf.Manifold.sphere(GUIDE_INNER_R,SEG)
 # Constant restrictive cones make these simple stems, not a second set of
 # stepped retaining lips. The exact common cuts are an additional guard.
 for i,v in enumerate(row['signature']):
  s=s-xform(cone(BETA,TRACK_GAP-BODY_GAP/2),frame(AXES[i])) if v==0 else s^xform(cone(78.,-BODY_GAP/2),frame(AXES[i]))
  s=s^xform(cone(ALPHA,-BODY_GAP/2),frame(AXES[i])) if v==2 else s-xform(cone(ALPHA,TRACK_GAP-BODY_GAP/2),frame(AXES[i]))
  s=s-xform(cut(0,TRACK_GAP-BODY_GAP/2,.25),frame(AXES[i])) if v==0 else s^xform(cut(0,-BODY_GAP/2,-.35),frame(AXES[i]))
  s=s^xform(cut(1,-BODY_GAP/2,-.35),frame(AXES[i])) if v==2 else s-xform(cut(1,TRACK_GAP-BODY_GAP/2,.25),frame(AXES[i]))
 ball=mf.Manifold.sphere(.25,16);s=(s.minkowski_difference(ball).minkowski_sum(ball))^s
 return main(s,.01).as_original().simplify(.003)

def run():
 pads={f:make(f) for f in 'WE'};records={}
 for f,s in pads.items():save(s,CACHE/f'guide-{f}.npz');print('PAD',f,s.volume(),s.num_tri(),flush=True)
 for row in ROWS:
  name=row['name'];body=load(CACHE/'final'/(name+'.npz'))
  if row['family'] in pads:
   pad=xform(pads[row['family']],mapping(canonical(row['family'])['signature'],row['signature']))
   attachment=(pad^body).volume();assert attachment>3,(name,'attachment',attachment)
   body=main(body+pad,.01).as_original().simplify(.003);records[name]=dict(attachment_volume_mm3=attachment,pad_volume_mm3=pad.volume())
  save(body,CACHE/'guided'/(name+'.npz'))
 (CACHE/'guide-pads.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':run()
