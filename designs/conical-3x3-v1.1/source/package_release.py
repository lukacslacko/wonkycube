"""Package source, tested print meshes, assembly instructions and audit results."""
from conical_design import *
import shutil,sys,hashlib,zipfile
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else WORK/'wonky-conical-3x3-70deg-64mm-v1p1'
required=['motion','assembly','hardware','retention','plates','midturn-capture','ridge-radii','printability','export-fidelity','root-web']
checks={}
for name in required:
 p=DEST/'reports'/(name+'.json');a=json.loads(p.read_text());assert a.get('passed',a.get('_completion',{}).get('passed',False)),(name,'not passed');assert a['manifest_sha256']==hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest();checks[name]=a
 if name=='printability':assert len(a['checks'])==27
 if name=='midturn-capture':assert len(a['checks'])==12
meta=json.loads((DEST/'manifest.json').read_text());h={r['name']:r for r in meta['parts']}
feedback=json.loads((HERE/'physical-feedback.json').read_text())
actual_hashes={p.relative_to(DEST).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in DEST.rglob('*.stl')}
feedback_matches=actual_hashes==feedback['delivered_stl_sha256']
shutil.copy2(HERE/'physical-feedback.json',DEST/'physical-feedback.json')
physical_status=(
 '**Owner-printed:** the owner reported that the reinforced v1.1 printed very well. '
 'These STL hashes match the supplied set associated with that report.' if feedback_matches else
 '**Regenerated build:** the STL hashes differ from the supplied v1.1 set. '
 'The original reinforced v1.1 received a successful-print report; this changed export needs its own print test.'
)

report=dict(version='wonky-conical-3x3-70-v1.1',cube_side_mm=SIDE,cone_half_angle_deg=ANGLE,
            printed_piece_count=27,moving_piece_count=26,physical_print_tested=feedback_matches,physical_feedback_record="physical-feedback.json",
            sampled_turn_poses=sum(r['samples'] for r in checks['motion'].values() if isinstance(r,dict) and 'samples' in r),
            checked_R3_sections=len(checks['ridge-radii']['sections']),
            maximum_R3_circle_error_mm=max(r['max_circle_error_mm'] for r in checks['ridge-radii']['sections']),
            layer_connectivity_cases=sum(len(r['tests']) for r in checks['printability']['checks']),
            minimum_stalk_root_web_mm=min(r['new_minimum_mm'] for r in checks['root-web']['centers']),
            screw_projection_past_locknut_mm=checks['root-web']['tip_beyond_nut_mm'],
            all_required_checks_passed=True,reports=list(checks),
            manifest_sha256=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest(),
            disclaimer='Computed geometry checks plus the separate physical-feedback record. No instrumented torque, strength or wear rating; no exhaustive escape proof.')
(DEST/'reports/validation-summary.json').write_text(json.dumps(report,indent=2))
neighbors={}
for row in ROWS:
 sig=set(row['signature']);adj=[r['name'] for r in ROWS if len(sig.symmetric_difference(r['signature']))==1]
 neighbors[row['name']]=dict(signature=row['signature'],direction=row['direction'],neighbors=adj)
(DEST/'reference/neighbors.json').write_text(json.dumps(neighbors,indent=2))
lines=['# Piece identification and neighbors','',
 'Mark these IDs on the inside of each piece after removing it from the bed. C means a screwed **center**, E an edge, and K a floating corner. These are mechanism names; a wonky piece can cover several exterior faces.','',
 '![Exterior assembly map](images/assembly-map.png)','',
 '| Piece | Adjacent screwed centers / axis directions | Pieces sharing a seam |','|---|---|---|']
axisnames=['+X','+Y','+Z','−X','−Y','−Z']
for row in ROWS:
 ids=', '.join(f'C{i+1:02} ({axisnames[i]})' for i in row['signature'])
 lines.append(f'| {row["name"]} | {ids} | {", ".join(neighbors[row["name"]]["neighbors"])} |')
lines+=['','Opposite centers: C01–C04, C02–C05, C03–C06. Directions here are in the **mechanism frame**; the face-map labels use the exterior cube frame.','',
 'Loose-part identification: [centers](images/catalog-C.png), [edges](images/catalog-E.png), [corners](images/catalog-K.png).','',
 'The solved reference 3MF contains named, overlapping assembly-position objects. Open it for inspection only; print the separated STL files or print plates.']
