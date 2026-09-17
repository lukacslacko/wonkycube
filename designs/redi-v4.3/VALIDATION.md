# Validation — compact Redi v4.3, 64 mm

These checks use the **exported and reloaded print STLs**, restored to their
assembly coordinates. The owner reports a successful compact build and likes
the mechanism's feel, with the nut-seat failure described below. This is a
qualitative build report, not a torque or endurance measurement. The exact
slicer profile and a hash of the printer job were not recorded; optional core
variants, coupons and the stand are not individually claimed to be print-tested.

## Files and fit

- 28 STL files including optional alternatives and fit tools;
  all are single connected, watertight, consistently wound solids with positive volume.
- 7 geometry-only 3MF plates checked for units, valid triangle
  indices, non-overlapping object bounds, and the P1S's 256 mm build volume.
- E pieces point radially inward toward −Z, with their inner feet facing the
  bed. C pieces retain an outside face on the bed; the core uses an axis flat.
  Support and brim settings follow your preferred edge-printing setup.
- A 0.002 mm initial mesh simplification is followed by bounded export cleanup.
  Largest additional simplification recorded: 0.010000 mm. The largest
  cumulative recorded numerical-slit vertex-weld bound is 0.002027 mm.
  Small coincident/degenerate triangles are cleaned without filling finite holes.
  These are mesh tolerances, not printer accuracy guarantees.

## Motion and assembly

- All eight axes, 0–120° sampled every 3°: largest intersection 0.00000860 mm³.
- Twelve consecutive mixed-axis turns, sampled every 6° in each resulting
  configuration: largest intersection 0.00000860 mm³.
- Core, screws, and washers are included in the movement checks.
- All 20 exterior insertion paths: edges before C pieces, with same-family
  peers treated as already installed; 0.25 mm samples near engagement.
  Largest intersection 0.00000000 mm³.
- The optional stand clears edge-loading paths and withdraws along C01 before
  the final C piece is installed. Temporary external support is still needed.

The surfaces of revolution and explicit insertion relief supply the intended
kinematic construction. Sampling alone is not a continuous-motion proof.

## Retention

Every edge is obstructed by each of its two C retainers during a straight radial
pull. First sampled contacts lie between **0.50 and 0.50 mm**
at a 0.001 mm³ overlap threshold. The inner geometry alone is used, so these
tests do not credit exterior-face interference as flange capture.

The canonical edge also encounters obstruction along all 18
specified principal pulls, including C lifts of 0, 0.10, and 0.25 mm, and all
60 specified ramped rocking paths (±5°, ±10°, and zero).
These are geometric capture tests, not holding-force measurements. They do not
rule out every possible compound escape, elastic deformation, or multiple-piece
motion. They also show why tighter main-face gaps do not remove all track float.

## Rounding and distinct pieces

Both radial ridges of all twelve edges were sectioned through the inner tracks
and into the outer cone: 1440 sections on delivered STLs.
All sections agree with their nominal **3 mm** construction circles to within
0.0321 mm. On the 1152 sections with enough exposed arc
to resolve curvature, fitted radii range from 2.9745 to
3.0412 mm. Near track inflections some arcs shrink almost to a
point; those are checked against the known construction circle rather than an
ill-conditioned free radius fit. No inner radius taper is used.

All 66 pairs of edge exteriors remain distinct when compared in both proper
mounting orientations, using 1880 common radial sample
directions. The weakest pair's RMS difference is 3.024 mm.
Reflections count as different, as requested. This verifies sampled differences;
the original cube orientation is retained, not reoptimized, and arbitrary
forced insertion attempts are not part of this shape comparison.

## Hardware and adjustment

The nut insertion paths clear the core apart from the intentional grip ribs.
The pocket roofs obstruct outward nut extraction. Washer landing rings, bearing
feet, 1.2 mm washer-well collars near the seats, washer insertion paths, and a
bare 2.5 mm hex-key access envelope are checked. Screws and washers clear the
rotating pieces and core; all screw pairs clear each other.

The M3 × 20 screw tip is at radius 8.30 mm; the nominal nut's inner face is at
11.65 mm. The model gives 3.35 mm of screw beyond the nut, without requiring a
shorter screw. The bearing foot starts 0.10 mm above the core flat; an inward
translation to that flat is checked separately from extra clamping travel.

The physical build revealed a limitation not established by these collision
checks: about half of the nut seats allow the nut to spin under the DIN985
locknut's installation torque. The proposed correction is a narrower final seat
around the screw bore while retaining the wide entrance; it is **not yet
implemented or tested**. Geometric axial capture does not prove torsional grip.

Roof strength, measured turning torque, quantified corner cutting, wear, and
PLA settling remain uncharacterized. No guarantee is made
that every printer yields the same bind/release point. Machine-readable details
are in `reports/*.json`; file hashes are in `manifest.json` and `SHA256SUMS`.

## Print orientation revision

The E STLs were rigidly rotated and translated after the mechanism checks above.
All twelve inward directions are −Z and all lowest points are at Z = 0. Every
triangle is retained; the largest inverse-transform coordinate difference from
the previously checked geometry is 0.00000204 mm
(binary STL roundoff). All twelve reloaded files remain single, watertight solids.
The other STL files and the solved reference assembly are byte-identical. Motion,
retention, hardware, and radius reports are retained from that equivalent geometry;
the new orientation and print plates are checked separately. See
`reports/edge-print-orientation.json` and `reports/plates.json`.

## Public release provenance

V4.3 publishes the local `wonky-redi-64mm-v4p3-radial-down` export. All 28 STLs,
seven print plates, canonical masters, reference geometry and existing numerical
reports are byte-identical to that delivery. Publication updates the documentation,
release metadata and source text/formatting; it does not regenerate the mechanism.
See `publication.json` for the original bundle hash and the unchanged file hashes.
