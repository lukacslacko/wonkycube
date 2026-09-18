"""Package only checked delivery files, documentation, source and hashes."""
from skewb_design import *
import shutil,hashlib,sys,zipfile,datetime
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else WORK/'wonky-skewb-64mm-v1p1'
manifest=json.loads((SRC/'manifest.json').read_text())
for r in manifest['parts']:
 assert hashlib.sha256((SRC/r['file']).read_bytes()).hexdigest()==r['sha256']
for mode in ['motion','assembly','hardware','retention','plates']:
 assert json.loads((SRC/'reports'/(mode+'.json')).read_text())['_completion']['passed']
for name in ['ridge-radii','shape-distinction','export-surface','tip-revision']:
 assert json.loads((SRC/'reports'/(name+'.json')).read_text())['passed']
if SRC.resolve()!=DEST.resolve():shutil.copytree(SRC,DEST,dirs_exist_ok=True)
source=DEST/'source';source.mkdir(exist_ok=True)
files=['skewb_design.py','corner_tip_trim.py','section_connectivity.py','check_tip_revision.py','render_tip_comparison.py','ridge_rounding.py','finish_skewb.py','export_skewb.py','validate_skewb.py','check_ridges_shapes.py','check_export_surface.py','mesh_io.py','mesh_render.py','print_3mf.py','render_skewb.py','build.py','package_release.py','physical-feedback.json','requirements.txt','chosen_rotation.json','LICENSE']
for name in files:
 if (HERE/name).resolve()!=(source/name).resolve():shutil.copy2(HERE/name,source/name)
shutil.copy2(HERE/'LICENSE',DEST/'LICENSE')

feedback=json.loads((HERE/'physical-feedback.json').read_text())
expected=feedback['delivered_stl_sha256']
actual={p.relative_to(DEST).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.rglob('*.stl')}
feedback_matches=actual==expected
shutil.copy2(HERE/'physical-feedback.json',DEST/'physical-feedback.json')
physical_status=(
    '**Owner-tested v1.1:** on 2026-09-18 the owner reported that the trimmed Skewb '
    'printed very well and turns very nicely. The STL hashes match the delivered '
    'revision associated with that report.' if feedback_matches else
    '**Generated build:** its STL hashes differ from the owner-tested v1.1 export. '
    'The original trimmed v1.1 received a successful print and turning report on '
    '2026-09-18; that report does not validate this regenerated variant.'
)
def write(name,content):
 (DEST/name).write_text(content.replace('{{PHYSICAL_STATUS}}',physical_status).strip()+'\n')
