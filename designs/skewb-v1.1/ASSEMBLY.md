# Printing, assembly and adjustment

## Fit coupons first

Print the three labeled nut-fit blocks (5.30, 5.40, 5.50 mm) and `rotor-fit`.
The label is in the filename/plate map, not engraved in a bearing surface. Mark
it immediately after removing it from the plate.

1. Slide a nut into a coupon's wide side entrance, metal bearing face toward the
   screw and nylon end toward the puzzle center. Press it fully into the narrowed
   seat with a blunt rod, keeping its bore aligned. Do not use the screw to pull a
   sideways nut into position.
2. Place the rotor coupon over the bore, drop in a 9 × 1 mm washer, and insert an
   M3 × 20 screw. Drive it through the nut's nylon ring and back it out several
   times. The nut must not turn in the pocket.
3. Choose the tightest fit that seats fully without splitting the plastic and
   passes the screw test. Default core: 5.40 mm. Alternatives: 5.30 and 5.50 mm.
   A nominal dimension is not a guarantee of fit for a particular nut or print.

Coupons check the hardware and flat bearing, not the complete puzzle. Their
orientation does not reproduce every tilted slot in the core. Check each of the
four core seats before enclosing the core. Test screws should be removed before
loading the floating pieces.

## P1S, 0.4 mm nozzle, PLA

Use your successful PLA settings as the baseline. A reasonable starting point
is 0.16 mm layers, four walls and 15–20% infill, keeping the small retainers solid
where practical. These are starting settings, not a validated slicer profile.
Keep the scale at 100%; scaling changes both hardware fit and running clearance.

- C01–C04 are placed on a broad exterior face. The core rests on the existing
  C01 bearing flat; no extra spherical portion was flattened for printing.
- The default F/K STLs are inward-radial-down. At 0.16 mm above the model's
  lowest point, an F piece has only about 0.6 mm² of section and a trimmed K piece about
  0.79 mm². **Do not rely on these tips alone for bed adhesion.** Inspect supports
  beneath the feet and a raft/brim strategy in your slicer before printing.
- The face-down 3MF alternatives offer broad bed contact. Use the F-face-down
  and K-face-down plates, or individual files in `print-options`. They preserve
  the same meshes under rigid rotation. Choose either these or the default
  inward-down versions, never two copies of the same ID.
- Inspect supports for undercuts in either orientation. Keep unwanted support
  out of nut slots and screw bores. Remove support scars and elephant foot from
  the rails, flat bearing lands and closely spaced main faces.

Use a clearance drill or careful deburring if a screw rubs inside a rotating
C piece. It must turn around the screw rather than grip its threads. Keep the
washer land flat and free of support debris.

Mark every full piece ID on a sheltered inside patch, away from sliding surfaces.
The [neighbor sheet](NEIGHBORS.md), [identification image](images/piece-identification.png)
and named solved 3MF identify placement. IDs belong to solved positions, not the
outer cube's visible geometric corners. The bed flat of the core is C01; use
[core-identification.png](images/core-identification.png) to match the other axes.

## Put the whole pieces together

The order is **K pieces → F pieces → screwed C pieces**. Each piece has a checked
straight insertion route along its radial direction; no retainer needs to snap
through another part. Loose parts need temporary external support during assembly.

1. Install and torque-test all four nuts in the core, then remove the test screws.
2. Optionally attach the stand at C01 using one washer and one screw. It supports
   the core, not the loose shell. A bare hex key with about 80 mm straight reach
   reaches the stand's screw. Place the stand's base on the table.
3. Position K01–K04 around the core in the solved orientations. Use your hands,
   low-tack tape on the outside, or other temporary external support.
4. Slide F01–F06 radially inward around them. The F feet capture the K feet.
   Check the solved seams against the named 3MF before adding screws.
5. Slide C02–C04 radially inward. Drop one washer into each access well and fit
   its screw into the captive nut. Leave the bearing released for adjustment.
6. Support the shell, remove the stand's screw/washer, and withdraw the stand
   straight outward along C01. Install C01, its washer and screw. Without the
   stand, simply install all four C pieces after the K and F pieces.
7. Remove temporary tape/supports. Check complete 120° turns about each of the
   four C axes while the other seams are aligned, then try mixed turns gently.

This order is intentionally reversible. For disassembly, remove the C pieces,
then F pieces, then K pieces. Hardware is standard; there is no glue, snap-through
assembly step, or permanently trapped extra plastic piece.

## Adjust the four axes

Bring a screw only to gentle bearing contact, judging resistance at the rotating
piece. Nyloc torque begins before the corner is clamped, so screw-driver torque
alone is not an indication of bearing contact. Start by backing off approximately
one fifth of a turn: M3 coarse pitch is 0.5 mm, so 72° corresponds to 0.10 mm of
axial head motion. Then tune in smaller increments.

The nominal bearing foot is 0.10 mm above its core flat in the assembly model.
The 0.03 mm main-face gap reduces slack, while the wider internal tracks retain
running clearance. Tightening the screws does not eliminate all floating-piece
play. The geometry is not a calibrated spring mechanism, and exact frictional
binding/release cannot be guaranteed from screw angle alone.

If a turn catches, first align the seams and look for burrs, support scars or a
rubbing bore. Do not force a jam or overtighten against PLA. The owner reports
successful printing and nice turning of the trimmed v1.1. Check hardware fit on
your own print; neither that report nor the geometry checks establish a measured
holding force, installation-torque rating or wear life.
