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
THETA0=np.degrees(np.arccos(1/np.sqrt(3)))
SIDE=100.0
CORE_R=24.0
INNER_R=24.5
GAP=0.50
FLARE=59.0
CORE_PAD=22.0
SEAT=36.0
SLEEVE_LEN=14.3
CAP_START=40.6

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

def cut_solid(offset=0.0,segments=192,flare=FLARE):
 # r is distance from the common mechanism center. The meridian is sampled
 # finely through the retaining flange, then offset in true millimeters.
 rs=np.unique(np.r_[0,np.linspace(24,28,17),np.linspace(28,32,9),np.linspace(32,33,17),250])
 th=np.radians(np.interp(rs,[0,24,28,32,33,250],[THETA0,THETA0,flare,flare,THETA0,THETA0]))
 coords=np.column_stack((rs*np.sin(th),rs*np.cos(th)))
 coords=np.vstack((coords,[0,coords[-1,1]]))
 section=mf.CrossSection([coords])
 if offset: section=section.offset(offset,join_type=mf.JoinType.Round,circular_segments=32)
 return section.revolve(segments)

def build_cells(Rcube=np.eye(3),segments=192,flare=FLARE):
 cube=xform(mf.Manifold.cube([SIDE]*3,center=True),Rcube)
 outer=mf.Manifold.sphere(INNER_R,segments)
 shell=cube-outer
 small=cut_solid(-GAP/2,segments,flare)
 large=cut_solid(GAP/2,segments,flare)
 ci=[xform(small,frame(n)) for n in AXES]
 co=[xform(large,frame(n)) for n in AXES]
 corners=[subtract(shell^ci[i],[co[j] for j in range(8) if j!=i]) for i in range(8)]
 edges=[subtract(shell^ci[i]^ci[j],[co[k] for k in range(8) if k not in (i,j)]) for i,j in EDGES]
 return cube,corners,edges

def convex_inflate(s,amount):
 pts=mesh(s).vertices
 hull=ConvexHull(pts)
 eq=hull.equations.copy();eq[:,3]-=amount
 # Collapse coplanar triangle planes, avoiding redundant Qhull constraints.
 eq=np.unique(np.round(eq,9),axis=0)
 verts=HalfspaceIntersection(eq,pts.mean(axis=0)).intersections
 return from_mesh(trimesh.convex.convex_hull(verts))

def assembly_relief(corners,edges,segments=192):
 # Every corner must slide outward along its screw axis, past stationary
 # edges. Subtract a conservative convex envelope of that continuous path.
 # Geometry removed from a valid turning cell cannot create turn collisions.
 ball=mf.Manifold.sphere(35.5,segments)
 reliefs=[];result=[]
 for a,c in enumerate(corners):
  cutters=[]
  for e,(i,j) in zip(edges,EDGES):
   if a not in (i,j):continue
   foot=e^ball
   swept=union([foot,foot.translate(-20*AXES[a])]).hull()
   cutters.append(convex_inflate(swept,.30))
  cutter=union(cutters)
  result.append(c-cutter);reliefs.append((c^cutter).volume())
 return result,reliefs

def core(segments=192):
 s=mf.Manifold.sphere(CORE_R,segments).trim_by_plane([0,0,1],-20)
 for n in AXES: s=s.trim_by_plane(-n,-CORE_PAD)
 for n in AXES:
  f=frame(n)
  # Pilot matched to nominal OD4.6 x L5.7 flush M3 inserts. Extra depth below
  # the insert provides a melt reservoir and screw-tip clearance.
  hole=mf.Manifold.cylinder(7.5,2.10,2.10,64).translate([0,0,14.5])
  pilot=mf.Manifold.cylinder(7,1.7,1.7,64).translate([0,0,10])
  lead=mf.Manifold.cylinder(0.5,2.1,2.6,64).translate([0,0,21.5])
  s=s-xform(union([hole,pilot,lead]),f)
 return s

def sleeve(length=SLEEVE_LEN):
 # Small bevels avoid elephant-foot interference on the printed journal.
 p=[[1.7,0],[2.8,0],[3,.2],[3,length-.2],[2.8,length],[1.7,length]]
 return mf.CrossSection([p]).revolve(96)

def d_profile(radius,flat,height,start):
 s=mf.Manifold.cylinder(height,radius,radius,96).translate([0,0,start])
 return s.trim_by_plane([-1,0,0],-flat)

def finish_corners(cube,corners):
 bodies=[];caps=[]
 for i,(s,n) in enumerate(zip(corners,AXES)):
  f=frame(n)
  bearing=mf.Manifold.cylinder(50,3.2,3.2,96)
  lower_cb=mf.Manifold.cylinder(CAP_START-SEAT+.01,3.8,3.8,96).translate([0,0,SEAT])
  cb=d_profile(5.0,4.2,100,CAP_START)
  s=s-xform(union([bearing,lower_cb,cb]),f)
  # The cap closes the axial screw access and follows the actual tilted cube.
  cap=xform(d_profile(4.75,3.95,100,CAP_START),f)^cube
  mag=mf.Manifold.cylinder(2.2,2.1,2.1,64).translate([0,0,CAP_START])
  cap=cap-xform(mag,f)
  bodies.append(s);caps.append(cap)
 return bodies,caps

if __name__=='__main__':
 import time
 out=Path(__file__).parent/'prototype';out.mkdir(exist_ok=True)
 t=time.time()
 cube,cs,es=build_cells(segments=96)
 cr=core(96)
 cs,caps=finish_corners(cube,cs)
 for group,ss in [('C',cs),('E',es),('P',caps),('core',[cr])]:
  for i,s in enumerate(ss):
   m=mesh(s)
   m.export(out/f'{group}{i+1:02}.stl')
   print(group,i+1,round(s.volume(),2),len(s.decompose()),m.is_watertight,flush=True)
 print('seconds',time.time()-t,flush=True)
