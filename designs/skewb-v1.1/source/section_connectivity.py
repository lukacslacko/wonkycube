"""Conservative fixed-linewidth layer connectivity, not a slicer toolpath model."""
from skewb_design import *
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

def polygons(cs):
 ps=[]
 for c in cs.decompose():
  loops=c.to_polygons()
  if not loops:continue
  areas=[abs(Polygon(p).area) for p in loops];i=int(np.argmax(areas));p=Polygon(loops[i],[q for j,q in enumerate(loops) if j!=i]).buffer(0)
  if not p.is_empty:ps.extend(list(p.geoms) if p.geom_type=='MultiPolygon' else [p])
 return ps

def check(s,height=.16,width=.42):
 m=mesh(s);lo,hi=m.bounds[:,2];zs=np.arange(lo+height/2,hi,height)
 nodes=[];edges=[];prev=[]
 for layer,z in enumerate(zs):
  cs=s.slice(float(z));cs=cs.offset(-width/2,join_type=mf.JoinType.Round,circular_segments=16).offset(width/2,join_type=mf.JoinType.Round,circular_segments=16)^cs
  ps=[p for p in polygons(cs) if p.area>.001];current=[]
  for p in ps:
   i=len(nodes);nodes.append((p.area*height,float(z),p.bounds));current.append((i,p))
   for j,q in prev:
    if p.intersects(q):edges.append((i,j))
  prev=current
 if not nodes:return []
 e=np.array(edges,dtype=int).reshape((-1,2));graph=coo_matrix((np.ones(len(e)),(e[:,0],e[:,1])),shape=(len(nodes),len(nodes)))
 num,labels=connected_components(graph,directed=False)
 return sorted([dict(volume_mm3=float(sum(nodes[i][0] for i in np.flatnonzero(labels==j))),z_mm=[min(nodes[i][1] for i in np.flatnonzero(labels==j)),max(nodes[i][1] for i in np.flatnonzero(labels==j))],layers=len(set(nodes[i][1] for i in np.flatnonzero(labels==j)))) for j in range(num)],key=lambda r:r['volume_mm3'],reverse=True)
if __name__=='__main__':
 row=next(r for r in ROWS if r['name']=='K01');f=frame(row['direction'])
 for label in ['old','chord-10.5','chord-9.5','chord-8.5','flat-16.5','flat-17.5']:
  s=xform(load(WORK/'trials'/(label+'.npz')),f.T)
  print(label,check(s),flush=True)