write('README.md',r'''
# Wonky Skewb — 64 mm v1.1

A Skewb shape mod adapted from the successful compact Wonky Redi v4.3: the same
64 mm outer cube, exterior rotation, M3 hardware stack, close main faces, generous
internal track allowance and rounded radial ridges.

{{PHYSICAL_STATUS}} See [physical-feedback.json](physical-feedback.json) for the
report, its scope and the supplied file hashes. This is qualitative owner feedback;
holding force, turn torque and long-term wear were not measured.

![Solved and exploded](images/overview.png)

There are **14 shell pieces and one core**: four screwed corners C01–C04, six
floating face pieces F01–F06 and four floating corners K01–K04. The core has four
axes in a tetrahedral arrangement. A 120° turn carries one screwed corner, three
F pieces and three K pieces. The other three screwed corners remain on the core.
The outside cuts are central planes, so their intersections with the cube are
straight. Only the hidden retaining regions depart from those planes.

## v1.1: floating-corner flange tips removed

K01–K04 have the three thin, perforated flange corners explicitly trimmed away.
The broad retaining lobes remain. The v1 slicer issue arose because the nominally
connected tips had webs too thin to form extrusion paths. This revision removes
them from the CAD, instead of relying on slicer repair or adding supports to waste
material on isolated fragments.

Only the four K parts need replacing. All other STL files match v1 byte for byte.
The outside shape, part IDs, assembly order, hardware and main running clearances
are retained. See [TIP-REVISION.md](TIP-REVISION.md) for the change and its checks.

![Floating-corner revision](images/tip-comparison.png)

## What is retained from your last print

| Feature | Skewb v1.1 |
|---|---|
| Nominal cube side | 64 mm |
| Exterior rotation | Same orientation as the compact Redi; not reoptimized |
| Main planar-face gap | 0.03 mm total |
| Extra internal track allowance | 0.40 mm on the receiving side of the rotational profile |
| Radial dihedral rounding | Nominal R3 transverse circles, continuing through the tracks |
| Other inner lead-ins | 0.60 mm on the positive cut profile; 0.45 mm on its receiver |
| Exterior edge softening | 0.80 mm |
| Spherical core radius | 19.20 mm; bearing flats at 17.60 mm |
| Rotating screw bore | Ø3.6 mm |
| Washer/access well | Ø9.6 mm |
| Washer seat | 27.30 mm from the center along each screw axis |
| Corner bearing foot | Flat annulus, Ø6.2 mm outside, starting at radius 17.70 mm |

The retaining geometry is new for the Skewb. F pieces hook under the screwed
corners; K pieces hook under the F pieces. The side-loading reliefs allow assembly
in that same order reversed: **K → F → C**. All retaining feet are integral with
the shell pieces. There are no glued caps or separate hidden plastic carriers.

## Hardware and improved nut pockets

Use **four each** of your DIN912 M3 × 20 screws, M3 washers of **9 mm OD × 1 mm**,
and DIN985 M3 locknuts. A bare 2.5 mm hex key reaches the screw heads. Your 20 mm
screws fit: their tips reach radius 8.30 mm, 3.35 mm beyond the nut's nominal inner
face, and the four screws clear one another.

The core implements the requested narrowed nut seat. The loading mouth stays
**5.85 mm wide**, with a taper to a **5.40 mm final seat across flats** around the
bore. A nominal 5.5 mm nut therefore has 0.10 mm total interference at the seat.
A blunt Ø3 mm rod has a checked sideways pressing path. The slot roof captures
the nut axially; the close parallel flats and back of the hex seat resist rotation.

Check the press fit with your actual nuts and print. Three
fit coupons and matching 5.30 / 5.40 / 5.50 mm core seats are included. The default
`core.stl` is 5.40 mm. **Drive a screw through the nylon ring in the coupon:** an
insertion fit alone does not establish resistance to installation torque. Test
all four seats in the actual core before assembling the puzzle.

![Hardware and nut pocket](images/hardware.png)

## Files and first print

1. Print the nut-fit coupons and rotor from `plates/fit-coupons-01.3mf`.
2. Choose one core matching the tightest coupon that seats without cracking and
   holds the nut under screw torque. Print C01–C04, F01–F06 and K01–K04 once each.
3. Follow [ASSEMBLY.md](ASSEMBLY.md), marking IDs using [NEIGHBORS.md](NEIGHBORS.md).

The STLs in `stl/puzzle` have F/K pieces pointing inward toward the print bed,
following your successful Redi orientation. Skewb tips are much smaller, so they
need support and careful bed adhesion in this orientation. **Face-down 3MF
alternatives** are supplied in `print-options` and the two `*-face-down` plates;
these have a broad exterior face on the bed and use exactly the same geometry.
Choose one orientation per piece, not both. The face-down files are a useful
starting option for a first Skewb build, especially K01–K04. The owner did not
restate the chosen orientation or detailed slicer settings in the success report.

All 3MFs are geometry only, without printer settings. Print at 100% scale; inspect
support placement in the slicer. The named reference `DO-NOT-PRINT-solved.3mf`
shows the solved assembly; it is not a print-in-place model. Plate maps and
identification images are included.

The optional assembly stand uses one of the four screws temporarily. The parts
are not interchangeable with the Redi or the 65° prototype, despite the shared
size and hardware. The Redi source and release are unchanged.

Read [DESIGN.md](DESIGN.md) for the mechanism, [VALIDATION.md](VALIDATION.md) for
checks and limits, and [source/README.md](source/README.md) to regenerate it.
MIT license covers the models, documentation and code; see [LICENSE](LICENSE).
''')
write('ASSEMBLY.md',r'''
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
''')

neighbors={}
for r in ROWS:
 neighbors[r['name']]=[s['name'] for s in ROWS if len(set(r['signature'])^set(s['signature']))==1]
