"""Finite translation/tilt configuration-space searches, anchored supports only."""
from retention_v2 import *
from collections import deque

def run():
 cells,core_part=load_parts();out=[]
 for f in ['P','K']:
  row=canonical(f);s=retaining_foot(cells[row['name']]);n=np.array(row['direction']);F=frame(n)
  support='C' if f=='P' else 'P';lift=.15 if f=='P' else .8
  fixed=union([v.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*lift) for k,v in cells.items() if k[0]==support]+[core_part])
  for tangent in [F[:,0],F[:,1]]:
   for pivot_depth in [24.,32.]:
    pivot=n*pivot_depth;free={(0,0)};seen={};q=deque([(0,0)]);escaped=False
    while q:
     key=q.popleft()
     if key[0]>=30:escaped=True;break
     for dz,dt in [(1,0),(-1,0),(0,1),(0,-1)]:
      k=(key[0]+dz,key[1]+dt)
      if k in seen or k in free or not(-2<=k[0]<=30 and -10<=k[1]<=10):continue
      rot=Rotation.from_rotvec(tangent*np.radians(k[1]*2)).as_matrix();moved=xform(s,rot,pivot-rot@pivot+n*(k[0]*.25));v=max(0.,(moved^fixed).volume());seen[k]=v
      if v<.002:free.add(k);q.append(k)
    rec=dict(family=f,support_family=support,support_lift_mm=lift,pivot_radius_mm=pivot_depth,rotation_axis=tangent.tolist(),radial_step_mm=.25,angular_step_degrees=2,radial_range_mm=[-.5,7.5],angle_range_degrees=[-20,20],visited_configurations=len(seen)+1,reachable_configurations=len(free),maximum_reachable_radial_offset_mm=max(k[0] for k in free)*.25,maximum_reachable_tilt_degrees=max(abs(k[1]) for k in free)*2,escape_found=escaped)
    print('ROCKING',rec,flush=True);out.append(rec)
 (DEST/'reports/rocking.json').write_text(json.dumps(dict(checks=out,scope='Eight restricted configuration-space searches. No arbitrary tangential translations, no elastic deformation, and no exhaustive escape proof.'),indent=2)+'\n')
 assert not any(r['escape_found'] for r in out)
if __name__=='__main__':run()
