# Regenerate spherical v3.2

Use Python 3.11 and `requirements.txt`. OpenSCAD is not used. Choose fresh build and release directories after changing geometry or resolution: finishing caches are parameter-specific.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
CUBOCTA_BUILD_DIR="$PWD/build" CUBOCTA_RELEASE="$PWD/release" OPENBLAS_NUM_THREADS=1 .venv/bin/python build.py
```

Default `CUBOCTA_SEG=144` is the delivered resolution. The two spherical steps use 0.25° meridian samples. CAD and numerical reports are generated; README and design notes are authored separately.

- `design.py`: 72 mm body, R28.5/R33.5 spherical collar, 40° hidden neck / 45° exterior cuts. Petal membership cuts have an additional 0.10 mm inward offset at each track wall, blended back to the original exterior gap. No insertion sweep is subtracted.
- `ridge_rounding.py`: R2 radial fillets. Petal fits at radial stations >= 35 mm use an unclipped reference solid so the fillet is not diverted by the outer face.
- `flange_rounding.py`: R1.2 outline fillets swept radially through the four corners of the two center flange ends. Each uses the actual intersection of two hidden 40-degree cones to define its radial direction and an extended conical reference to fit the transverse circle. The v3.1 additional whole-body ball opening is removed; original small-edge rounding remains. Final meshes are simplified to 0.005 mm tolerance.
- `finish.py`, `tip_trim.py`: original small-edge rounding, corner spine and three tiny corner-tip cuts.
- `fixed-parts/corner-print-8.stl`: exact successful spherical-v3 corner master. The exporter checks the independently regenerated corner against it, then copies this STL unchanged. Changing shell radii or size requires regenerating that master; the exporter deliberately rejects such silent mixing.
- `hardware.py`: unchanged core, bearing foot, washer seat and M3×20 / 9×1 washer / DIN985 interfaces.
- `export.py`: watertight STLs, quantities and full-set 3MF plates.
- `validate.py`: final-mesh sweeps, nut loading and layer connectivity. The numerical assembly flag remains unvalidated: a complete insertion path was not computed. The owner subsequently assembled the supplied v3.2 files successfully; see [physical feedback](../physical-feedback.json).
- `retention_v2.py`, `nominal_capture.py`, `rocking.py`: shared test implementation adapted to spherical feet; only material below R28.5 is credited for capture. Supporting petals are moved outward 0.8 mm in the corner sensitivity tests.
- `stress_jumbling.py`: 48-step legal jumbling walk with retention checkpoints.
- `structure.py`, `neck_web.py`, `spherical_report.py`: hardware/neck dimensions and remaining spherical bearing faces.
- `render.py`, `illustrate.py`, `test_patch.py`: drawings, seven-piece full test and six-piece upgrade test.
- `package_audit.py`, `supplements.py`: plate counts and bounds, exact STL reuse, hardware, neighbors and summary.

Optional `revision_check.py` and `revision_render.py` compare the result with the original spherical-v3 package. Set `CUBOCTA_V3_REFERENCE` to that package directory. Also set `CUBOCTA_V31_REFERENCE` to the accepted v3.1 package. They verify byte-identical P/K/core reuse, measure all four radial outline fillets at three depths, and compare restored material with the original v3 center. `compatibility.py` can additionally check the original 64 mm core using `CUBOCTA_V1_REFERENCE`.

A clean rebuild runs all motion/retention checks. Do not reuse the v3.1 retention results through `CUBOCTA_RETENTION_BASELINE`: C has changed.

The original numerical summaries and their generator retain the pre-print status from the CAD-validation stage. The publication adds [VALIDATION.md](../VALIDATION.md) and physical feedback separately; a changed rebuild does not inherit the supplied files’ physical result.
