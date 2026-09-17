# Printing and assembling the compact Redi

## Hardware fit first

1. Print the three nut-fit blocks and the rotor coupon. Choose the tightest
   5.50 / 5.60 / 5.70 mm pocket that seats your nut fully without splitting PLA.
   Use the matching core; the default is 5.60 mm.
2. Insert a nut sideways under the coupon roof. Its metal bearing face points
   toward the screw; the nylon end points inward, toward the puzzle center.
3. Place the rotor over it, add a 9 × 1 mm washer, then fit an M3 × 20 screw.
   Check the washer sits flat and the rotor turns after a small screw backoff.

Drive the screw far enough to engage the nylon ring while watching the nut.
The nut must stay fixed while the screw advances and backs out. A nut that merely
stays in place during handling has not passed this torque check. Try several nuts;
one successful slot does not establish the fit of all eight differently oriented
slots in the core. These coupons check hardware and the bearing, not the whole
flange mechanism, and their print orientation does not reproduce every core slot.

## P1S / 0.4 mm nozzle / PLA

Start with 0.16 mm layers, four walls, and approximately 15–20% infill. These are
starting settings, not a tested Bambu profile. Use enough walls at the small
flanges to fill them solidly where practical. Keep the model at 100% scale.

E01–E12 are oriented with their inward radial vector pointing straight down
(−Z): the retaining feet face the bed and the outside shell is above them. Each
STL already has its lowest point at Z = 0; keep this orientation when importing
it rather than using automatic lay-on-face. C pieces retain their outside-face
print orientation, and the core remains on one axis flat. Use supports and a
brim as needed for your usual edge-printing setup.

Inspect support in the slicer and keep it out of the screw bores and nut slots.
Clean support scars and elephant foot, especially on bearing feet, flange rims,
and the closely spaced main faces. Deburr a tight clearance bore instead of
letting a screw cut threads into the rotating C piece.

Write each full ID, such as **E01**, on a sheltered inside patch with a Sharpie,
away from sliding and bearing surfaces. Use [NEIGHBORS.md](NEIGHBORS.md), the
plate maps, and `images/piece-identification.png`. The named assembled 3MF shows
the solved orientation. IDs are not engraved into the running surfaces.

## Nut loading

Press all eight nuts sideways into the core's open slots until their screw holes
line up with the core bores. The roofs stop outward extraction; the hexagonal
seats are intended to resist rotation and the small ribs aid handling retention.
The nylon ends face the puzzle center. Test each nut with a screw, then remove
those screws before positioning the exterior pieces.

**Known issue:** the owner reports that about half the installed nuts spin under
the screw's locking torque. Check every seat before enclosing the core. Do not
keep driving a screw against a spinning nut: it can wear the pocket further.
The planned core-only revision will keep the entrance easy to load and narrow
the final seat for a press fit using a blunt metal rod. It is **not included** in
this release; see [README.md](README.md#known-core-issue-nuts-can-spin).

Use a bare 2.5 mm hex key long enough to reach the heads. An approximately 80 mm
straight reach also accommodates the optional stand. The narrow access wells
are intended for the hex key, not the large tubular Phillips-bit holder used
on the earliest proof of concept.

## Whole-piece assembly

The order is **edges first, C pieces last**, the same assembly principle as
v4.2. Each C piece slides inward along its screw axis; no flange has to snap
through a closed retainer.

1. Support the core. Optionally screw the supplied stand onto the C01 axis with
   one washer and screw and place its base on the table.
2. Arrange E01–E12 around the core in their solved positions. Use your hands,
   removable low-tack tape on the outside faces, and temporary external support
   as needed. Floating edges will not stand in place unaided.
3. Slide C02–C08 into their positions. Drop one washer into each access well,
   then install its screw into the captive nut. Leave each bearing released.
4. Support the puzzle, remove the stand's screw and washer, and withdraw the
   stand straight outward along C01. Insert C01, then install its washer and
   screw. Without the stand, simply install all eight C pieces last.
5. Remove tape and external supports. Test all eight axes gently before
   scrambling. If a turn catches, inspect alignment and print burrs first.

The stand supports the core, not the loose edges. The provided assembly checks
include stand withdrawal and edge loading around it.

## Tune

Bring each screw to gentle bearing contact. Judge contact by resistance of the
rotating piece, since the nylon nut resists the screw before the bearing clamps.
Back off by approximately one fifth turn, then tune in smaller increments.
Do not crank a screw down against PLA. Track clearance remains even with the
bearing clamped; see [VALIDATION.md](VALIDATION.md) for measured pull travel.

The owner has built this revision and likes its feel apart from the nut seats.
Long-term wear, PLA settling, and measured torque remain uncharacterized.