(DEST/'NEIGHBORS.md').write_text('\n'.join(lines)+'\n')
(DEST/'README.md').write_text('''# Wonky conical 3×3 — 70°, 64 mm, v1.1

A complete printable design using six face-direction axes and the saved exterior
rotation of the successful 64 mm Wonky Redi and Skewb. Its 70° conical cuts give
six screwed centers, twelve edges and eight floating corners. The intended moves
are 90° face turns. The surface outline is the selected 70° gallery shape, with
working gaps and rounded edges added.

{{PHYSICAL_STATUS}}
See [the physical feedback record](physical-feedback.json) for the report and
its scope. Exact slicer settings were not restated; strength and endurance
have not been measured.

![Delivered geometry](images/solved-two-sides.png)

## Revision 1.1 — reinforced screwed centers

A slicer review exposed a thin connection between each center's stalk and body.
The original mesh was connected, but the shortest measured web between the wide
washer well and the outside root was only about **0.65 mm**. Connectivity and
collision checks did not establish sufficient strength at that junction.

The washer seat is now **1.5 mm farther outward**, shortening the wide well and
increasing that local web to about **2.04 mm**. The Ø3.6 mm through passage,
bearing foot, exterior and retaining surfaces keep their working dimensions.
The M3 × 20 screw still passes through the entire locknut, projecting about
**1.85 mm** beyond it. The head remains inside the solved cube.

Only the six **C01–C06** puzzle STLs change. The **core, twelve E edges and eight
K corners are byte-for-byte identical to v1** in this compatible release.
Keep any of those already printed. The optional rotor-fit coupon and reference
assembly are also updated; the assembly stand and nut coupons remain unchanged.

![Stalk-root reinforcement](images/root-reinforcement.png)

This is a geometric reinforcement, not a measured strength or endurance rating.
For the revised centers, retain the recommended walls and solid layers around
the washer seat; sparse infill alone is not a substitute for that load path.

## What to print

Print exactly one of each of the **27 files in `stl/puzzle/`**:

- `core.stl`: default 5.40 mm terminal nut seats.
- `C01`–`C06`: six screwed centers.
- `E01`–`E12`: twelve floating edges.
- `K01`–`K08`: eight floating corners.

The STLs are already on the bed, in millimetres. Use **100% scale**. E pieces have their inward radial vector pointing down, as preferred on the
previous prints. K corners and C centers use a broad exterior face down;
the K pieces otherwise have almost point-sized initial bed contact. The core
uses an axle flat down. Geometry-only 3MF plates preserve those poses and the object names.
They do not silently install a printer or filament profile.

The `E-face-down` / `K-radial-down` plates and individual `print-options/` files
are **alternate orientations of the same pieces**, not extra parts to print.
Do not print both sets. Keep the default radial-down pose for the edges to continue the approach
that worked on the Redi. The optional radial-down corner pose requires supports
under the tiny initial tips; the default broad-face-down corners have much
more bed contact.

Print the nut coupons first. `core-seat-5.30` and `core-seat-5.50` are optional
replacement cores with tighter/looser final seats; choose only one core.
The loading mouth is 5.85 mm in all variants. Test the actual DIN985 nut by
fully driving a screw through its nylon ring, not just by checking whether the
nut stays in place. The optional stand supports the core during assembly and
is removed before the last center is fitted.

## Hardware

- **6 × DIN912 M3 × 20 mm screws**.
- **6 × washers, 9 mm outside diameter × 1 mm thick**, with M3 clearance holes.
- **6 × DIN985 M3 nylon-insert locknuts**, nominal 5.5 mm across flats × 4 mm high.
- A matching hex key; a blunt approximately 3 mm rod to seat the nuts.

Besides the core, there are no separate hidden printed parts. The core,
26 visible pieces and six hardware stacks are the whole mechanism; assembly
uses no sleeves, inserts, springs, magnets or glued joints. The optional stand is an assembly tool only.

## Printing on the P1S

Use the 0.4 mm nozzle and PLA for the first trial, so that the material stays
consistent with the successful earlier builds. A practical starting point is
0.16 mm layers, 4 walls and 20–25% infill; use more walls/infill for the core if
desired. These are suggested starting settings; the successful-print report
did not restate the exact slicer settings used. Use a brim on the small radial-down footprints and removable
supports for the flange undersides. Inspect support placement before slicing;
keep the screw bores and nut-loading channels accessible. Small channel roofs
can be bridged; avoid packing inaccessible support inside a nut seat.

Remove support residue and raised seams from the sliding surfaces, especially
under the retaining lands. Do not sand away the lands or enlarge the main cone
gaps as a first step. The broad track clearance and close main faces have
different jobs. Any elephant foot on a radial-down retaining end needs removal.

The delivered meshes were checked for a connected printable layer graph at
0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width combinations. This is a
geometric check, not Bambu Studio toolpaths or a physical strength test.

## Assembly

1. Mark every piece on its inside using [the ID map and neighbor table](NEIGHBORS.md).
   Open `reference/DO-NOT-PRINT-solved.3mf` to inspect the named solved assembly.
2. Load all six locknuts into the bare core through their side channels. Orient
   each nut with its nylon ring **toward the core's center**, so the screw enters
   the metal threads first. Press the nut into the tighter final seat with a
   blunt rod. Check all six seats against installation torque before covering them.
3. Optionally attach the assembly stand in the **C01** position, using the same
   screw and washer that will later hold C01. It leaves the other insertion paths
   open. Temporary tape or elastic bands around the outside can help hold loose
   pieces while the retainers are still absent.
4. Place **all eight K corners first**, then **all twelve E edges**, matching the
   outside shape and IDs. Each has a straight inward radial insertion path at
   this stage. No flange must be forced through another flange.
5. Fit C02–C06 over their corresponding core flats. Drop a washer down each
   access well and install its screw into the locknut. Start loose enough to
   permit small alignment adjustments. The centers retain the edges, which
   in turn retain the corners.
6. Support the assembly, remove the stand's screw and washer, and withdraw the
   stand straight along the C01 axis. Install C01 with that screw and washer.
   If no stand was used, simply install C01 last.
7. Adjust the six centers evenly. Tighten until the assembly just becomes firm,
   then back off slightly until it turns without force. M3 coarse pitch is
   0.5 mm, so **one fifth of a turn corresponds to 0.10 mm** of axial adjustment.
   Locknut drag is not the same as bearing clamp load: judge by the puzzle's feel.
   Remove any temporary tape/bands before turning.

Keep the screw adjustment small. The tests include modest center lift, but
excess lift can increase rocking and eventually allow popping. Do not force
a turn through support scars, a badly misaligned layer, or a tight nut seat.

![Mechanism pieces](images/internal-pieces.png)

## Design details and evidence

See [DESIGN.md](DESIGN.md), [NEIGHBORS.md](NEIGHBORS.md), and the JSON files in
`reports/`. Those reports check the **reloaded delivered STLs**, not only the
pre-export CAD. They include turns, scrambled positions, insertion and stand
withdrawal, hardware access, sampled extraction paths, fillet sections,
printable connectivity, and plate placement.

Full regeneration source is in `source/`; `manifest.json` records part hashes,
dimensions, volumes and the rigid print-to-assembly correspondence. The solved
reference is for inspection only. MIT license covers the source and generated
design. No print has been sent to a printer by this package.
''')
(DEST/'DESIGN.md').write_text('''# Mechanism and dimensions

## Capture and movement

The six axes are ±X, ±Y and ±Z in the mechanism frame. Every quarter-turn moves
one center, four edges and four corners. Piece membership is the set of conical
caps containing that piece: one cap for a center, two for an edge and three for
a corner. Proper cube rotations permute this arrangement, giving ordinary
3×3 piece movement with visible center orientation.

The visible boundaries are cones with 70° half-angle and apex at the puzzle
center. Inside the outer shell, their profiles acquire flat shoulders. In local
axis coordinates `(rho, z)`, the nominal retaining lip extends to rho = 26.5 mm
between z = 5.5 and 8.5 mm, reconnecting to the cone at rho = 8.5 / cot(70°),
approximately 23.35 mm. That gives a 3 mm axial lip and approximately 3.15 mm
radial overhang **before rounding and clearance**. The exterior cut is still the
chosen cone; the hook lives inside it.

Each boundary is a surface of revolution about its associated turn axis. A
whole moving cap therefore follows an invariant boundary while turning. The
unrounded shoulder is expanded to define its mating track; the printed lip is
rounded separately. This preserves generous track entry without enlarging the
main cone gap. Rounding and exterior clipping only remove material.

Corners are retained by edges, edges by screwed centers. The checked insertion
order is K → E → C; the six screws are reached from outside. No snap-fit through
an already closed retaining loop is required. The optional stand has a checked
withdrawal route through the unoccupied C01 position.

![Exploded mechanism](images/exploded.png)

## Parameters retained from the successful builds

| Parameter | Value and interpretation |
|---|---|
| Solved cube | 64 mm, same saved active exterior rotation |
| Main conical-face gap | 0.03 mm total nominal separation |
| Track allowance | 0.40 mm extra expansion of the unrounded mating profile, per boundary |
| Track transition | Tapers back to the main gap over local rho 26.8–29.0 mm |
| Long radial ridge rounding | R3 circular sections, continued through the track region |
| Other inner convex edges | 0.60 mm on edges/corners; 0.45 mm on centers |
| Exterior lips | Approximately R0.8 subtractive morphological rounding |
| Core sphere / moving inner cavity | R19.2 / R19.7 mm: 0.50 mm nominal radial separation |
| Core axle pad / center foot plane | 17.60 / 17.70 mm from origin: 0.10 mm nominal axial gap |
| Bearing foot | 6.2 mm outside diameter; matching flat core pad |
| Rotating shank bore | 3.6 mm diameter: 0.6 mm diametral clearance around an M3 shank |
| Washer access well | 9.6 mm diameter for a 9 mm washer |
| Washer seat | 28.8 mm along the axis (v1.1) |
| Washer / screw underside / screw head top | 1.0 mm / 29.8 mm / 32.8 mm |
| M3 × 20 screw tip | 9.8 mm from the origin |
| Nut axial envelope | 11.65–15.65 mm; screw extends 1.85 mm past the inner nut face |
| Core screw passage | 3.4 mm diameter, through the core |
| Nut loading mouth / terminal seat | 5.85 / 5.40 mm across flats; 5.30 and 5.50 mm alternatives |
| Nut pocket height / roof thickness | 4.25 / 1.95 mm |

The screw is fixed relative to the core; the printed center and washer provide
an adjustable bearing interface. The nuts resist screw loosening and are keyed
by their flats. There is no rigid spacer: tightening clamps the rotor, while a
small back-off permits rotation. Use the coupons to check actual hardware fit.

The 0.03 mm main gap is an intentional continuation of the owner's successful
close-fitting prints, **not a general claim of 0.03 mm FDM accuracy**. It is
independent of the wider hidden track and adjustable screw position.

## Rounding across branched tracks

The six-axis geometry has branched inner sections. Reusing the Redi's rule for
choosing the last material interval would round the far return of some sections
and leave thin fins. This design selects the entry boundary, softens other inner
protrusions, and verifies the delivered fillet arcs in transverse sections.
Intersections with the core cavity, other fillets and the outside cube can
terminate an arc; a spherical principal-curvature claim is not intended.

No disconnected flange scraps are deliberately included. The delivered layer
connectivity report checks all 27 main print files at two layer/line-width
combinations. This extends the Skewb lesson: mesh connectivity alone is not
sufficient evidence that a thin tip will produce connected extrusion paths.

## Stalk-root reinforcement in v1.1

The original center was a single solid, with a continuous stalk, but the washer
well approached the outside root to approximately 0.65 mm at its thinnest
measured location. A connected layer graph does not identify such a weak load
path. The v1.1 seat moves outward by 1.5 mm, adding approximately 93.27 mm³ inside
each old well. The corresponding root web measures at least 2.04 mm on all six
exported centers. The exposed flange and bearing dimensions remain unchanged.

The measurement samples 720 angles around the bottom rim of the washer well,
finds the nearest exposed root surface, and checks that the shortest connecting
segment lies in solid material. It is a geometric wall measurement, not an
FEA result or a force rating. See `reports/root-web.json` and
`images/root-reinforcement.png`.

The compatible patch starts from the actual v1 STLs; E/K/core files keep their
original hashes. Their original CAD-to-export fidelity data are retained with
hash checks. The six new C files are audited against their new pre-export CAD.
The standard full CAD build also uses the raised seat; exact STL bytes across
independent builds are not promised.

## Validation limits

The reports establish closed, connected delivered solids and collision-free
**sampled** intended turns, including a multi-axis scramble. They check radial
insertion, the hardware envelopes and loading routes, stand withdrawal, and
rigid extraction/rocking probes with modest center lift. Additional extraction
probes are made at 22.5°, 45° and 67.5° through a turn.

They do not measure turning torque, printed holding force, elastic popping,
thread durability or long-term wear, and do not exhaust every possible escape
motion.

{{PHYSICAL_STATUS}} See [physical-feedback.json](physical-feedback.json). This
is a successful-print report, not an instrumented strength test or a separate
assessment of turning performance.

The exterior rotation matrix is stored in `source/chosen_rotation.json`. All
piece directions are in mechanism coordinates. The manifest's transform is
`print = Q @ mechanism + t`; invert it to restore a printed piece to assembly.
The reference solved 3MF is expressed in the exterior cube's coordinates.
''')
source_files=['conical_design.py','ridge_rounding.py','regularize.py','finish_conical.py','export_conical.py','validate_conical.py','check_ridges.py','check_printability.py','check_midturn_capture.py','check_export_fidelity.py','render_conical.py','package_release.py','reinforce_from_v1.py','check_root_web.py','v1-root-reference.json','build.py','mesh_io.py','mesh_render.py','print_3mf.py','section_connectivity.py','chosen_rotation.json','requirements.txt','LICENSE','README.md','physical-feedback.json']
(DEST/'source').mkdir(exist_ok=True)
for name in source_files:
 if (HERE/name).resolve()!=(DEST/'source'/name).resolve():shutil.copy2(HERE/name,DEST/'source'/name)
