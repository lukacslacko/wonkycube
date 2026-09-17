# Compact Wonky Redi — 64 mm v4.3

The **20-piece Redi-equivalent puzzle**, regenerated from the v4.2 construction
with a smaller mechanism, captive DIN985 nuts, 9 × 1 mm washers, and closer
conical faces. This is separate from the 65° puzzle: it has **eight C pieces,
twelve E pieces, and one core**, with no petals or dual centers.

The owner has printed and assembled this compact revision and reports that the
mechanism feels very nice, apart from the nut-seat issue below. This release
preserves the supplied radial-down print geometry without rebuilding its meshes.
The exported meshes also have computational checks; see [VALIDATION.md](VALIDATION.md).

![Solved compact cube](images/solved.png)

## Changes from v4.2

| Feature | This revision |
|---|---|
| Solved cube | 64 mm, down from 80 mm |
| Exterior orientation | Original optimized wonky orientation retained |
| Conical half-angle | 54.7356103°, the original Redi cut family |
| Main-face nominal gap | 0.03 mm total, down from 0.20 mm |
| Rail dimensions | Regenerated at 80% of the original linear dimensions |
| Flange-track allowance | 0.40 mm expansion of the **unrounded** flange sweep; not scaled down |
| Edge radial ridges | Constant 3 mm transverse rounding through the track region |
| Other inner lead-ins | 0.60 mm on edges; 0.45 mm on corners |
| Outer edge softening | 0.80 mm, applied before the R3 ridge cut, as in the v4.2 sequence |
| Screws | 8 × DIN912 M3 × 20, flat underside, 2.5 mm hex key |
| Washers | 8 × 9 mm OD × 1 mm thick, with M3 clearance hole |
| Nuts | 8 × DIN985 M3, nominal 5.5 mm across flats × 4 mm high |
| Rotating shank hole | Ø3.6 mm |
| Washer/access well | Ø9.6 mm |
| Core screw passage | Ø3.4 mm, through the core along each pair of opposite axes |

**Your 20 mm screws fit; shorter screws are not needed.** Their tips stop at an
8.30 mm radius from the puzzle center. The nominal nut's inner face is at
11.65 mm, so the screw extends 3.35 mm beyond it. The eight screw envelopes clear
one another and the printed core. That extra screw length occupies already
available space inside the core.

The core's rounded portions are spherical (radius 19.20 mm). Its eight bearing
flats are 17.60 mm from the center; one of these existing flats is the print bed
face. Side-loading nut pockets have a 1.95 mm retaining roof and small grip ribs,
using the same capture method as the 65° core. No inserts, glued caps, or separate
hidden retainers are used.

## Known core issue: nuts can spin

In the owner's build, about half of the nut seats are loose enough for a nut to
rotate while the screw is driven through its nylon locking ring. The retaining
roof captures the nut axially, but the current seat does not reliably react the
installation torque. The small grip ribs are not a proven torque lock.

The next change should affect **only the core**: retain the easy-loading slot
entrance, then narrow the final seating region around the screw bore, with a
short lead-in so a nut can be pushed firmly home using a blunt metal rod.
Preserve the nut depth, roof, screw alignment, core bearing flats and outer
envelope so the existing C and E pieces remain compatible. The final interference
must be selected by printing a coupon and driving a screw through the actual
locknut; insertion feel alone is insufficient.

**This is a pending improvement, not a change in these STL files.** The existing
5.50/5.60/5.70 mm core variants change the pocket width; they do not implement a
separately narrowed terminal seat and are not claimed to solve the reported issue.

## Size

At 64 mm, the bounding volume is 51.2% of the 80 mm cube's. Actual filament and
print time depend on walls, infill, orientation, and support. The size was chosen
to retain useful flange and bearing material while preserving the 3 mm rounding.
This is a checked compact size, not a claim of the smallest theoretically possible
mechanism.

![Hardware section](images/hardware-dimensions.png)

## Print orientation update

The twelve edge STLs and their print plate now have the inward radial direction
pointing down (−Z), with their lowest point on the bed. This is an orientation-only
update: piece shapes and dimensions are retained. All other STLs are unchanged.

## Files to use

- `stl/puzzle`: print C01–C08, E01–E12, and one core.
- `plates`: geometry-only 3MF print plates, with named objects; use
  [plate maps](plate-maps.html) to retain the IDs. Choose slicer settings yourself.
- `stl/fit-coupons`: three nut fits (5.50, 5.60, 5.70 mm) and a rotor for your
  actual screw/washer combination. Default `core.stl` uses the 5.60 mm pocket.
- `stl/optional`: alternate cores matching the other coupons, plus a removable
  screw-mounted assembly stand. Print only one core for the puzzle.
- `reference/DO-NOT-PRINT-assembled-cube.3mf`: named solved geometry for orientation.
- [NEIGHBORS.md](NEIGHBORS.md): the Redi part IDs and solved seam neighbors.
- [ASSEMBLY.md](ASSEMBLY.md): print, nut-loading, assembly, and adjustment guide.
- [VALIDATION.md](VALIDATION.md): checks performed and their limits.
- `source`: MIT-licensed CAD, canonical masters, and regeneration scripts.

The compact pieces **do not interchange with the 80 mm v4.2 parts or the 65°
prototype**. The C/E IDs retain their v4.2 Redi positions; the 65° list uses a
different edge ordering, so use this package's neighbor sheet.

## Adjustment

The bearing foot sits nominally 0.10 mm above its core flat. Tightening the screw
brings the foot toward the flat; backing off an M3 screw by one fifth turn (72°)
moves its head outward by 0.10 mm. Adjust gently by feel, rather than applying a
metal-fastener torque to plastic.

The close main faces reduce geometric slack. The intentionally wider tracks
still allow some edge movement, so screw tightening does not independently remove
all flange clearance. The checks measure geometry, not the exact hand feel or a
guaranteed “bind then release by 0.10 mm” setting. The 0.03 mm gap is below typical
FDM dimensional variation; remove support scars and burrs before forcing a turn.

MIT license, including models and CAD; see [LICENSE](LICENSE).