rows=['# Solved neighbors — Wonky Skewb v1.1','','Mark each full ID on the inside, away from running surfaces. Tick after printing and marking. These are exterior seam neighbors, excluding point contacts; order is not clockwise. Use this Skewb list, not the Redi or 65° list.','','| Marked | Piece | Family | Solved seam neighbors |','|---|---|---|---|']
for r in ROWS:rows.append('| ☐ | '+r['name']+' | '+{'C':'Screwed corner','F':'Face piece','K':'Floating corner'}[r['family']]+' | '+', '.join(neighbors[r['name']])+' |')
rows+=['','Assembly order: **K → F → C**. Every F is held by its two C neighbors; every K by its three F neighbors. The four C pieces screw to the core.','','![Solved placement](images/piece-identification.png)','','## Which pieces move in each turn?','','A positive 120° turn uses the right-hand rule around the named C axis, pointing outward from the core. Each row lists the seven carried pieces.','','| Axis | Pieces carried from the solved state |','|---|---|']
for i in range(4):rows.append('| C'+str(i+1).zfill(2)+' | '+', '.join(r['name'] for r in ROWS if i in r['signature'])+' |')
write('NEIGHBORS.md','\n'.join(rows))
write('TIP-REVISION.md',r'''
# v1.1 — replace only the four floating corners

The three perforated flange tips on each K piece are explicitly removed. Their
very thin webs could disappear during slicing while leaving isolated little tip
fragments that attracted support. A watertight CAD mesh did not prevent that.

![Before and after](images/tip-comparison.png)

## Files to replace

Print **K01, K02, K03 and K04** from this revision. Their IDs and solved positions
are unchanged. The core, C01–C04, F01–F06 and hardware are unchanged; all other STL
files are byte-for-byte identical to v1. Keep those existing pieces.

Both inward-down STLs and face-down 3MF alternatives are supplied, with updated
K print plates. Choose one orientation per piece. Retain support for normal
overhangs; removing these fragments does not make the whole piece support-free.

## What remains to hold the corners

The broad retaining lobes between the trimmed corners still engage all three F
neighbors. The sampled outward pull first meets them at the same 0.50 mm travel
as before. All tested tilted pulls and rocking paths remain blocked, including
the tests with the screwed corners lifted by 0.10 and 0.25 mm. The first-contact
distances for those tests match v1. The tips are therefore not required for
capture in these checks. This does not establish a physical breaking load.

The trim is subtraction only, at three chord planes 9.5 mm from the K axis and
confined below an axial coordinate of 22 mm. The actual removed material is
within radius 22.262 mm of the puzzle center. It removes approximately
143.765 mm³ per corner, leaving the exterior shape and mating-part geometry intact.
All four replacement meshes are closed and each is one connected solid.

## Printability check

A fixed-linewidth layer test reproduces six isolated fragments around the three
old tips at 0.16 mm layers / 0.42 mm width. The replacements have **one connected
printable layer graph in all 40 tested cases**, covering both orientations of all
four corners and layer/width pairs 0.12/0.42, 0.16/0.40, 0.16/0.42, 0.16/0.48 and
0.20/0.42 mm. Separate regions within one layer are allowed where they join the
main body higher up; those are normal overhangs, unlike isolated scraps.

These are geometric checks, not Bambu toolpaths. The installed Bambu Studio CLI
failed while loading its stock configuration, so no successful Bambu slicing
test is claimed. See [VALIDATION.md](VALIDATION.md) and `reports/tip-revision.json`.

## Physical result

On 2026-09-18 the owner reported that the Skewb with these trimmed tips printed
very well and turns very nicely. This supports the practical correction alongside
the geometry checks; it does not measure strength or long-term wear. The exact
settings and selected print orientation were not restated. See
[physical-feedback.json](physical-feedback.json) for the report and export hashes.

Source: `source/corner_tip_trim.py`. The trim happens after the original assembly
reliefs, preserving compatibility with the previous F and C pieces.
''')
write('DESIGN.md',r'''
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
''')

