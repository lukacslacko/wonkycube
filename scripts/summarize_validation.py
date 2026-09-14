"""Write the publication validation document from checked release reports."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'models/current/reference'


def main():
    v=json.loads((REF/'verification.json').read_text())
    r=json.loads((REF/'ridge_revision_check.json').read_text())
    a=json.loads((REF/'radius_check.json').read_text())
    e=json.loads((REF/'edge_shape_check.json').read_text())
    p=json.loads((REF/'reproduction_check.json').read_text())
    assert v['passed'] and r['passed'] and a['passed'] and p['passed']
    assert e['all_66_pairs_distinct_in_sampled_exterior']
    sections=a['sections'];minr=min(q['fitted_radius_mm'] for q in sections);maxr=max(q['fitted_radius_mm'] for q in sections)
    err=max(q['max_error_from_nominal_circle_mm'] for q in sections)
    gap=min(q['minimum_outer_gap_mm'] for q in v['all_axis_turn_sweeps'])
    old=sum(q['baseline_overlap_mm3'] for q in r['misalignment_probe'])
    new=sum(q['revision_overlap_mm3'] for q in r['misalignment_probe'])
    body=f'''# Validation and provenance

The **v4.2.1 publication export passes all four geometry reports**, plus an independent repeat-build comparison. These results apply to the files identified by [SHA256SUMS.txt](../models/current/SHA256SUMS.txt).

## Physical evidence and version identity

The owner built and iterated full puzzles on a Bambu Lab P1S with a 0.4 mm nozzle. PLA was the original material baseline. On 2026-09-14 the owner confirmed using the **v4.2 / 3 mm** files and reported that the print worked very well. The exact latest material/profile and the file hashes sent to the printer were not recorded.

During publication, the saved v4.2 folder was found to contain exports from different generation attempts: individual E01–E03 STLs had been updated, while other STLs, arranged plates and the assembly arrays still reflected an earlier attempt. That does not invalidate the owner's physical report, but it prevents attributing that report to one completely identified file set. The available files are preserved in the [historical snapshot](../history/README.md) and historical release assets.

V4.2.1 is a fresh, internally consistent export of the constant-3-mm intent, including the corrected inner track profile. It preserves the same core, corners, hardware, exterior face planes and print transforms. **This exact publication export has not independently been reported printed.** There is no need to replace a satisfactory existing print solely to match this release number.

## Digital checks on the publication set

| Check | Result |
|---|---|
| Saved puzzle and fixture/jig STLs | {len(v['saved_stl_checks'])}/28 closed, connected, consistently wound, positive-volume meshes |
| Aligned outer parts and hardware | No overlap detected |
| Eight complete 120° turn paths | 25 samples per axis, pass |
| Smallest sampled outer-part gap | {gap:.4f} mm |
| All corner and edge insertion routes | Clear along the specified sampled paths |
| Washer and driver access | All eight axes pass, including a Ø12 mm holder envelope |
| Stand withdrawal before C01 installation | Pass |
| Bearing annuli, washer seats and collars | Pass |
| Optional one-axis fixture | 360° sampled in 5° steps, pass |
| Arranged plates | All six within the 256 mm build area |
| One new E12 among v4.1 parts | All eight axes at 13 angles each pass |
| Edge radial retention | All twelve encounter both adjacent retainers |
| Detailed E12 extraction probes | 18/18 principal pulls blocked; 0 escapes among 60 specified rocking paths |
| Core and corners | Nine print STLs byte-identical to the supplied baseline |
| Repeat build from public source/baseline | All 28 STL bytes and all six decompressed 3MF payloads match |

The flat bearing foot intentionally touches the core pad. The verifier allows a small numerical coplanarity volume there (less than 0.01 mm³) only if a 0.005 mm lift clears it. Outer-part and hardware intersection checks use a separate 0.00001 mm³ threshold. Thread engagement in the plastic pilot is intentional and is evaluated separately from rotating-part collisions.

The detailed extraction audit includes corner lifts of 0, 0.10 and 0.25 mm and rocking up to ±10°. This is evidence of geometric obstruction along those paths, not a force rating or a search over every six-degree-of-freedom escape route.

## The actual 3 mm radius

The print STLs are transformed back into mechanism coordinates before measurement. Both radial ridges of all twelve edges are checked at 80 stations: every 0.125 mm from 24.5 through 34 mm in the inner track, plus outer stations at 35.5, 37.5 and 40 mm. Each fit uses 41 points across the central 80% of the exposed arc.

Across **{len(sections):,} sections**, fitted radii range from **{minr:.5f} to {maxr:.5f} mm**. The maximum sampled departure from the specified 3 mm circle is **{err:.6f} mm**. Acceptance thresholds are ±0.06 mm in fitted radius and 0.015 mm in circle departure. The construction uses a fixed transverse radius along the ridge; the section samples check the mesh approximation, rather than proving every surface point analytically.

![Actual constant-radius sections](../models/current/reference/constant-radius-v4p2.png)

Some tiny Boolean arcs collapsed into collinear slits during float32 STL conversion. The exporter collapses only closed boundary loops at most 0.002 mm long and within 0.000001 mm of a line, then requires a closed, consistently wound mesh. It does not fill arbitrary holes. This preserves the transverse profile more accurately than broadly simplifying the steep track region. [v3_io.py](../cad/v3_io.py) contains the bounds and checks.

## Misalignment and shape distinction

A separate probe holds C07 at ±0.5°, ±1° or ±2° and moves C08 through those same six values. Across 36 rigid poses, summed moving/static overlap decreases from **{old:.6f} to {new:.6f} mm³** relative to v4.1. This is a geometric interference comparison. It is not a measured torque reduction or a physical corner-cutting angle: the model does not simulate compliant motion, friction or cam-driven realignment.

All **66 edge pairs** remain distinct across **{e['common_valid_directions']} common radial directions** in the two compatible proper mounting orientations. The smallest pairwise RMS radial difference is **{e['minimum_pair_RMS_mm']:.4f} mm**. Reflections remain distinct. The exterior rotation was retained, not reoptimized.

## Reports and limitations

- [Mechanism, mesh, hardware and assembly report](../models/current/reference/verification.json)
- [Revision, mixed-version motion and retention report](../models/current/reference/ridge_revision_check.json)
- [Actual STL radius report](../models/current/reference/radius_check.json)
- [Edge-shape comparison](../models/current/reference/edge_shape_check.json)
- [Independent repeat-build comparison](../models/current/reference/reproduction_check.json)

Finite turn samples are not a continuous collision proof. The checks omit layer texture, support scars, friction, creep, wear, thread stripping and elastic deformation. The physical success report is useful evidence of the design family; it does not measure lifetime, load capacity or the effect of every parameter independently. Instructions and settings remain practical starting points rather than a certified printer profile.
'''
    (ROOT/'docs/validation.md').write_text(body)
    print('Validation document generated from passing reports')


if __name__=='__main__':main()
