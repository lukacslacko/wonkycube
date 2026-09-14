# Designing printed mechanisms that retain well and move freely

These lessons came from printing and revising a corner-turning puzzle. They apply more broadly to captive sliders, rotating shells and mechanisms with intersecting motion paths. The [design reference](design.md) records the particular dimensions used here; the principles below explain how to choose and evaluate such dimensions elsewhere.

The successful behavior comes from a combination of features. The print trials changed several features between revisions, so they do not isolate a measured contribution from each radius or clearance.

## 1. Give retention, guidance and fastening separate jobs

A useful interface has an explicit answer to each of these questions:

| Job | Geometric feature | Failure when confused with another job |
|---|---|---|
| Locate an axis | Journal/bore and bearing foot | Wobble or off-axis rubbing |
| Support inward force | Flat annular bearing pad | Screw has to carry bending that a bearing could support |
| Limit outward movement | Washer, screw and seat | Loose adjustment becomes separation |
| Retain a sliding piece | Overlapping shoulder with a useful flat land | A sloped lip becomes an escape ramp |
| Permit intended motion | Swept track with positive allowance | Local interference despite an apparently generous gap elsewhere |
| Help entry under small misalignment | Rounded ends and ridges | A sharp tip meets a sharp track mouth |

In this puzzle, the core's curved envelope is spherical between its axle pads, but the corners rotate on **matching flat feet and pads**. A spherical-looking core does not imply that the corner's concave underside is its bearing. The support geometry must match where contact actually occurs.

The screw is stationary in the core; the corner clears its shank. Its washer limits outward movement, while a small adjustment gap prevents the screw from clamping the rotor onto its bearing.

## 2. Positive capture depends on direction, not just flange size

Start with the direction in which an unwanted piece could leave. The retainer must intersect that path with meaningful material remaining after all track and assembly cuts.

A broad sloping flange can still let a piece cam outward. A flatter shoulder presents a more direct obstruction. In the working design, a stepped surface of revolution replaces the early conical flare. Its constant-axis-coordinate shoulder leaves a flat land; the two adjacent corner retainers cooperate to capture an edge.

![Actual stepped retaining shoulder](images/retaining-shoulder-v3.png)

Increasing flange projection alone is insufficient: a larger flange also needs a larger swept passage past neighboring structures. Enlarging that passage can remove the very land that was supposed to retain it. Design the flange and its neighboring passages together, then inspect the *remaining* overlap.

Keep entrance radii local enough to preserve a substantial load-bearing land. A perfectly rounded nub can be easy to turn and easy to pull out. Recheck retention whenever rounding or track widening removes material near the capture surface.

Do more than a straight radial pull test. Include tilted pieces, lifted retainers and intermediate turn positions. An early print escaped by motions that a simple aligned test did not adequately characterize.

## 3. Derive clearance from the mating part's motion

For a moving solid F and motion transforms T(t), its occupied envelope is

`S = union over t of T(t) F`.

A useful starting groove is that envelope expanded by a distance allowance c: `S ⊕ ball(c)`. The actual construction may use a two-dimensional profile and revolution when the motion permits it. The essential point is to preserve the swept solid's concavities and account for approximation error.

For this design, the flange is projected into `(rho, z)` coordinates about the relevant axis, its profile is expanded, and the result is revolved. Sampling the triangle interiors matters: rotating only the mesh vertices can miss the inner radial bound of a face.

Use the **unrounded mating flange** to create the track cutter, expand that cutter, and round the printed flange separately. Otherwise, a smaller rounded flange can produce a narrower groove, cancelling part of the intended entry relief.

![Actual sections before and after wider tracks and internal rounding](images/track-section-v4.png)

A whole-object convex hull is often too aggressive for a retaining mechanism. It fills useful concavities and may erase the lock. Assembly clearances need the same care as turning clearances: use the real insertion sweep, not an arbitrary oversized cavity.

## 4. Treat clearance as several independent dimensions

There is no single tolerance that controls a mechanism's feel. Distinguish at least:

- Sliding separation between the main surfaces.
- Extra clearance inside tracks and at their mouths.
- Axial movement allowed by the fastener.
- Diametral clearance around a rotating screw shank.
- Interference in a screw pilot that must grip plastic.
- Access clearance for the actual washer and driver holder.

Name whether a value is **per wall, total separation, radial or diametral**. An offset applied to the entire swept profile moves every profile boundary by that distance; it is not the same as a diametral hole allowance.

Here, the outer interfaces use 0.20 mm nominal separation, while the track cutter has a 0.40 mm distance allowance from the old unrounded flange. Local relief can be larger. The washer adjustment allows approximately 0.10 mm axial freedom. These numbers describe different contacts and should not be added into a single “puzzle gap.”

Reducing every gap toward zero may reduce wobble but increase binding. Negative clearance plus a loose screw is especially hard to control: loosening moves one retainer along one axis; it does not open all intersecting tracks uniformly. Excessive lift also reduces capture and permits rocking.

Use print coupons to calibrate holes and short comparison parts to calibrate motion. A nominal CAD allowance is not a promise of the as-printed gap.

## 5. Round the entire contact path, including its transitions

A rounded ridge helps an approaching surface slide past or guide it toward alignment instead of presenting a knife edge. Whether it actually realigns depends on freedom of movement, friction and the applied force; a fillet alone does not guarantee corner cutting.

