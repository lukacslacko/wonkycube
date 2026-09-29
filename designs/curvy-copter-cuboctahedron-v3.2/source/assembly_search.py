"""Search directions, then sampled coupled rotation/translation insertion paths."""
from design import *
from collections import deque
def run():
 cells=get('relieved');row=canonical('P');s=cells[row['name']];n=np.array(row['direction']);F=frame(n)
 fixed=union([v for k,v in cells.items() if k!=row['name'] and k[0] in 'KP'])
 ds=np.r_[np.arange(.25,6.01,.25),np.arange(7,60,2)]
 records=[]
 for slope in [0,.35,.7,1.,1.5,2.]:
  for theta in ([0] if slope==0 else np.arange(24)*np.pi/12):
   d=n+slope*(np.cos(theta)*F[:,0]+np.sin(theta)*F[:,1]);d/=np.linalg.norm(d)
   worst=max((s.translate(d*float(x))^fixed).volume() for x in ds)
   records.append((worst,d));
 print('BEST STRAIGHT',sorted([(v,d.tolist()) for v,d in records],key=lambda x:x[0])[:12],flush=True)
 if min(v for v,d in records)<.001:return
 # Try a twist about the petal's own radial line or an adjacent turn axis,
 # combined with withdrawal along the square-face normal.
 travel=np.eye(3)[int(np.argmax(abs(n)))];travel*=np.sign(travel@n)
 for axis in [n,AXES[8],AXES[canonical('P')['signature'][0]]]:
  seen={};came={(0,0):None};queue=deque([(0,0)]);end=None
  while queue:
   key=queue.popleft()
   if key[0]>=28:end=key;break
   for step in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
    kk=(key[0]+step[0],key[1]+step[1])
    if kk in seen or kk in came or not(-2<=kk[0]<=28 and -60<=kk[1]<=60):continue
    worst=0
    for t in [.5,1.]:
     z=(key[0]+step[0]*t)*.25;a=(key[1]+step[1]*t)*1.
     q=Rotation.from_rotvec(axis*np.radians(a)).as_matrix()
     worst=max(worst,(xform(s,q,travel*z)^fixed).volume())
    seen[kk]=worst
    if worst<.001:came[kk]=key;queue.append(kk)
  path=[]
  if end:
   while end is not None:path.append(end);end=came[end]
  print('PATH',axis.tolist(),'free',len(came),'extent',max(k[0] for k in came),'found',bool(path),flush=True)
  if path:
   (WORK/'petal-insertion-path.json').write_text(json.dumps(dict(axis=axis.tolist(),travel=travel.tolist(),steps=list(reversed(path)),translation_step=.25,angle_step_degrees=1),indent=2));return
if __name__=='__main__':run()
