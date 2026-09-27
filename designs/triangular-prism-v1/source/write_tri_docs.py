"""Release instructions derived from the triangular-prism definitions."""
from conical_design import *
import sys
from physical_feedback import feedback_text
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
text='''# Wonky triangular prism · 70° · 64 mm

![Both sides of the delivered meshes](images/solved-two-sides.png)

A non-wavy, face-turning triangular-prism puzzle inside a rotated 64 mm cube. C01–C03 are the three equatorial axes: each turns 180°. C04 and C05 are the opposing poles: each turns 120°. The solved shape, including center orientation, replaces stickers.

This is a complete new puzzle. Its parts do not fit the 48 mm wavy version. It uses the successful 64 mm pentagonal prism's retention and hardware layout, adapted to five axes. The cone half-angle is 70°: triangular-prism corners first appear at about 63.435°, so copying the pentagonal prism's 60° angle would not produce this set of pieces. These are straight conical generating profiles; their intersections with flat cube faces are curved.

## Print

Print one of every STL in `stl/puzzle/`: **5 screwed centers, 3 vertical petals, 6 horizontal petals, 6 floating corners, and 1 core — 21 parts total.** The main plates are `centers-corners-core-01.3mf` and `petals-01.3mf` in `plates/`. Their objects retain the part IDs. They are geometry-only 3MFs: apply your printer and support settings. Alternate orientations, optional cores, fit coupons and the assembly stand are additional choices, not more required puzzle pieces.

For the P1S / 0.4 mm nozzle, use PLA at 100% scale, millimetres. Start with 0.16 mm layers, four walls, five top/bottom layers and 25–30% gyroid infill. Use six walls and 40% gyroid on the core, matching the successful pentagonal print. Automatic tree support on the build plate only is a suitable starting point; inspect the actual Bambu slice around every foot and retaining shoulder. Remove support and seam burrs carefully without sanding away the flat retaining lands. A brim up to 8 mm fits the supplied plate spacing. Parts with a small first-layer footprint need one.

V/H petals are oriented with their inward radial direction down, following the established print preference. Centers and corners use a broad exterior face down. The core rests on a real axle pad. `print-options/` contains individual alternative orientations if desired. `reference/DO-NOT-PRINT-solved.3mf` is an assembly reference only.

## Hardware

- **5 × DIN912 M3×20** socket-head screws, nominal head Ø5.5 × 3 mm.
- **5 × Ø9 × 1 mm washers**, with M3 clearance holes. Use the familiar 9 mm washers for this build; the stack is not set for the 7 × 0.5 mm washers.
- **5 × DIN985 M3 nuts**, nominal 5.5 mm across flats and 4 mm tall.
- A 2.5 mm hex key, blunt metal rod for seating nuts, and a marker for part IDs.

The core uses the well-tuned pentagonal pocket: 5.20 mm terminal width across flats, 5.85 mm entrance, 3 mm tight loading region and 3 mm taper, with 4.25 mm pocket height. Try `stl/fit-coupons/nut-fit-5.20.stl` with your actual nut first. If necessary, test 5.30 / 5.40 and choose the corresponding optional core; print only one core. Print angle and nut variation can affect this interference fit. Seat nuts fully, with their nylon rings toward the puzzle center, before assembly.

The screw bore is Ø3.6 mm and the washer well Ø9.6 mm. The spherical core radius is 21.2 mm; flat pads are at 19.6 mm and bearing feet at 19.7 mm. Washer seats are at 30.1 mm, 1.2 mm inward from the pentagonal version to contain the C03 screw head. With a 1 mm washer, the nominal M3×20 screw ends at 11.1 mm, 2.55 mm beyond the nut's inward face. No magnets, glue, hidden loose retainers, core tracks or split core are required.

## Assemble

Mark IDs inside every piece. Use `NEIGHBORS.md`, `images/assembly-map.png`, and the inside-facing `catalog-*.png` images to identify them. The render colors distinguish piece families; they are not required filament colors.

1. Clean supports and seat all five nuts in the core.
2. Optionally use `stl/optional/assembly-stand.stl` in place of C01, held with one of the five screws and washers. It holds the core while assembling; no extra permanent hardware is needed.
3. Place K01–K06 against the core in their solved positions. Hold this incomplete shell with your fingers or temporary tape.
4. Place V01–V03 and H01–H06 between them. Their internal shoulders overlap the corners' feet. The checked insertion path is straight inward along each part's radial direction, with the other petals already in their solved positions.
5. Insert C02–C05 and start their screws into the nuts. Keep the shell aligned and leave a little freedom while closing it.
6. Support the shell, withdraw the optional stand along C01's axis, and replace it with C01, reusing its screw and washer. Without a stand, install C01 last.
7. Adjust all five screws gradually and evenly. M3 coarse pitch is 0.5 mm/revolution: one fifth of a turn changes the setting by 0.10 mm. Aim for free movement with minimal play; the nylon nut's turning resistance is not a measure of bearing preload. Check full 180° side and 120° pole turns from correctly aligned positions.

No part needs to snap past a finished retaining lip. Assembly checks include the core, neighboring installed pieces, hardware, stand and its withdrawal. They establish sampled collision-free paths, not that an unfinished shell stands up unaided.

## Retention and fit

The previous small wavy triangle assembled, but its floating corners popped, including after enlargement. A blocked single rigid pull in CAD did not predict that physical behavior. This design therefore replaces that mechanism rather than scaling its STLs.

The internal cut uses a **closed stepped shoulder and neck**, following the pentagonal construction. Its flat land runs outward from transverse radius 7.2·tan(70°) = 19.78 mm to 26.5 mm at axial height 7.2 mm. The cylindrical wall rises to 9.0 mm, then returns to the cone at 9·tan(70°) = 24.73 mm. That gives 1.77 mm nominal undercut projection before clearances and rounding. The shoulder is enclosed within radius 28 mm, inside the 32 mm cube insphere. Screwed centers capture petals; petals capture corners.

Main conical faces use 0.03 mm total nominal separation. Hidden track cutters have an additional 0.40 mm expansion, tapering back to the body gap toward the exterior. Printed flanges and cutter clearances are separate. Internal convex edges use 0.60 mm easing on floating pieces / 0.45 mm on centers; radial dihedral ridges use R2 transverse circular fillets through the track region; exterior edges use 0.8 mm easing. Washer lands and flat bearing pads remain flat. Nearly no material is removed for the sampled assembly path; the useful shoulders are preserved.

The corners' three tiny terminal regions are explicitly trimmed after rounding, removing about 11.57 mm³ per corner. This eliminates thin webs that could otherwise slice into separate scraps. The broad retaining lobes remain, and capture is checked on the trimmed exports. The trim stays inside a 31 mm sphere and does not alter the visible cube surface; exact clipping planes are in `finish_conical.py` and `reports/terminal-trimming.json`.

{PHYSICAL_FEEDBACK} CAD motion and capture checks are separate evidence; `VALIDATION.md` states their coverage and limits.

## Contents

`manifest.json` records hashes and print-to-mechanism transforms. `images/` shows the actual delivered meshes. `reports/` contains measurements tied to the manifest hash. `source/BUILD.md` describes regeneration. Source and generated design files are MIT licensed.
'''
text=text.replace('{PHYSICAL_FEEDBACK}',feedback_text(DEST))
(DEST/'README.md').write_text(text)
lines=['# Piece neighbors','','These pieces share an exterior seam in the solved puzzle. Internal retaining contacts can include additional pieces. The axis IDs refer to screwed centers, not cube face names.','','| Piece | Turn axes containing it | Exterior neighbors |','|---|---|---|']
records=[]
for r in ROWS:
 sig=set(r['signature']);neighbors=[s['name'] for s in ROWS if len(sig.symmetric_difference(s['signature']))==1]
 rec=dict(name=r['name'],axes=[f'C{i+1:02}' for i in r['signature']],neighbors=neighbors);records.append(rec)
 lines.append('| '+r['name']+' | '+', '.join(rec['axes'])+' | '+', '.join(neighbors)+' |')
lines+=['','A side turn moves its C center, two V petals, two H petals and four K corners. A pole turn moves its C center, three H petals and three K corners.','', 'C01 = (1,0,0), C02 = (−1/2,√3/2,0), C03 = (−1/2,−√3/2,0), C04 = (0,0,1), C05 = (0,0,−1) in mechanism coordinates.']
(DEST/'NEIGHBORS.md').write_text('\n'.join(lines)+'\n');(DEST/'reference/neighbors.json').write_text(json.dumps(records,indent=2))
