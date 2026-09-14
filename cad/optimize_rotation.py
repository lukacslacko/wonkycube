import itertools, json, time
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import differential_evolution, minimize
from scipy.stats import qmc

OUT=Path(__file__).parent
axes=np.array(list(itertools.product([-1,1],repeat=3)),float)/np.sqrt(3)
# The even signed coordinate permutations are the 12 legal edge frames.
group=[]
for p in itertools.permutations(range(3)):
 for signs in itertools.product([-1,1],repeat=3):
  m=np.eye(3)[list(p)]*np.array(signs)[:,None]
  if np.linalg.det(m)>0.9 and np.prod(signs)>0:
   group.append(m)
group=np.array(group)
base=np.array([1,1,0])/np.sqrt(2)
group=group[np.lexsort((group@base).T[::-1])]
edge_dirs=group@base
flip=2*np.outer(base,base)-np.eye(3)

def samples(power):
 # Uniform solid-angle sampling from a sphere, restricted to the reference lens.
 p=qmc.Sobol(2,scramble=False).random_base2(power)
 z=2*p[:,0]-1
 phi=2*np.pi*p[:,1]
 u=np.column_stack((np.sqrt(1-z*z)*np.cos(phi),np.sqrt(1-z*z)*np.sin(phi),z))
 return u[(u[:,0]+u[:,1]-abs(u[:,2]))>=1+1e-9]

def prepare(power):
 u=samples(power)
 # Include the lens's only other proper self-isometry (a half turn).
 dirs=np.einsum('eij,snj->esni',group,np.stack((u,u@flip.T)))
 return u,dirs

u,dirs=prepare(12)
ii,jj=np.triu_indices(12,1)
evaluations=0
def distances(angles,ds=dirs):
 R=Rotation.from_euler('xyz',angles,degrees=True).as_matrix()
 h=50/np.max(np.abs(ds@R),axis=-1)
 # Optimize the weakest pair, with each piece in either physically matching frame.
 delta=h[ii,0,None,:]-h[jj,:,:]
 dd=np.sqrt(np.mean(delta*delta,axis=-1)).min(axis=-1)
 return dd
def score(angles):
 return -distances(angles).min()

if __name__=='__main__':
 start=time.time()
 results=[]
 for seed in [11,29,47,83]:
  result=differential_evolution(score,[(0,90)]*3,popsize=22,maxiter=220,
                                tol=2e-6,polish=False,seed=seed,workers=1)
  polish=minimize(score,result.x,method='Nelder-Mead',options={'maxiter':1200,'xatol':1e-7,'fatol':1e-8})
  a=polish.x
  results.append({'seed':seed,'angles_xyz_deg':a.tolist(),'sample_min_rms_mm':-polish.fun,'nfev':int(result.nfev+polish.nfev)})
  print(results[-1],flush=True)
 best=max(results,key=lambda v:v['sample_min_rms_mm'])
 # Independently denser validation and a fine-mesh local refinement.
 uv,dv=prepare(17)
 def dense_score(a): return -distances(a,dv).min()
 dense=minimize(dense_score,best['angles_xyz_deg'],method='Nelder-Mead',options={'maxiter':1500,'xatol':1e-7,'fatol':1e-8})
 a=dense.x
 R=Rotation.from_euler('xyz',a,degrees=True).as_matrix()
 d=distances(a,dv)
 result={'cube_side_mm':100,'rotation_convention':'Active cube-to-mechanism R = Rz(z) @ Ry(y) @ Rx(x); x/y/z fixed mechanism axes; degrees',
 'angles_xyz_deg':a.tolist(),'cube_to_mechanism_matrix':R.tolist(),
 'cone_half_angle_deg':float(np.degrees(np.arccos(1/np.sqrt(3)))),
 'objective':'Maximize minimum over 66 unordered pairs of equal-solid-angle RMS radial outer surface difference, minimized over the two proper self-isometries of the edge lens; cube side 100 mm',
 'min_pair_rms_mm':float(d.min()),'mean_pair_rms_mm':float(d.mean()),
 'sampling_directions_per_edge_search':len(u),'sampling_directions_per_edge_validation':len(uv),
 'search_runs':results,'dense_refinement_evaluations':int(dense.nfev),
 'pair_scores':[{'edge_a':int(i+1),'edge_b':int(j+1),'rms_mm':float(v)} for i,j,v in zip(ii,jj,d)],
 'edge_directions':edge_dirs.tolist(),'edge_frames':group.tolist(),
 'global_optimum_proven':False,'seconds':time.time()-start}
 (OUT/'rotation.json').write_text(json.dumps(result,indent=2))
 print(json.dumps({k:result[k] for k in ['angles_xyz_deg','min_pair_rms_mm','mean_pair_rms_mm','seconds']},indent=2),flush=True)
