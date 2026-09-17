"""Package a checked development build into a separate, reproducible release."""
from redi_design import *
import shutil,hashlib,zipfile
src=WORK/'release'
dest=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'packaged'
manifest=json.loads((src/'manifest.json').read_text())
reports={key:json.loads((src/'reports'/(key+'.json')).read_text()) for key in ['motion','assembly','hardware','retention','plates','ridge-radii','edge-shapes']}
assert all(reports[key].get('_completion',{}).get('passed',reports[key].get('passed',False)) for key in reports)
for row in manifest['parts']:
 assert hashlib.sha256((src/row['file']).read_bytes()).hexdigest()==row['sha256'],row['name']
for row in reports['plates']['plates']:
 assert hashlib.sha256((src/row['file']).read_bytes()).hexdigest()==row['sha256']
motion=reports['motion'];assembly=reports['assembly'];retention=reports['retention'];radii=reports['ridge-radii'];shape=reports['edge-shapes']
axis_max=max(row['worst'][1] for key,row in motion.items() if key.startswith('axis_'))
scramble_max=max(row['worst'][1] for key,row in motion.items() if key.startswith('scramble_'))
insertion_max=max(row[1] for key,row in assembly.items() if key.startswith('insert_'))
contacts=[d for row in retention['all_edges'] for d in row['first_radial_contact_each_retainer_mm']]
radius_values=[r['fitted_radius_mm'] for r in radii['sections'] if r['radius_fit_resolved']]
circle_error=max(r['max_circle_error_mm'] for r in radii['sections'])
cleanup=max(row.get('cleanup',{}).get('simplification_mm',0) for row in manifest['parts'])
weld=max(row.get('cleanup',{}).get('slit_weld_displacement_bound_mm',0) for row in manifest['parts'])
text=f'''# Validation — compact Redi v4.3, 64 mm

These checks use the **exported and reloaded print STLs**, restored to their
assembly coordinates. These checks describe this regenerated file set; they do
not establish that this exact rebuild has been physically printed. The published
v4.3 has owner feedback of good feel apart from nut seats that can spin under
locknut installation torque. A tighter terminal seat remains a proposed core-only
change, not a feature of the current geometry.

## Files and fit

- {len(manifest['parts'])} STL files including optional alternatives and fit tools;
  all are single connected, watertight, consistently wound solids with positive volume.
- {len(manifest['plates'])} geometry-only 3MF plates checked for units, valid triangle
  indices, non-overlapping object bounds, and the P1S's 256 mm build volume.
- E pieces point radially inward toward −Z, with their inner feet facing the
  bed. C pieces retain an outside face on the bed; the core uses an axis flat.
  Support and brim settings follow your preferred edge-printing setup.
- A 0.002 mm initial mesh simplification is followed by bounded export cleanup.
  Largest additional simplification recorded: {cleanup:.6f} mm. The largest
  cumulative recorded numerical-slit vertex-weld bound is {weld:.6f} mm.
  Small coincident/degenerate triangles are cleaned without filling finite holes.
  These are mesh tolerances, not printer accuracy guarantees.

## Motion and assembly

- All eight axes, 0–120° sampled every 3°: largest intersection {axis_max:.8f} mm³.
- Twelve consecutive mixed-axis turns, sampled every 6° in each resulting
  configuration: largest intersection {scramble_max:.8f} mm³.
- Core, screws, and washers are included in the movement checks.
- All 20 exterior insertion paths: edges before C pieces, with same-family
  peers treated as already installed; 0.25 mm samples near engagement.
  Largest intersection {insertion_max:.8f} mm³.
- The optional stand clears edge-loading paths and withdraws along C01 before
  the final C piece is installed. Temporary external support is still needed.

The surfaces of revolution and explicit insertion relief supply the intended
kinematic construction. Sampling alone is not a continuous-motion proof.

## Retention

Every edge is obstructed by each of its two C retainers during a straight radial
pull. First sampled contacts lie between **{min(contacts):.2f} and {max(contacts):.2f} mm**
at a 0.001 mm³ overlap threshold. The inner geometry alone is used, so these
tests do not credit exterior-face interference as flange capture.

The canonical edge also encounters obstruction along all {len(retention['principal'])}
specified principal pulls, including C lifts of 0, 0.10, and 0.25 mm, and all
{len(retention['rocking'])} specified ramped rocking paths (±5°, ±10°, and zero).
These are geometric capture tests, not holding-force measurements. They do not
rule out every possible compound escape, elastic deformation, or multiple-piece
motion. They also show why tighter main-face gaps do not remove all track float.

## Rounding and distinct pieces

Both radial ridges of all twelve edges were sectioned through the inner tracks
and into the outer cone: {len(radii['sections'])} sections on delivered STLs.
All sections agree with their nominal **3 mm** construction circles to within
{circle_error:.4f} mm. On the {len(radius_values)} sections with enough exposed arc
to resolve curvature, fitted radii range from {min(radius_values):.4f} to
{max(radius_values):.4f} mm. Near track inflections some arcs shrink almost to a
point; those are checked against the known construction circle rather than an
ill-conditioned free radius fit. No inner radius taper is used.

All 66 pairs of edge exteriors remain distinct when compared in both proper
mounting orientations, using {shape['common_directions']} common radial sample
directions. The weakest pair's RMS difference is {shape['minimum_pair_rms_mm']:.3f} mm.
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

Actual print fit, locknut grip, roof strength, turning torque, corner cutting,
wear, and PLA settling remain physical-trial questions. No guarantee is made
that every printer yields the same bind/release point. Machine-readable details
are in `reports/*.json`; file hashes are in `manifest.json` and `SHA256SUMS`.
'''
(src/'VALIDATION.md').write_text(text)
if dest.exists():raise SystemExit('Package destination exists; choose a new directory.')
shutil.copytree(src,dest)
(dest/'source').mkdir()
for path in HERE.iterdir():
 if path.is_file() and path.suffix in ['.py','.md','.json','.txt']:shutil.copy(path,dest/'source'/path.name)
(dest/'source/masters').mkdir()
for name in ['canonical-C.npz','canonical-E.npz','ridge-sections.json']:shutil.copy(OUT/name,dest/'source/masters'/name)
shutil.copy(OUT/'ridge-sections.json',dest/'reference/ridge-sections.json')
files=sorted(p for p in dest.rglob('*') if p.is_file() and p.name!='SHA256SUMS')
(dest/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(dest).as_posix()+'\n' for p in files))
archive=dest.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files+[dest/'SHA256SUMS']:z.write(p,Path(dest.name)/p.relative_to(dest))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
digest=hashlib.sha256(archive.read_bytes()).hexdigest();archive.with_suffix('.zip.sha256').write_text(digest+'  '+archive.name+'\n')
print('PACKAGED',dest,'ZIP bytes',archive.stat().st_size,'SHA256',digest)
