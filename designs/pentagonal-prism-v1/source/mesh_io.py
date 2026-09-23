"""Closed float32 STL export with bounded cleanup of collapsed/coincident faces."""
from conical_design import *
from scipy.spatial import cKDTree

def weld_export_slits(m):
 """Collapse short sides of numerical slits, never cap a finite opening.

 Float32 can duplicate a tangent vertex or turn a tiny ribbon into a
 non-manifold edge. Only vertices within 0.003 mm of another boundary
 vertex are considered; each cluster moves at most 0.002 mm and the
 cumulative per-pass bound cannot exceed 0.004 mm.
 """
 c=m.copy();total=0.
 for repeat in range(4):
  edges=c.edges_unique[np.bincount(c.edges_unique_inverse)!=2]
  if not len(edges):break
  largest=0.;changed=False
  for group in trimesh.graph.connected_components(edges,min_len=1):
   pairs=cKDTree(c.vertices[group]).query_pairs(.003,output_type='ndarray')
   if not len(pairs):continue
   for cluster in trimesh.graph.connected_components(pairs,min_len=2):
    ids=np.asarray(group)[cluster];p=c.vertices[ids];center=p.mean(axis=0).astype(np.float32).astype(float)
    move=float(np.linalg.norm(p-center,axis=1).max())
    if move>min(.002,.004-total):continue
    c.vertices[ids]=center;largest=max(largest,move);changed=True
  if not changed:break
  total+=largest
  c.merge_vertices(digits_vertex=8);c.update_faces(c.nondegenerate_faces());c.update_faces(c.unique_faces());c.remove_unreferenced_vertices()
 c.metadata=m.metadata.copy()
 prior=c.metadata.get('cleanup',{}).copy()
 c.metadata['cleanup']={**prior,'slit_weld_displacement_bound_mm':total+prior.get('slit_weld_displacement_bound_mm',0)}
 return c

def close_numerical_contacts(m):
 """Close quantization-only edge contacts with tiny local solid unions.

 Collapsed multi-face contacts and boundary slits narrower than 0.002 mm
 are treated; finite openings are not capped. Each capsule is
 0.001--0.003 mm in radius; cumulative local envelope is at most 0.006 mm.
 The delivered shapes are independently collision- and fidelity-checked.
 """
 prior=m.metadata.get('cleanup',{}).copy();used=prior.get('local_contact_envelope_mm',0.)
 solid=from_mesh(m)
 if solid.status()!=mf.Error.NoError:return None
 counts=[];added=0.;extra=0.
 for radius in [.001,.002,.003,None]:
  c=float32_candidate(mesh(solid),8);c.metadata=m.metadata.copy();c=weld_export_slits(c)
  if c.is_watertight and c.is_winding_consistent and c.volume>0:
   c.metadata['cleanup']={**prior,**c.metadata.get('cleanup',{}),'coordinate_decimals':min(8,prior.get('coordinate_decimals',12)),
     'local_contact_envelope_mm':used+extra,'local_contact_capsules':prior.get('local_contact_capsules',0)+sum(counts),
     'local_contact_added_volume_mm3':prior.get('local_contact_added_volume_mm3',0.)+added}
   return c
  if radius is None or used+extra+radius>.00600001:return None
  incidence=np.bincount(c.edges_unique_inverse);contacts=c.edges_unique[incidence>2]
  boundary=c.edges_unique[incidence==1];slits=[]
  for group in trimesh.graph.connected_components(boundary,min_len=2):
   points=c.vertices[group];v=points-points.mean(axis=0);_,_,basis=np.linalg.svd(v,full_matrices=False)
   width=float(np.linalg.norm(v-np.outer(v@basis[0],basis[0]),axis=1).max())
   if width<.002:
    ids=set(group);slits.extend(e for e in boundary if e[0] in ids and e[1] in ids)
  bad=np.vstack([contacts,np.asarray(slits,dtype=int).reshape((-1,2))])
  if not len(bad):return None
  capsules=[]
  for edge in bad:
   p,q=c.vertices[edge];d=q-p;h=float(np.linalg.norm(d))
   if h<1e-9:continue
   capsules.append(xform(mf.Manifold.cylinder(h+2*radius,radius,radius,12),frame(d/h),p-d/h*radius))
  before=solid.volume();solid=union([solid]+capsules);added+=solid.volume()-before;extra+=radius;counts.append(len(capsules))
 return None

