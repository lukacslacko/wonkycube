"""Downward sweep of the actual upper-facing triangles, without convex filling."""
from mechanism import *

def downward_sweep(s,n,clearance=.08):
    f=frame(n);m=mesh(xform(s,f.T)).copy()
    faces=m.triangles[m.face_normals[:,2]>1e-5]
    floor=float(m.bounds[0,2]-30)
    triangles=np.array([[0,1,2],[5,4,3],[0,3,4],[0,4,1],[1,4,5],[1,5,2],[2,5,3],[2,3,0]],dtype=np.uint64)
    prisms=[]
    for p in faces:
        top=p.copy();top[:,2]+=clearance
        bottom=top.copy();bottom[:,2]=floor
        v=np.vstack([top,bottom])
        q=mf.Manifold(mf.Mesh64(v,triangles))
        if not q.is_empty():prisms.append(q)
    return xform(union(prisms),f)
