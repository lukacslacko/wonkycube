# Mechanism and reusable design choices

## Floating-corner printability correction in v1.1

Three clipping chords at 9.5 mm from the floating corner axis remove the
perforated inner flange corners below axial distance 22 mm. The actual removed
material lies within radius 22.262 mm of the puzzle center. The three small holes
are opened to the perimeter, eliminating their spindly terminal loops. The larger
retaining lobes between the cuts remain. About 143.765 mm³ is removed per K piece.

Apply this trim **after** the original insertion reliefs and rounding. Continue
using the original, untrimmed K geometry when generating F/C insertion clearances;
this keeps the previous mating parts compatible. `corner_tip_trim.py` implements
the final subtraction. No material is added to close a hole or reduce clearance.

A connected CAD solid is insufficient evidence that a feature will print as one
part. Intersect the mesh with print layers, remove contours too narrow for the
intended extrusion width, and check connectivity between the remaining layer
regions. Here that check reproduces the old tip islands and eliminates them in
the revision. It supplements mesh integrity and retention checks; it is not a
replacement for a slicer's toolpaths or for testing a physical print.

## Four plane cuts with internal retaining steps

Take the tetrahedral unit axes proportional to (−1,−1,+1), (−1,+1,−1),
(+1,−1,−1) and (+1,+1,+1). A piece belongs to the positive side of one, two or
three cuts: these signatures identify the C, F and K families respectively.
The four axes sum to zero, so no finite-volume outside piece has zero or four
positive signs. A 120° turn about one axis permutes the other three axes.

Far from the center the interfaces are planes through the puzzle center. Near
the center, each plane is replaced by the same **surface of revolution about its
turn axis**. This is why the rails can pass through intermediate angles: both
sides see the same axisymmetric interface, rather than relying only on fit at
0° and 120°. Intersections of the four volumes define the interlocking pieces.
The exterior cube is clipped afterward using the existing wonky rotation.

In a meridional section, the nominal positive cut boundary follows these points
in cylindrical coordinates (rho, z), in millimeters:

```
(0,0) → (18.2,0) → (18.2,-3.5) → (22,-3.5)
      → (22,+3.5) → (25.5,+3.5) → (25.5,0) → outside
```

The opposing radial shoulders create an undercut. They provide positive capture
rather than relying on friction or on a shallow taper that lets a piece cam out.
The core cavity radius is 19.70 mm. The rounded core radius is 19.20 mm, with
four true bearing flats. A flat annular foot on each C piece bears on its flat.
A shoulder screw is unnecessary: the screw is a retaining/tensioning fastener,
the Ø3.6 mm bore gives shank clearance, and the flat foot supplies the bearing.

F feet are retained under two C neighbors. K feet are retained under three F
neighbors. Those relationships also dictate assembly: carve clearance for the
actual K insertion sweep into F, and for F/K insertion sweeps into C. The sweep
uses individual upper-facing mesh triangles and a 0.05 mm axial allowance;
it does not convex-fill nonconvex recesses. Only feet within radius 28 mm take
part in this relief. Then verify an explicit insertion route for every full
piece, including the final corner and the removable stand.

## Separate body gap, running clearance, rounding and preload

The nominal main-face gap is 0.03 mm total, split about the cut. Internal receiving
tracks receive an additional 0.40 mm offset from the **unrounded** rotational
profile. This wider allowance tapers back to the main-face gap between cylindrical
radii 26.5 and 29 mm. The moving profile gets 0.60 mm convex lead-ins and the
receiving profile 0.45 mm relief. Rounding the solid flange must not shrink its
clearance cutter; otherwise a rounded protrusion still meets a narrow throat.

The 3 mm radial fillets use transverse circular arcs, with adaptive stations
through the stepped region. The radius stays constant while the circle center
and exposed arc change with the local profile. This avoids shrinking the fillet
at the innermost track region. It is a transverse R3 construction, not a claim
that the whole surface is a sphere or that every groove intersection has a
3 mm blend in every direction. Outside edges have separate 0.80 mm softening.

Retention shoulders need material behind them after all rounding and insertion
relief. Their strength cannot be inferred merely from a watertight mesh or from
one obstructed pull direction. Check multiple pulling/rocking directions, lifted
corners, actual print orientation and a physical build. Leave some running
clearance at the shoulders even when the main faces are close.

Screw preload controls bearing restraint; it does not independently remove track
clearance. Keep the shank from gripping the rotor. Keep the washer seated on a
broad flat land and separate installation torque retention from axial nut capture.

## Nut loading is different from nut torque retention

The Redi's wide seats allowed some DIN985 nuts to spin. Here the side entrance is
5.85 mm wide, tapering over 2.5 mm into a 5.40 mm-wide terminal region extending
3.5 mm outward from the bore. The rear half of a hexagonal pocket locates the nut.
The slot is 4.25 mm high for a nominal 4 mm nut, with its roof at radius 15.65 mm.
The 1.95 mm roof captures the nut beneath the 17.60 mm bearing flat.

A wide entrance and narrow seat serve different jobs. The first permits loading;
the second reacts screw torque. Printed interference and an accessible pressing
route make assembly practical. Verify with the actual locking screw driven through
the nylon ring, including all differently oriented slots. Keep seat-width variants
as core-only choices so a fit change does not require reprinting the shell.

## Reuse dimensions thoughtfully

The 64 mm outer size and hardware stack are copied from the compact Redi. The
Skewb bearing foot radius is 3.10 mm rather than 3.20 mm: the extra 0.10 mm relief
avoids a small contact with a passing piece at the deeper cuts. The rail topology
and assembly hierarchy are new, not scaled Redi internals. Reuse learned
clearances and rounding independently of the decorative outer scale.

Mirrors remain distinct, as requested. Sampled exterior comparisons distinguish
every pair within each interchangeable family under its proper mounting rotations.
The old Redi rotation is reused; this is not a claim of an optimal Skewb orientation.

Geometry and computational checks are original for this project. Background on
Skewb piece behavior: [Jaap's puzzle page](https://www.jaapsch.net/puzzles/skewb.htm)
and [Kevin Gittemeier's Skewb tutorial](https://www.kevingittemeier.com/skewb-tutorial-bm/).