def cleaned(m,_warm=True):
 components=sorted(m.split(only_watertight=False),key=lambda c:abs(c.volume),reverse=True)
 if len(components)>1:
  discarded=[float(c.volume) for c in components[1:]]
  if sum(abs(v) for v in discarded)<.02:
   metadata=m.metadata.copy();m=components[0];m.metadata=metadata
   m.metadata.setdefault('cleanup',{})['discarded_numerical_component_volumes_mm3']=discarded
 local=close_numerical_contacts(m)
 if local is not None:return local
 budget=.010-m.metadata.get('cleanup',{}).get('simplification_mm',0)
 strategies=[(0,0)]+[(0,t) for t in [.002,.004,.006,.008,.010] if t<=budget]+[(r,t) for r in [.002,.004,.006,.008,.010] for t in [0,.002,.004] if r+t<=budget+1e-9]
 for reset_tol,tolerance in strategies:
  if reset_tol:
   reset=from_mesh(m).as_original().simplify(reset_tol)
   base=from_mesh(mesh(reset))
   source=mesh(base if tolerance==0 else base.simplify(tolerance))
  else:source=m if tolerance==0 else mesh(from_mesh(m).simplify(tolerance))
  for digits in [12,9,8,7,6,5,4,3]:
   c=source.copy();c.vertices=(c.vertices if digits==12 else np.round(c.vertices,digits)).astype(np.float32).astype(float);c.merge_vertices(digits_vertex=8);c.update_faces(c.nondegenerate_faces());c.remove_unreferenced_vertices()
   f=c.faces;key=np.sort(f,axis=1);_,inverse,counts=np.unique(key,axis=0,return_inverse=True,return_counts=True);keep=np.ones(len(f),bool)
   for group in np.flatnonzero(counts>1):
    ids=np.flatnonzero(inverse==group);tri=f[ids];parity=((tri[:,0]>tri[:,1]).astype(int)+(tri[:,0]>tri[:,2]).astype(int)+(tri[:,1]>tri[:,2]).astype(int))%2
    positive=ids[parity==0];negative=ids[parity==1];keep[ids]=False
    if len(positive)>len(negative):keep[positive[0]]=True
    elif len(negative)>len(positive):keep[negative[0]]=True
   c.update_faces(keep);c.remove_unreferenced_vertices()
   if not c.is_watertight:c=weld_export_slits(c)
   if c.is_watertight and c.is_winding_consistent and c.volume>0:
    prior=m.metadata.get('cleanup',{})
    c.metadata['cleanup']={**prior,**c.metadata.get('cleanup',{}),'simplification_mm':reset_tol+tolerance+prior.get('simplification_mm',0),'coordinate_decimals':min(digits,prior.get('coordinate_decimals',12)),'removed_coincident_faces':int(np.count_nonzero(~keep))+prior.get('removed_coincident_faces',0)}
    return c
 if _warm:
  for warm_tol in [.004,.008]:
   if warm_tol>budget:continue
   candidate=mesh(from_mesh(m).as_original().simplify(warm_tol))
   prior=m.metadata.get('cleanup',{}).copy()
   candidate.metadata['cleanup']={**prior,'simplification_mm':warm_tol+prior.get('simplification_mm',0)}
   try:return cleaned(candidate,False)
   except ValueError:pass
 raise ValueError('Closed STL export failed within a cumulative 0.010 mm simplification allowance and 0.001 mm coordinate quantization')

def float32_candidate(m,digits=6):
 """Quantize and cancel opposite coincident triangles without capping openings."""
 c=m.copy();c.vertices=np.round(c.vertices,digits).astype(np.float32).astype(float);c.merge_vertices(digits_vertex=8);c.update_faces(c.nondegenerate_faces());c.remove_unreferenced_vertices()
 f=c.faces;key=np.sort(f,axis=1);_,inverse,counts=np.unique(key,axis=0,return_inverse=True,return_counts=True);keep=np.ones(len(f),bool)
 for group in np.flatnonzero(counts>1):
  ids=np.flatnonzero(inverse==group);tri=f[ids];parity=((tri[:,0]>tri[:,1]).astype(int)+(tri[:,0]>tri[:,2]).astype(int)+(tri[:,1]>tri[:,2]).astype(int))%2
  positive=ids[parity==0];negative=ids[parity==1];keep[ids]=False
  if len(positive)>len(negative):keep[positive[0]]=True
  elif len(negative)>len(positive):keep[negative[0]]=True
 c.update_faces(keep);c.remove_unreferenced_vertices();return c