motion=json.loads((DEST/'reports/motion.json').read_text());assembly=json.loads((DEST/'reports/assembly.json').read_text());radii=json.loads((DEST/'reports/ridge-radii.json').read_text());shapes=json.loads((DEST/'reports/shape-distinction.json').read_text());surface=json.loads((DEST/'reports/export-surface.json').read_text())
mmax=max(v['worst'][1] for k,v in motion.items() if k!='_completion');amax=max(v['worst'][1] for k,v in assembly.items() if k!='_completion')
surfmax=max(v[d]['maximum_mm'] for v in surface['parts'] for d in ['regularized_cad_to_print','print_to_regularized_cad'])
write('VALIDATION.md',f'''
# Validation and physical feedback — Skewb v1.1

These checks use the exported, reloaded delivery meshes, in millimeters. They
establish sampled geometric fit and explicit assembly routes.

{{{{PHYSICAL_STATUS}}}}

The owner feedback adds a successful physical build and a qualitative assessment
of turning. It is distinct from the computational results below. Exact slicer
settings and nut-seat variant were not restated; holding force, turn torque,
wear life and a corner-cutting angle have not been measured. The report and
original export hashes are in [physical-feedback.json](physical-feedback.json).

| Check | Result |
|---|---|
| STL integrity | {len(manifest['parts'])} closed, consistently wound, positive-volume, single-component meshes |
| Print plates | {len(manifest['plates'])} named 3MF plates within 256 × 256 mm, without bounding-box overlap |
| Alternative orientations | 10 face-down 3MFs preserve the default meshes by rigid transformation |
| Aligned turns | 4 axes × 41 samples over 0–120°, with core, screws and washers |
| Scrambled turns | 16 mixed-axis moves × 21 intermediate samples; signatures updated after each move |
| Largest sampled turn intersection | {mmax:.3g} mm³, below the 0.001 mm³ numerical acceptance threshold |
| Whole-piece insertion | All 14 pieces, 79 offsets each, plus stand withdrawal |
| Largest sampled insertion intersection | {amax:.3g} mm³, below the 0.001 mm³ threshold |
| Retention | All 10 floating pieces have positive internal obstruction under outward pull |
| Further retention paths | 114 directional pulls and 72 ramped rocking paths, all obstructed |
| Lifted screwed corners | Retention paths repeated at nominal, +0.10 and +0.25 mm C lift |
| Radial fillets | {len(radii['sections'])} exposed transverse arc sections checked; no radius taper in the cutter |
| Largest sampled R3 circle deviation | {max(v['max_circle_error_mm'] for v in radii['sections']):.4f} mm |
| Largest sampled original-CAD vs STL ridge-profile difference | {max(v['max_export_profile_error_mm'] for v in radii['sections']):.4f} mm |
| Sampled export surface distance after regularization | At most {surfmax:.6f} mm bidirectionally |

The first detected nominal radial obstruction is about 0.55 mm for F pieces and
0.50 mm for K pieces. These are sampled pull travel against fixed rigid neighbors,
not looseness measured in an assembled hand-held puzzle. The retention tests use
only inner geometry within radius 30 mm, so the decorative exterior is not credited
as a retainer. The two canonical floating families are probed along 19 directions
and 12 rocking paths at each of three C lifts. This is not an exhaustive search
of every possible combined six-degree-of-freedom escape or flexing of printed feet.

## Floating-corner revision

Only K01–K04 differ from the previous release. The CAD edit is subtraction within
radius 22.262 mm; the exterior shape is unaffected. At 0.16 mm layers and 0.42 mm
fixed extrusion width, the old K01 has six small detached layer-graph components
around its three tips. The revised K pieces have a single connected printable
layer graph in all 40 tested combinations: four pieces, two orientations and five
layer-height/line-width pairs (0.12/0.42, 0.16/0.40, 0.16/0.42, 0.16/0.48, 0.20/0.42).

All tested pull and rocking paths remain obstructed, including lifted C pieces.
The first-contact distances match v1 in these sampled checks. That establishes
geometric retention after trimming, not equal breaking strength or measured force.

Bambu Studio 02.05.00.66's CLI test failed while loading the stock printer/filament
configuration (exit 139). No completed automated Bambu slice or toolpath check
was obtained during that validation run. The later owner report confirms an
actual successful print; its G-code was not inspected here. The layer checks are geometric simulations using a fixed line width;
they do not model Arachne's variable width, bridges, supports or slicer heuristics.
The revised parts still need appropriate support for their normal overhangs.

## Hardware

All four screw envelopes clear the core and each other. Washer insertion and
hex-key access are checked through each C well. The washer land and flat bearing
annulus are present. Each nut has a free outer loading route, intended interference
at its final seat, an axial retaining roof and a clear Ø3 mm press-rod route.
Rotating the nominal hex nut into the pocket walls produces additional geometric
interference; this does not predict the pocket's torque capacity. The alternate
core sizes clear the same mechanism envelope.

## Shape distinction

The minimum sampled exterior RMS difference between pairs, after trying proper
mounting rotations, is {shapes['C']['minimum_pair_rms_mm']:.3f} mm for C,
{shapes['F']['minimum_pair_rms_mm']:.3f} mm for F and
{shapes['K']['minimum_pair_rms_mm']:.3f} mm for K. Reflections are not identified
with rotations. These are sampled comparisons, not an optimality proof.

## Mesh and sampling limits

The cutter circles are checked in planes transverse to radial ridges, through the
inner track region and toward the exterior. The middle 80% of each exposed arc is
sampled; other fillets, the core cavity and the cube can terminate an arc. Exposure
is selected from pre-export CAD rather than from the mesh being tested. A fillet's
intersection with another surface need not itself be circular.

Export uses 0.001 mm normal-error mesh regularization before float32 STL conversion.
That tolerance is not a bound on the motion of every vertex: nearly zero-thickness
CSG whiskers can disappear. Regularization's added/removed volumes are reported
separately. Bidirectional surface samples compare the regularized export input with
the reloaded STL; the circle/profile checks also compare against original CAD.
Any extra cleanup is recorded per part in the manifest. Finite holes are not filled
as a mesh-repair shortcut. Face-down alternatives use indexed, double-precision
3MF to avoid a second STL quantization.

Turn samples are 3° apart for single-axis tests and 6° for the mixed sequence.
The analytic axisymmetric interfaces motivate intermediate motion, but the numerical
reports are sampled checks, not a formal continuous-motion proof. Small residual
intersection volumes at coincident mesh boundaries are treated as numerical noise.
First-layer section areas are also recorded; they do not predict support performance.

Machine-readable results are in `reports/`. `manifest.json` records dimensions,
orientations and STL hashes. `SHA256SUMS` covers the delivered package contents.
''')
write('source/README.md',r'''
# Regenerating the Wonky Skewb

Python 3.11 and the pinned packages in `requirements.txt` were used. This is a
Python/Manifold mesh-CAD workflow; OpenSCAD is not required. All units are mm.

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python build.py --build-dir ./build --output ./wonky-skewb-64mm-v1p1
```

Run from this source directory, or use absolute paths. The build creates raw
rotational cells, insertion reliefs and constant-radius ridge cuts; clips them to
the rotated cube; adds the axle feet; exports the print meshes; runs geometry and
hardware checks; renders documentation images; and packages the result and a ZIP.
A failed check stops packaging. Generation and validation take several minutes.

- `skewb_design.py`: dimensions, axes, hardware, cuts and assembly relief.
- `ridge_rounding.py`: constant transverse R3 cutters with adaptive stations.
- `finish_skewb.py`: exterior softening, axle feet, K-tip trimming and optional stand.
- `corner_tip_trim.py`: the final three-chord subtraction on K pieces only.
- `section_connectivity.py`, `check_tip_revision.py`: line-width-aware print-layer
  connectivity and localized geometry checks. Pass a previous release folder as
  the second argument to `check_tip_revision.py` to also check unchanged STL hashes.
- `render_tip_comparison.py`: before/after view of the modified internal flange.
- `export_skewb.py`, `mesh_io.py`, `print_3mf.py`: delivery meshes and orientations.
- `validate_skewb.py`: motion, insertion, hardware, retention and plate checks.
- `check_ridges_shapes.py`: delivered circle profiles and exterior distinction.
- `check_export_surface.py`: regularization volumes and sampled conversion fidelity.
- `render_skewb.py`, `mesh_render.py`: renders of the delivered meshes.
- `package_release.py`: documentation, source and checksum packaging.
- `physical-feedback.json`: the owner report and STL hashes of the delivered
  revision. Packaging associates that report only with an exact STL-set match;
  changed exports are marked as generated variants requiring their own print test.
  These hashes identify the supplied files, not an independently inspected print job.
- `chosen_rotation.json`: the exterior orientation reused from the Redi.

Each script can be run separately with `SKEWB_BUILD_DIR` pointing at the same
build directory. Caches are generated artifacts, not another design source. Do not
reuse old caches after changing geometric parameters. The full build regenerates
them in dependency order. Byte-identical output across versions of geometry
libraries is not promised; rerun the checks after changing versions or dimensions.

The four permanent C axes and the C/F/K signatures are internal mechanism
coordinates. `mechanism_to_print` in the manifest is a 3 × 4 rigid transform:
`print = Q @ mechanism + t`. Reverse it to restore the solved mechanism frame.
`cube-to-mechanism.json` maps an axis-aligned exterior cube into that frame.
The reference solved 3MF is displayed back in exterior-cube coordinates.

The license covers source and generated designs. The previous Redi release is a
separate design and is not modified by this build.
''')
summary=dict(design='wonky-skewb-64mm-v1.1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_tested=feedback_matches,physical_feedback_record='physical-feedback.json',physical_test_scope='Owner-reported qualitative print and turning result for matching delivered STLs; not all optional variants or instrumented performance',manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),reports={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((DEST/'reports').glob('*.json'))},stl_count=len(manifest['parts']),plate_count=len(manifest['plates']),default_puzzle_parts=15,hardware_sets=4)
write('build-report.json',json.dumps(summary,indent=2))
# Exclude only the checksum file itself; all code, documentation and models count.
paths=sorted(p for p in DEST.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
write('SHA256SUMS','\n'.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(DEST).as_posix() for p in paths))
archive=DEST.with_name(DEST.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(DEST.rglob('*')):
  if p.is_file():z.write(p,arcname=DEST.name+'/'+p.relative_to(DEST).as_posix())
archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
print('PACKAGED',DEST,'ZIP',archive,'bytes',archive.stat().st_size,flush=True)