shutil.copy2(HERE/'LICENSE',DEST/'LICENSE')
for name in ['README.md','DESIGN.md']:
 p=DEST/name;p.write_text(p.read_text().replace('{{PHYSICAL_STATUS}}',physical_status))
(DEST/'VALIDATION.md').write_text(f'''# Conical 3×3 validation and physical feedback

{physical_status}

The owner report is limited to successful printing. It does not supply a separate
turning assessment, instrumented strength or fatigue result, or an inspection of
the printer's input files. Exact settings and the chosen nut-seat variant were
not restated. [Report and supplied STL hashes](physical-feedback.json).

The numerical reports describe the delivered meshes and their explicit assembly
transforms. Each required report is linked to the manifest by SHA-256.

| Check | Result |
|---|---|
| Required report groups | {len(checks)} passed |
| Sampled intended turn and scramble poses | {report['sampled_turn_poses']} |
| R3 transverse ridge sections | {report['checked_R3_sections']} |
| Largest checked circle error | {report['maximum_R3_circle_error_mm']:.4f} mm |
| Printable layer-graph cases | {report['layer_connectivity_cases']} |
| Smallest measured screwed-piece root web | {report['minimum_stalk_root_web_mm']:.2f} mm |
| Screw projection beyond locknut | {report['screw_projection_past_locknut_mm']:.2f} mm |

Additional checks cover radial insertion, hardware and driver access, stand
withdrawal, exported mesh fidelity, print-plate placement, and sampled extraction
and rocking paths, including intermediate turn positions and modest center lift.

The web measurement tests 720 angular positions per screwed piece. The six
reinforced centers preserve bearing and retaining dimensions; the other 21
puzzle STLs are byte-for-byte unchanged from v1. See
[the revision report](reports/revision.json) and [root measurements](reports/root-web.json).

Connectivity establishes a continuous solid or a modeled printable path; it does
not establish sufficient mechanical strength. Finite pose samples also do not
prove clearance or retention at every possible configuration. Physical loads,
friction, elastic popping, wear and fatigue need separate testing.

[Aggregate report](reports/validation-summary.json) · [Design](DESIGN.md) ·
[Assembly and printing](README.md) · [Regeneration source](source/README.md)
''')
if OUT.resolve()!=DEST.resolve():shutil.copytree(DEST,OUT,dirs_exist_ok=True)
paths=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(OUT).as_posix()+'\n' for p in paths))
archive=OUT.with_name(OUT.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(OUT.rglob('*')):
  if p.is_file():z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
print('PACKAGE',archive,flush=True)
