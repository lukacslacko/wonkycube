"""Subtract-only lead-in rounding and clearance revision of the v3.1 meshes."""
from mechanism_v3 import *

INNER_LIMIT=35.5
INNER_WORK_RADIUS=37.0
EDGE_INNER_ROUND=.60
CORNER_INNER_ROUND=.45
TRACK_EXTRA_CLEARANCE=.20
ORBIT_SEGMENTS=288

def rotational_profile(s,n):
    """Project each surface triangle into (rho,z), preserving concavities.

    At every sampled z the triangle projects to a radial interval. Using the
    closest point on its horizontal segment captures the inner radial bound;
    projecting only the original vertices would omit this. Subdividing at
    <=0.10 mm z spacing keeps the radial chord approximation small relative
    to the explicitly added 0.20 mm clearance. No whole-profile convex hull.
    """
    m=mesh(xform(s,frame(n).T));polys=[]
    for tri in m.triangles:
        zs=np.unique(tri[:,2]);cuts=[]
        for lo,hi in zip(zs[:-1],zs[1:]):
            cuts.extend(np.linspace(lo,hi,max(2,int(np.ceil((hi-lo)/.10))+1)))
        if not cuts:continue
        cuts=np.unique(cuts);bounds=[]
        for z in cuts:
            points=[]
            for i,j in [(0,1),(1,2),(2,0)]:
                p,q=tri[i],tri[j]
                if abs(q[2]-p[2])<1e-10:
                    if abs(z-p[2])<1e-9:points.extend([p[:2],q[:2]])
                elif min(p[2],q[2])-1e-9<=z<=max(p[2],q[2])+1e-9:
                    points.append((p+(q-p)*np.clip((z-p[2])/(q[2]-p[2]),0,1))[:2])
            if not points:continue
            pts=np.asarray(points);rho_max=float(np.linalg.norm(pts,axis=1).max());rho_min=rho_max
            for p in pts:
                for q in pts:
                    delta=q-p;den=delta@delta;t=0 if den<1e-20 else np.clip(-(p@delta)/den,0,1)
                    rho_min=min(rho_min,float(np.linalg.norm(p+t*delta)))
            bounds.append([z,rho_min,rho_max])
        for p,q in zip(bounds[:-1],bounds[1:]):
            poly=[[p[1],p[0]],[p[2],p[0]],[q[2],q[0]],[q[1],q[0]]]
            if abs((p[2]-p[1]+q[2]-q[1])*(q[0]-p[0]))>1e-12:polys.append(poly)
    # Each input polygon has positive winding; NonZero unions overlapping cells.
    return mf.CrossSection(polys,mf.FillRule.NonZero).simplify(.002)

def track_cutter(foot,n,clearance=GAP+TRACK_EXTRA_CLEARANCE):
    profile=rotational_profile(foot,n)
    widened=profile.offset(clearance,join_type=mf.JoinType.Round,circular_segments=64)
    return xform(widened.revolve(ORBIT_SEGMENTS),frame(n)),profile

def protected_axle(n):
    # Protect the foot and central stem, then the washer seat/collar. A broad
    # cylinder all the way down would also protect the flange track itself.
    stem=mf.Manifold.cylinder(150,3.75,3.75,144).translate([0,0,20])
    cup=mf.Manifold.cylinder(150,10,10,144).translate([0,0,33.4])
    return xform(stem+cup,frame(n))

def round_inner(s,radius,axis=None):
    working_ball=mf.Manifold.sphere(INNER_WORK_RADIUS,192)
    limit_ball=mf.Manifold.sphere(INNER_LIMIT,192)
    inner=s^working_ball
    protected=inner-limit_ball
    if axis is not None:protected+=inner^protected_axle(axis)
    kernel=mf.Manifold.sphere(radius,24)
    seed=inner.minkowski_difference(kernel)+protected
    rounded=(seed.minkowski_sum(kernel)^inner)+(s-limit_ball)
    return main_component(rounded^s)

def widen_corner(s,n,cutters):
    limit=mf.Manifold.sphere(INNER_LIMIT,192)
    removable=(union(cutters)^limit)-protected_axle(n)
    return main_component(s-removable)
