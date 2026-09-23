"""Analytic surfaces of revolution for a corner turning conical Redi mechanism."""
from pathlib import Path
import itertools, json, math
import numpy as np
import manifold3d as mf
import trimesh
from scipy.spatial.transform import Rotation
from scipy.spatial import ConvexHull, HalfspaceIntersection

AXES=np.array(list(itertools.product([-1,1],repeat=3)),float)/np.sqrt(3)
EDGES=[(i,j) for i in range(8) for j in range(i+1,8) if np.isclose(AXES[i]@AXES[j],1/3)]
EDGES.sort(key=lambda ij:tuple(AXES[ij[0]]+AXES[ij[1]]))

def matrix(R,t=(0,0,0)):
 return np.column_stack((R,np.array(t,float)))
def xform(s,R=np.eye(3),t=(0,0,0)):
 return s.transform(matrix(R,t))
def frame(n):
 n=np.array(n,float)
 u=np.cross([0,0,1],n);u/=np.linalg.norm(u)
 v=np.cross(n,u)
 return np.column_stack((u,v,n))
def mesh(s):
 m=s.to_mesh64()
 return trimesh.Trimesh(np.array(m.vert_properties)[:,:3],np.array(m.tri_verts),process=False)
def from_mesh(m):
 return mf.Manifold(mf.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
def union(ss): return mf.Manifold.batch_boolean(ss,mf.OpType.Add)
def subtract(s,ss): return mf.Manifold.batch_boolean([s]+list(ss),mf.OpType.Subtract)

