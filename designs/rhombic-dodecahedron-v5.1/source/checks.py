from hardware import *
def unit(v):return np.array(v)/np.linalg.norm(v)
def hit(s,fixed,v,distances):
 for d in distances:
  overlap=(s.translate(v*d)^fixed).volume()
  if overlap>.01:return dict(distance_mm=float(d),intersection_mm3=float(overlap))
 return None
def assembly(cells,c):
 # Preserve full shoulders: start with all centers unscrewed and a loose,
 # expanded shell. A coordinated contraction seats the interlocked pieces.
 # Petals move 0.95 mm per 1 mm of center travel. This is a constructive
 # multi-part path, not a claim that a final center inserts into fixed petals.
 ratio=.95;opening=12.;states=[];worst=[0.,0.,'','']
 for d in np.r_[np.arange(0,8.001,.1),np.arange(8.25,opening+.001,.25)]:
  state={r['name']:cells[r['name']].translate(np.array(r['direction'])*d*(ratio if r['family']=='P' else 1)) for r in ROWS}
  state['core']=c;bounds={k:np.array(v.bounding_box()).reshape(2,3) for k,v in state.items()}
  maximum=0.
  for f in ORBITS:
   name=canonical(f)['name'];lo,hi=bounds[name]
   for k,v in state.items():
    if k==name:continue
    l,h=bounds[k]
    if np.any(hi<=l) or np.any(h<=lo):continue
    vv=(state[name]^v).volume();maximum=max(maximum,vv)
    if vv>worst[1]:worst=[float(d),float(vv),name,k]
  assert maximum<.005,('coordinated shell closure',d,worst)
  states.append(dict(center_translation_mm=float(d),petal_translation_mm=float(ratio*d),maximum_collision_mm3=float(maximum)))
 print('ASSEMBLY closure',worst,flush=True)
 expanded={r['name']:cells[r['name']].translate(np.array(r['direction'])*opening*(ratio if r['family']=='P' else 1)) for r in ROWS}
 entries=[]
 for f in ORBITS:
  row=canonical(f);name=row['name'];n=np.array(row['direction']);s=expanded[name]
  fixed=union([v for k,v in expanded.items() if k!=name]+[c]);high=[0,0]
  for d in np.r_[np.arange(0,8.01,.25),np.arange(9,81,1)]:
   vol=(s.translate(n*d)^fixed).volume()
   if vol>high[1]:high=[float(d),float(vol)]
  print('ASSEMBLY expanded entry',f,high,flush=True);assert high[1]<.005,('entry into expanded shell',f,high)
  entries.append(dict(family=f,additional_outward_travel_mm=80,worst=high))
 return dict(passed=True,method='Radial placement into an expanded loose shell, followed by coordinated contraction; centers unscrewed until seated.',initial_center_translation_mm=opening,initial_petal_translation_mm=opening*ratio,contraction=states,entry=entries,scope='Finite constructive rigid path, exploiting cubic symmetry for repeated parts. Requires supporting several loose pieces together, for example with temporary tape; not single-piece insertion into a tightly fastened puzzle.')
def motion(cells,c,step=10,all_axes=False):
 hw=union([s for i in range(N_AXES) for s in hardware(i)]);result=[]
 for a in (range(N_AXES) if all_axes else [0,8]):
  n=AXES[a];end=120 if a<8 else 90
  moving=union([cells[r['name']] for r in ROWS if a in r['signature']])
  fixed=union([cells[r['name']] for r in ROWS if a not in r['signature']]+[c,hw]);worst=[0,0]
  for angle in np.linspace(0,end,int(np.ceil(end/step))+1):
   q=Rotation.from_rotvec(n*np.radians(angle)).as_matrix();vol=(xform(moving,q)^fixed).volume()
   if vol>worst[1]:worst=[float(angle),float(vol)]
  print('MOTION',a,worst,flush=True);result.append(dict(axis=a,angle_degrees=end,sample_step_degrees=step,worst=worst));assert worst[1]<.005
 return result
def capture(cells,c,angles=True):
 out=[];row=canonical('P');name=row['name'];dir0=np.array(row['direction'])
 for axis in [0,8]:
  end=120 if axis<8 else 90
  for angle in (np.linspace(0,end,5) if angles else [0]):
   q=Rotation.from_rotvec(AXES[axis]*np.radians(angle)).as_matrix()
   state={r['name']:xform(cells[r['name']],q) if axis in r['signature'] else cells[r['name']] for r in ROWS}
   n=q@dir0 if axis in row['signature'] else dir0;F=frame(n);s=state[name]
   for lift in [0,.1]:
    fixed=union([v.translate(np.array(next(r['direction'] for r in ROWS if r['name']==k))*lift) if k[0] in ['T','S'] else v for k,v in state.items() if k!=name]+[c])
    directions=[n]+[unit(n+slope*(np.cos(t)*F[:,0]+np.sin(t)*F[:,1])) for slope in [.35,.7] for t in np.arange(6)*np.pi/3]
    found=[hit(s,fixed,d,np.arange(.1,6.01,.1)) for d in directions]
    print('CAPTURE',axis,angle,lift,[None if x is None else x['distance_mm'] for x in found],flush=True)
    rec=dict(axis=axis,angle_degrees=float(angle),center_lift_mm=lift,contacts=found);out.append(rec);assert all(x is not None for x in found),('escape',rec)
 return out
if __name__=='__main__':
 import sys
 stage=sys.argv[1] if len(sys.argv)>1 else 'relieved';cells=get(stage)
 if stage not in ['final','printed']:
  for row in ROWS:
   if row['family']!='P':cells[row['name']]=axle(cells[row['name']],np.array(row['direction']),row['family'])
 c=core();save(c,CACHE/'core.npz');r={}
 r['assembly']=assembly(cells,c);r['motion']=motion(cells,c);r['capture']=capture(cells,c,angles=stage=='final')
 (CACHE/(stage+'-checks.json')).write_text(json.dumps(r,indent=2)+'\n')