Two different rounding operations proved useful:

- Small radii on internal protrusions and track entrances remove local snag points while preserving flat lands.
- Larger radii on the long radial dihedral ridges relieve contacts as the turn changes from one axis to another.

The radius must continue through the part of the ridge that enters the track. Protecting an entire inner zone preserved its smaller radius, leaving a catch-prone transition even though the visible outer ridge looked rounded.

The final intent is a **3 mm circular radius in sections transverse to each radial ridge**. That is a precise construction, not a claim that every principal curvature of a three-dimensional fillet is 3 mm. The circle center follows the stepped track profile; it does not simply extend the outer cone inward. Different opening angles can make equal radii look different.

Some track sections contain a thin foreground rib, then a void, then the main body. Fitting to the first boundary can put the rounding cutter into the void and leave a smaller-radius strip behind. Determine the actual solid interval that must survive, then verify the exported mesh in sections. A parameter labelled “3 mm” is not evidence that the print file has that radius everywhere.

![Equal 3 mm radius in actual transverse sections through the track and outer ridge](../models/current/reference/constant-radius-v4p2.png)

## 6. Preserve the useful constraints when making compatibility revisions

Holding the main dimensions fixed makes physical experiments informative. Keep axes, bearing heights, fastener seats, exterior face planes and part IDs stable while changing a particular sliding feature.

A subtract-only revision has a valuable ideal-geometry property: if each new part is a subset of its old part, it cannot create a new collision at the same rigid poses. This supports mixing old and new parts. It does **not** prove unchanged strength, retention, available grip or self-alignment. Removing material can worsen all of those.

Protect the exact bearing foot and washer collar rather than broadly protecting every internal surface. Broad protection can accidentally leave the sharp transition the revision was intended to remove. Check motion, material left at the lands, and assembly access separately.

## 7. Size the exterior around a mechanically adequate interior

Set the fastener, bearing, retaining and access dimensions first. Then make the decorative or puzzle exterior large enough to contain those features with adequate walls in every direction.

The exterior need not be as large as the first prototype. Reducing this puzzle from 100 to 80 mm kept the 24 mm core radius and brought the grip closer to the interfaces. This is a useful ergonomic and shell-size change, not a measured optimum or a proof that a smaller cube would work.

Do not shrink a finished STL uniformly to achieve that result. Uniform scaling also shrinks screw holes, washer wells, lands and gaps. Change the outer envelope independently and regenerate/check the affected intersections.

An asymmetric shell can expose thin spots that a symmetric prototype hides. Inspect the least favorable rotated direction, not just a central section.

## 8. Design the assembly path at the same time as the motion

Closed-loop retention is only useful if there is an assembly sequence. Model the swept volume of each insertion, the driver and washer access, and the withdrawal of any assembly jig.

This mechanism is assembled by placing the edges around the core before installing the corner retainers. Corners slide along their axes and are screwed from outside. One corner corridor stays empty until the stand is withdrawn. Nothing needs to pass through an already installed flange.

A fastener can be visible yet unreachable by the actual tool: include the tubular bit holder, not just the Phillips tip. Likewise, a jig that supports the first step can be trapped by the last step. Explicitly reserve and verify its exit route.

## 9. Separate ideal geometry from printed behavior

Use a ladder of evidence:

1. Validate the delivered files: closed, connected, consistently wound meshes and correct scale.
2. Check aligned fit and sampled intended turns with hardware present.
3. Check insertion, tool access and jig withdrawal.
4. Probe escape paths and small misalignment, especially after material removal.
5. Print a coupon/fixture or a few interchangeable parts.
6. Test the full mechanism and record the exact file hashes, material and settings.

Finite collision samples do not prove clearance at every possible pose. Intersection volume does not measure hand torque. A blocked rigid extraction path does not establish a holding-force rating or resistance to elastic popping.

Layer steps, supports, seams, elephant foot, washer burrs and screw tension can dominate small nominal clearances. Clean raised residue from sliding surfaces while preserving the retaining lands. Keep material and settings unchanged when comparing geometry; test a new polymer as a separate experiment. There is no measured PLA-versus-ABS friction ranking for this puzzle.

Numerical export deserves its own checks. Very small Boolean slivers can collapse when STL coordinates become float32. Controlled simplification and welding must still yield a closed mesh; then inspect the actual fillet sections. On steep profiles, a small normal-distance simplification error can become a larger transverse section error.

## A practical diagnosis table

| Symptom | Inspect first | Design response to evaluate |
|---|---|---|
| Pulls out while aligned | Remaining capture land and escape direction | More positive shoulder; avoid a ramp |
| Pops only when turning | Intermediate overlap, rocking and retainer lift | Rework intersecting paths; reduce excess axial play |
| Drags throughout a turn | Bearing pressure, track allowance, support residue | Separate fastening friction from sliding interference |
| Catches when changing axes | Ridge/track-mouth contact and transition bands | Continuous local rounding; expanded unrounded sweep |
| Turns freely but feels unstable | Axial and diametral freedom | Tighten the appropriate constraint without closing every gap |
| CAD passes but print catches | Seams, supports, first-layer lip, dimensions | Calibrate and finish before changing the whole mechanism |

The reusable rule is to preserve firm constraints in unwanted directions while making the intended paths forgiving. Capture lands, bearings, clearances and rounded entrances cooperate; none can substitute for all the others.
