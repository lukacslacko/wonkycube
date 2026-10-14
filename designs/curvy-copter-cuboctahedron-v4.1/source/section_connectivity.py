"""Conservative fixed-linewidth layer connectivity, not a slicer toolpath model."""
from design import *
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
 results=[]
 for j in range(num):
  ids=np.flatnonzero(labels==j);b=np.array([nodes[i][2] for i in ids]);zs=[nodes[i][1] for i in ids]
  results.append(dict(volume_mm3=float(sum(nodes[i][0] for i in ids)),z_mm=[min(zs),max(zs)],layers=len(set(zs)),bounds_mm=[[float(b[:,0].min()),float(b[:,1].min()),min(zs)-height/2],[float(b[:,2].max()),float(b[:,3].max()),max(zs)+height/2]]))
 return sorted(results,key=lambda r:r['volume_mm3'],reverse=True)
