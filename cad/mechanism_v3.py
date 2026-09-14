"""80 mm revision: square retaining rails, exact assembly sweeps, rounded exterior."""
from mechanism import *
from poc_mechanism import poc_core
from exact_assembly_sweep import downward_sweep

SIDE=80.0
GAP=.20
FOOT_R=3.7
FOOT_TOP=25.5
PILOT_D=2.6
SCREW_BORE_D=3.3
ACCESS_D=13.8
POC_SEAT=34.0
WASHER_OD=13.0
WASHER_ID=3.2
WASHER_T=.55
AXIAL_PLAY=.10
SCREW_LENGTH=20.0
SCREW_TOP=POC_SEAT+AXIAL_PLAY+WASHER_T
SCREW_TIP=SCREW_TOP-SCREW_LENGTH
RAIL_RADIUS=28.0
EXTERIOR_ROUND=1.0
PROTECTED_RADIUS=35.5
ASSEMBLY_RELIEF_SIDE_CLEARANCE=.03

def main_component(s):
    pieces=s.decompose()
    main=max(pieces,key=lambda p:p.volume())
    debris=sum(abs(p.volume()) for p in pieces if p is not main)
    if debris>1e-4:raise ValueError(f'Meaningful disconnected material: {debris} mm3')
    return main

def cut_solid_v3(offset=0,segments=192):
    # rho is perpendicular distance to the active axle; z runs along it.
    # A constant-z shoulder at z=17 replaces the old sloping radial ramp.
    points=[[0,0],[np.sqrt(2)*14,14],[RAIL_RADIUS-.4,14],
        [RAIL_RADIUS,14.4],[RAIL_RADIUS,16.8],[RAIL_RADIUS-.2,17],
        [np.sqrt(2)*17,17],[np.sqrt(2)*200,200],[0,200]]
    s=mf.CrossSection([points])
    if offset:s=s.offset(offset,join_type=mf.JoinType.Round,circular_segments=32)
    return s.revolve(segments)

def build_cells_v3(Rcube,segments=192):
    cube=xform(mf.Manifold.cube([SIDE]*3,True),Rcube)
    shell=cube-mf.Manifold.sphere(INNER_R,segments)
    small=cut_solid_v3(-GAP/2,segments);large=cut_solid_v3(GAP/2,segments)
    ci=[xform(small,frame(n)) for n in AXES];co=[xform(large,frame(n)) for n in AXES]
    cs=[subtract(shell^ci[i],[co[j] for j in range(8) if j!=i]) for i in range(8)]
    es=[]
    for i,j in EDGES:
        cell=subtract(shell^ci[i]^ci[j],[co[k] for k in range(8) if k not in (i,j)])
        components=cell.decompose();main=max(components,key=lambda p:p.volume())
        # Two annular belts also intersect in small, disconnected inner cells.
        # They are intentionally left as voids, not printed as floating tabs.
        for extra in components:
            if extra is main:continue
            if np.max(np.linalg.norm(mesh(extra).vertices,axis=1))>33.1:
                raise ValueError('Unexpected detached cell outside the inner rail region')
        es.append(main)
    return cube,cs,es

def assembly_relief_v3(corners,edges,segments=192):
    ball=mf.Manifold.sphere(PROTECTED_RADIUS,segments);result=[];removed=[]
    feet=[e^ball for e in edges]
    for a,c in enumerate(corners):
        # Axial clearance alone leaves the vertical walls of a sweep exactly
        # coincident with the edge. Give those walls a small positive clearance
        # too, preserving the non-convex shape of the retaining shoulder.
        kernel=mf.Manifold.sphere(ASSEMBLY_RELIEF_SIDE_CLEARANCE,12)
        cutters=[downward_sweep(e,AXES[a],.08).minkowski_sum(kernel) for pair,e in zip(EDGES,feet) if a in pair]
        new=main_component(c-union(cutters));removed.append(c.volume()-new.volume());result.append(new)
    return result,removed

def finish_corners_v3(corners):
    result=[]
    for s,n in zip(corners,AXES):
        foot=mf.Manifold.cylinder(FOOT_TOP-CORE_PAD,FOOT_R,FOOT_R,144).translate([0,0,CORE_PAD])
        bore=mf.Manifold.cylinder(150,SCREW_BORE_D/2,SCREW_BORE_D/2,128)
        well=mf.Manifold.cylinder(150,ACCESS_D/2,ACCESS_D/2,192).translate([0,0,POC_SEAT])
        result.append(main_component((s+xform(foot,frame(n)))-xform(union([bore,well]),frame(n))))
    return result

def round_exterior(s):
    # Morphological opening rounds acute convex edges while keeping planar
    # face interiors. Seeding the protected inner region before dilation
    # preserves every retaining shoulder, bearing foot and washer seat.
    s=s.simplify(.012)
    kernel=mf.Manifold.sphere(EXTERIOR_ROUND,24)
    eroded=s.minkowski_difference(kernel)
    seed=eroded+(s^mf.Manifold.sphere(PROTECTED_RADIUS,192))
    rounded=main_component(seed.minkowski_sum(kernel)^s).simplify(.012)
    return rounded

def hardware(n,play=AXIAL_PLAY,length=SCREW_LENGTH):
    top=POC_SEAT+play+WASHER_T
    screw=union([mf.Manifold.cylinder(length,1.5,1.5,96).translate([0,0,top-length]),
        mf.Manifold.cylinder(3,3,3,96).translate([0,0,top])])
    w=mf.Manifold.cylinder(WASHER_T,WASHER_OD/2,WASHER_OD/2,192)-mf.Manifold.cylinder(WASHER_T,WASHER_ID/2,WASHER_ID/2,96)
    return xform(screw,frame(n)),xform(w,frame(n),n*(POC_SEAT+play))
