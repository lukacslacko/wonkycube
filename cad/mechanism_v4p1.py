"""Targeted transverse fillets along the two radial ridges of each v4 edge."""
from mechanism_v3 import *
from scipy.optimize import brentq

RADIAL_RIDGE_ROUND=2.0
PRESERVE_FOOT_RADIUS=33.5
FULL_ROUND_START=37.5
TANGENCY_ALLOWANCE=.01

def ridge_cutter(radius=RADIAL_RIDGE_ROUND):
    """Loft a circular fillet tangent to both offset conical faces.

    For the canonical E12 +X ridge, let h=(GAP/2)/sqrt(2), X=x-h.
    At a fixed x, the positive-z conical boundary is
        y=h+X*(z+h)/(X-z-h).
    Its derivative is X**2/(X-z-h)**2. A radius-r circle centered
    at (yc,0) is tangent where z*sqrt(1+1/slope**2)=r. Mirror its
    arc about z=0, then loft these profiles along the radial ridge.
    Matching position and slope in every section also matches the axial
    derivative at the tangency curve. No broad-face or flange rounding.
    """
    h=(GAP/2)/np.sqrt(2);rings=[]
    xs=np.r_[np.arange(PRESERVE_FOOT_RADIUS,FULL_ROUND_START,.25),np.arange(FULL_ROUND_START,90.01,.75),90.0]
    xs=np.unique(xs)
    for x in xs:
        u=np.clip((x-PRESERVE_FOOT_RADIUS)/(FULL_ROUND_START-PRESERVE_FOOT_RADIUS),0,1)
        r=max(.01,radius*u*u*(3-2*u));X=x-h
        slope=lambda z:X*X/(X-z-h)**2
        zt=brentq(lambda z:z*np.sqrt(1+1/slope(z)**2)-r,0,r)
        yt=h+X*(zt+h)/(X-zt-h);yc=yt+zt/slope(zt)
        angles=np.linspace(-np.arcsin(zt/r),np.arcsin(zt/r),65)
        arc=np.column_stack((yc-r*np.cos(angles)-TANGENCY_ALLOWANCE,r*np.sin(angles)))
        # A tiny retreat from exact tangency avoids cutting a faceting skin.
        yz=np.vstack([[-10,0],[-10,-zt],arc,[-10,zt]])
        rings.append(np.column_stack((np.full(len(yz),x),yz)))
    vertices=np.vstack(rings);n=len(rings[0]);faces=[]
    for k in range(len(rings)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;c=a+n;d=b+n
            faces.extend([[a,b,c],[b,d,c]])
    for j in range(1,n-1):
        faces.append([0,j+1,j])
        a=(len(rings)-1)*n;faces.append([a,a+j,a+j+1])
    m=trimesh.Trimesh(vertices,np.array(faces),process=True)
    if m.volume<0:m.invert()
    assert m.is_watertight and m.is_winding_consistent
    first=from_mesh(m)
    second=xform(first,np.array([[0,1,0],[1,0,0],[0,0,-1]]))
    return first+second

def round_radial_ridges(s,Q,cutter):
    return main_component(s-xform(cutter,Q))
