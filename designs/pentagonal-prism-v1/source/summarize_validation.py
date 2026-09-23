"""Require completed checks and summarize their actual delivery results."""
from conical_design import *
from physical_feedback import feedback_text
import sys,hashlib,shutil
DEST=Path(sys.argv[1]) if len(sys.argv)>1 else WORK/'release'
meta=json.loads((DEST/'manifest.json').read_text());digest=hashlib.sha256((DEST/'manifest.json').read_bytes()).hexdigest()
checks={}
for mode in ['motion','assembly','hardware','retention','plates','structure','midturn-capture','printability','ridge-radii','export-fidelity']:
 d=json.loads((DEST/'reports'/(mode+'.json')).read_text())
 assert d.get('manifest_sha256')==digest,mode
 assert d.get('passed',d.get('_completion',{}).get('passed',False)),mode
 checks[mode]=d
for p in meta['parts']:
 assert hashlib.sha256((DEST/p['file']).read_bytes()).hexdigest()==p['sha256'],p['name']
rot=json.loads((HERE/'chosen_rotation.json').read_text());residual=max(abs((AXES[i]@R)[0]+(AXES[i]@R)[1]) for i in [4,5,6]);assert residual<1e-12
matrix_check=dict(rotation_deg=rot['delta_rotation_deg'],orthogonality_error=float(np.linalg.norm(R.T@R-np.eye(3))),determinant=float(np.linalg.det(R)),C05_C06_C07_plane_x_plus_y_residual=float(residual))
(DEST/'reports/alignment.json').write_text(json.dumps(matrix_check,indent=2))
trim=[]
for orbit in ORBITS:
 p=CACHE/'ridges-2'/(orbit+'-tip-trimming.json');trim.append(json.loads(p.read_text()))
(DEST/'reports/tip-trimming.json').write_text(json.dumps(trim,indent=2))
shutil.copy(CACHE/'regularization.json',DEST/'reports/regularization.json')
shutil.copy(CACHE/'finish-report.json',DEST/'reports/finish.json')
motion=checks['motion'];assembly=checks['assembly'];ret=checks['retention'];struct=checks['structure'];radii=checks['ridge-radii']
turns=[v for k,v in motion.items() if k.startswith('axis_') or k.startswith('scramble_')]
paths=[v for k,v in assembly.items() if k.startswith('insert_') or k=='stand_withdrawal']
contact=[v['first_contact_mm'] for k,v in ret.items() if k.startswith('radial_')]
summary=dict(passed=True,manifest_sha256=digest,puzzle_parts=sum(p['file'].startswith('stl/puzzle/') for p in meta['parts']),move_paths=len(turns),turn_samples=sum(p['samples'] for p in turns),max_turn_overlap_mm3=max(p['worst'][1] for p in turns),assembly_paths=len(paths),assembly_samples=sum(p['samples'] for p in paths),max_assembly_overlap_mm3=max(p['worst'][1] for p in paths),min_root_web_mm=min(p['minimum_sampled_well_root_web_mm'] for p in struct['centers']),min_screw_head_cube_recess_mm=min(p['minimum_head_to_cube_mm'] for p in struct['centers']),radial_contact_range_mm=[min(contact),max(contact)],ridge_radius_sections=len(radii['sections']),max_ridge_radius_error_mm=max(p['max_circle_error_mm'] for p in radii['sections']))
(DEST/'reports/summary.json').write_text(json.dumps(summary,indent=2))
text=f'''# Validation of the delivered print files

**All listed checks completed on the exported and reloaded meshes.** {feedback_text(DEST)} The reports are tied to the SHA-256 of `manifest.json`; every STL also has its own recorded hash.

| Check | Result |
|---|---|
| Main puzzle STLs | {summary['puzzle_parts']} closed, consistently wound, positive-volume single components |
| C05/C06/C07 alignment | Plane x+y=0; minimum rotation {rot['delta_rotation_deg']:.8f}° |
| Turning | All 7 axes, then 24 mixed moves; {summary['turn_samples']} sampled configurations |
| Largest measured turn overlap | {summary['max_turn_overlap_mm3']:.3g} mm³ (acceptance limit 0.001 mm³) |
| Assembly | {summary['assembly_paths']} radial insertion/stand removal paths, {summary['assembly_samples']} positions, including core and installed hardware |
| Largest measured assembly overlap | {summary['max_assembly_overlap_mm3']:.3g} mm³ |
| Washer lands and feet | Full annuli present; shaft, washer loading and hex-key access clear |
| Tight nut loading | Easy entrance, deliberate interference at terminal flats, roof support and rotational obstruction checked |
| Center stalks | Continuous cylindrical annulus around screw passage checked |
| Washer-well roots | Minimum sampled web {summary['min_root_web_mm']:.2f} mm |
| Screw heads | Minimum nominal clearance to cube faces {summary['min_screw_head_cube_recess_mm']:.2f} mm |
| Floating part retention | First aligned rigid radial obstruction at {min(contact):.2f}–{max(contact):.2f} mm of displacement |
| Off-axis retention | Angled pulls and combined rocking/extraction, including 0.10/0.25 mm center lift |
| Mid-turn retention | 30 sets of 13 rigid pull directions across both move families and 0/0.10 mm center lift |
| Radial rounding | R2 exposed arcs checked at {summary['ridge_radius_sections']} transverse sections, including tracks; worst measured radius error {summary['max_ridge_radius_error_mm']:.3f} mm |
| Layer connectivity | Every main print orientation at 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width pairs; no secondary printable component above 0.03 mm³ |
| Print plates | Bounds, non-overlap, units and alternate-orientation mesh equivalence checked |

The tip-trimming report records only tiny components that were already detached after rounding. They are deliberately absent from the print files. Root-web and annulus checks are geometric measurements, not finite-element strength calculations.

Motion is sampled every 3° from solved positions and every 6° in the mixed-move sequence. The cuts are surfaces of revolution and the move endpoints respect the D5 axis symmetry; the numerical checks additionally cover the actual clipped, rounded, exported parts and hardware. These checks are not an exhaustive search of every puzzle state or every possible elastic escape path.

Track gaps, nut press fits, friction, screw preload, layer adhesion and support removal still depend on the real print. Fixed-width layer connectivity is not a Bambu Studio toolpath simulation and does not eliminate the need for supports. Print the nut and rotor fit coupons before the complete puzzle. Use gentle initial turns and adjustment; no physical load or lifetime rating is claimed.
'''
(DEST/'VALIDATION.md').write_text(text)
print(json.dumps(summary,indent=2))
