"""Small shared solid-geometry helpers from the proven prism design."""
from pathlib import Path
import numpy as np
import manifold3d as mf
import trimesh

def matrix(q,t=(0,0,0)):return np.column_stack((q,np.array(t,float)))

def xform(s,q=np.eye(3),t=(0,0,0)):return s.transform(matrix(q,t))

def frame(n):
 n=np.asarray(n,float);seed=np.array([0.,0,1]) if abs(n[2])<.9 else np.array([1.,0,0])
 u=np.cross(seed,n);u/=np.linalg.norm(u)
 return np.column_stack((u,np.cross(n,u),n))

def mesh(s):
 m=s.to_mesh64();return trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)

def from_mesh(m):return mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))

def union(ss):return mf.Manifold.batch_boolean(list(ss),mf.OpType.Add)

def subtract(s,ss):return mf.Manifold.batch_boolean([s]+list(ss),mf.OpType.Subtract)

def save(s,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);m=mesh(s);np.savez_compressed(path,v=m.vertices,f=m.faces)

def load(path):
 d=np.load(path);return from_mesh(trimesh.Trimesh(d['v'],d['f'],process=False))

def main(s,allowed=.01):
 cs=sorted(s.decompose(),key=lambda c:c.volume(),reverse=True)
 if not cs:raise ValueError('empty solid')
 discarded=sum(abs(c.volume()) for c in cs[1:])
 if discarded>allowed:raise ValueError(('disconnected components',[c.volume() for c in cs]))
 return cs[0]

def downward_sweep(s,n,clearance=.05):
 f=frame(n);m=mesh(xform(s,f.T));faces=m.triangles[m.face_normals[:,2]>1e-5]
 floor=float(m.bounds[0,2]-100);indices=np.array([[0,1,2],[5,4,3],[0,3,4],[0,4,1],[1,4,5],[1,5,2],[2,5,3],[2,3,0]],dtype=np.uint64)
 prisms=[]
 for p in faces:
  top=p.copy();top[:,2]+=clearance;bottom=top.copy();bottom[:,2]=floor
  v=np.vstack([top,bottom]);q=mf.Manifold(mf.Mesh64(v,indices))
  if not q.is_empty():prisms.append(q)
 return xform(union(prisms),f)
