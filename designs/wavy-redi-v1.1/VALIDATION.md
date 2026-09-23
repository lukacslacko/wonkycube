# Validation of the delivered print files

All eight validation jobs completed successfully. Each job reloaded the
delivered STLs, checked their hashes and restored their assembly coordinates.
These results apply to the files listed in `manifest.json`.

| Check | Result |
|---|---|
| Printed puzzle solids | 21 closed, consistently wound, single-component meshes |
| Turns | 944 sampled positions over all 8 axes and a 12-move scramble |
| Worst measured turning intersection | 7.16567e-06 mm³; acceptance threshold 0.003 mm³ |
| Assembly | 760 sampled group-loading positions; all passed |
| Capture | All 12 petals blocked under radial pull; inner shoulder checked with up to 0.10 mm axial-piece lift and ±10° rocking |
| Core-root minimum inscribed diameter | 3.38 mm |
| Area at that section | 11.59 mm² |
| Radial-edge fillet | R2 mm across 1023 fitted sections, including the inner track region |
| Extrusion-width connectivity | 0.42 mm line, 0.16 mm layers; total small disconnected estimate 0 mm³ |
| Hardware | Screw, washer and driver paths, complete washer lands and bearing feet, nut-entry gauge and screw engagement checked |
| Cube tips | All eight checked; maximum distance to an intentionally rounded tip 0.627 mm |
| Plates | Within 256 × 256 mm bounds, with nonoverlapping part bounding boxes |

## Why the assembly path works

The hidden profile has nondecreasing distance from the turn axis: the
cutting body is open outward along that axis. Translating a group of all
remaining pieces belonging to that cut keeps the group inside the same
cutting body. The other printed pieces are outside it. Rounding and track
relief remove material and preserve this property. The specific loading
checks additionally include the hub, bearing feet, fitted screws and STL
tessellation. Reverse the recorded removal order to obtain the illustrated
assembly sequence. This does not rely on snapping parts through one another.

## What the checks do not establish

The original v1 was printed and reported to build and turn very well. The
v1.1 nut-seat and exterior-tip changes have not yet been physically tested.
Collision sampling is not a continuous
physical simulation, and capture tests cover the listed pull/rock paths,
not every possible forced extraction. The section-width test is a geometric
approximation, not Bambu Studio toolpaths; supports are still required.
The core-root measurement is a geometric thickness check, not a load or
fatigue rating. Friction, PLA surface finish, support removal and screw
tension need feedback from the actual print.

The 5.25 mm nut seat intentionally interferes with a nominal 5.5 mm nut.
This reduces the slight over-tightness reported for the v1 wavy print. A 5.15 mm
gauge checks the entry path; a rigid collision test cannot predict the
force needed to press the real nut into the plastic.
