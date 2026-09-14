"""Constant 3 mm transverse ridge fillets, including the stepped track region."""
from mechanism_v3 import *
from scipy.optimize import brentq

RADIAL_RIDGE_ROUND=3.0
CUTTER_START=20.0
CUTTER_END=90.0
PLAIN_CONE_START=33.5
TANGENCY_ALLOWANCE=.005

def cone_circle(x,radius):
    h=(GAP/2)/np.sqrt(2);X=x-h
    slope=lambda z:X*X/(X-z-h)**2
    zt=brentq(lambda z:z*np.sqrt(1+1/slope(z)**2)-radius,0,radius)
    yt=h+X*(zt+h)/(X-zt-h)
    return yt+zt/slope(zt),float(np.arcsin(zt/radius))

def profile_circle(polygons,radius):
    """Find the nearest centered radius-r circle inside the front profile.

    On every interval of z with a fixed front boundary y=m*z+b,
    maximize y+sqrt(r*r-z*z). The maximum gives the circle center;
    the maximizing z gives tangency. This follows the real rail steps
    instead of assuming that the inner profile remains conical.
    """
    segments=[];breaks=[-radius,radius]
    for p in polygons:
        for a,b in zip(p,np.roll(p,-1,axis=0)):
            dz=b[1]-a[1]
            if abs(dz)<1e-10:continue
            lo=max(-radius,min(a[1],b[1]));hi=min(radius,max(a[1],b[1]))
            if hi-lo<1e-9:continue
            slope=(b[0]-a[0])/dz;intercept=a[0]-slope*a[1]
            segments.append((lo,hi,slope,intercept));breaks.extend([lo,hi])
    best=(-np.inf,0);breaks=np.unique(breaks)
    for lo,hi in zip(breaks[:-1],breaks[1:]):
        mid=(lo+hi)/2;active=[s for s in segments if s[0]-1e-9<=mid<=s[1]+1e-9]
        if not active:continue
        # A track section can contain a thin foreground rib, then a void,
        # then the main body. Place the circle in the main body's last solid
        # interval, not in that rib or the intervening void. The final cut
        # also trims any foreground rib that intrudes into the fillet.
        active=sorted(active,key=lambda s:s[2]*mid+s[3])
        if len(active)<2:raise ValueError('Missing rear material interval')
        _,_,m,b=active[-2]
        z=float(np.clip(radius*m/np.sqrt(1+m*m),lo,hi))
        center=m*z+b+np.sqrt(max(0,radius*radius-z*z))
        if center>best[0]:best=(center,abs(z))
    if not np.isfinite(best[0]):raise ValueError('No continuous front profile')
    return float(best[0]),float(np.arcsin(np.clip(best[1]/radius,0,1)))

def ridge_cutter(reference_edge,radius=RADIAL_RIDGE_ROUND):
    F=np.array([[0,1,0],[0,0,1],[1,0,0]])
    local=xform(reference_edge,F);cache={}
    def sample(x):
        if x not in cache:
            cy,angle=(cone_circle(x,radius) if x>=PLAIN_CONE_START else profile_circle(local.slice(x).to_polygons(),radius))
            # Below the physical start of a convex ridge the tangent angle
            # tends to zero. Keep a nondegenerate cutter of negligible width;
            # the radius itself never decreases.
            cache[x]=(cy,max(angle,.0005))
        return cache[x]
    xs=list(np.r_[np.arange(CUTTER_START,PLAIN_CONE_START,.25),np.arange(PLAIN_CONE_START,CUTTER_END,.5),CUTTER_END])
    for depth in range(10):
        extra=[]
        for lo,hi in zip(xs[:-1],xs[1:]):
            a=sample(lo);b=sample(hi);mid=(lo+hi)/2;c=sample(mid)
            if hi-lo>.002 and (abs(a[1]-b[1])>.025 or abs(c[0]-(a[0]+b[0])/2)>.005 or abs(c[1]-(a[1]+b[1])/2)>.01):extra.append(mid)
        if not extra:break
        xs=sorted(xs+extra)
    rings=[];records=[]
    for x in xs:
        cy,angle=sample(x);angles=np.linspace(-angle,angle,97)
        arc=np.column_stack((cy-radius*np.cos(angles)-TANGENCY_ALLOWANCE,radius*np.sin(angles)))
        zt=radius*np.sin(angle)
        yz=np.vstack([[-20,0],[-20,-zt],arc,[-20,zt]])
        rings.append(np.column_stack((np.full(len(yz),x),yz)))
        records.append({'x_mm':float(x),'circle_center_y_mm':cy-TANGENCY_ALLOWANCE,'radius_mm':radius,'half_arc_angle_rad':angle})
    vertices=np.vstack(rings);n=len(rings[0]);faces=[]
    for k in range(len(rings)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;c=a+n;d=b+n
            faces.extend([[a,b,c],[b,d,c]])
    for j in range(1,n-1):
        faces.append([0,j+1,j]);a=(len(rings)-1)*n;faces.append([a,a+j,a+j+1])
    m=trimesh.Trimesh(vertices,np.array(faces),process=True)
    if m.volume<0:m.invert()
    assert m.is_watertight and m.is_winding_consistent
    # The track ridge bends steeply in x. Stretch x during simplification so
    # a small normal-distance tolerance cannot become a much larger error
    # in a transverse circle section on those steep portions.
    first=xform(xform(from_mesh(m),np.diag([20.,1.,1.])).simplify(.001),np.diag([.05,1.,1.]))
    second=xform(first,np.array([[0,1,0],[1,0,0],[0,0,-1]]))
    return first+second,records

def round_radial_ridges(s,Q,cutter):
    return main_component(s-xform(cutter,Q))
