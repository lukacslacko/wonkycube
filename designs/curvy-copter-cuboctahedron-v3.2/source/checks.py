from hardware import *
def unit(v):return np.array(v)/np.linalg.norm(v)
def assembly(cells,core_part):
 out=[];rank={'K':0,'P':1,'C':2}
 for f in ['K','P','C']:
  row=canonical(f);name=row['name'];n=np.array(row['direction']);s=cells[name]
  # Petals hook past the corner shoulders along their square-face normal,
  # rather than along the nearly parallel corner/petal radial directions.
  if f=='P':
   k=int(np.argmax(abs(n)));n=np.eye(3)[k]*np.sign(n[k])
  fixed=union([v for k,v in cells.items() if k!=name and rank[k[0]]<=rank[f]]+[core_part]);worst=[0,0]
  for d in np.r_[np.arange(0,6,.25),np.arange(6,61,1)]:
   vol=(s.translate(n*d)^fixed).volume()
   if vol>worst[1]:worst=[float(d),float(vol)]
  print('ASSEMBLY',f,worst,flush=True);out.append(dict(family=f,outward_path_direction=n.tolist(),maximum_translation_mm=60,worst=worst));assert worst[1]<.001
 return out
