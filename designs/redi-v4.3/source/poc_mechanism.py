"""Direct-screw, flat-foot revision of the Rotated Redi prototype (millimetres)."""
from mechanism import *

PILOT_D = 2.6
SCREW_BORE_D = 3.4
ACCESS_D = 13.8
POC_SEAT = 34.0
FOOT_R = 5.2
FOOT_TOP = 27.0
WASHER_OD = 13.0
WASHER_ID = 3.2  # conservative nominal envelope; actual washer must pass the screw
WASHER_T = 0.55
AXIAL_PLAY = 0.20
SCREW_LENGTH = 20.0
SCREW_TOP = POC_SEAT + AXIAL_PLAY + WASHER_T
SCREW_TIP = SCREW_TOP - SCREW_LENGTH

def poc_core(pilot=PILOT_D, segments=288, print_flat=True):
    s = mf.Manifold.sphere(CORE_R, segments)
    if print_flat:
        s = s.trim_by_plane([0, 0, 1], -20)
    for n in AXES:
        s = s.trim_by_plane(-n, -CORE_PAD)
    # Four complete, intersecting diagonals provide all eight through pilots.
    for n in AXES[:4]:
        hole = mf.Manifold.cylinder(80, pilot/2, pilot/2, 96).translate([0,0,-40])
        s -= xform(hole, frame(n))
    for n in AXES:
        lead = mf.Manifold.cylinder(.3, pilot/2, pilot/2+.3, 96).translate([0,0,CORE_PAD-.3])
        s -= xform(lead, frame(n))
    return s

def poc_corners(corners):
    result=[]
    for s,n in zip(corners,AXES):
        f=frame(n)
        # This small, axisymmetric foot stays inside the original turning
        # corridor. Its annular underside rests directly on the flat core pad.
        foot=mf.Manifold.cylinder(FOOT_TOP-CORE_PAD, FOOT_R, FOOT_R, 192).translate([0,0,CORE_PAD])
        bore=mf.Manifold.cylinder(150, SCREW_BORE_D/2, SCREW_BORE_D/2, 128)
        access=mf.Manifold.cylinder(150, ACCESS_D/2, ACCESS_D/2, 192).translate([0,0,POC_SEAT])
        result.append((s+xform(foot,f))-xform(union([bore,access]),f))
    return result

def hardware(n,play=AXIAL_PLAY,length=SCREW_LENGTH):
    top=POC_SEAT+play+WASHER_T
    screw=union([
        mf.Manifold.cylinder(length,1.5,1.5,96).translate([0,0,top-length]),
        mf.Manifold.cylinder(3,3,3,96).translate([0,0,top])
    ])
    washer=mf.Manifold.cylinder(WASHER_T,WASHER_OD/2,WASHER_OD/2,192)-mf.Manifold.cylinder(WASHER_T,WASHER_ID/2,WASHER_ID/2,96)
    return xform(screw,frame(n)),xform(washer,frame(n),n*(POC_SEAT+play))
