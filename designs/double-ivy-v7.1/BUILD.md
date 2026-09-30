# Rebuild Double Ivy v7.1

The source is self-contained, including the exact original core and stand meshes. The main source scripts reproduce the v7 baseline; the two explicit finishing steps below provide v7.1. Python 3.11.15 was used. No OpenSCAD or proprietary CAD is required. The original core is copied, not regenerated or scaled.

Create a virtual environment, install `source/requirements.txt`, and run these commands from the package root. Shell variables below only control this build. Use a **new, empty build directory** whenever parameters change; the generation scripts cache expensive geometry.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r source/requirements.txt
export OPENBLAS_NUM_THREADS=1
export IVY_BUILD_DIR="$PWD/build"
export IVY_RELEASE="$PWD/rebuilt"
export MPLCONFIGDIR="$PWD/build/matplotlib"
.venv/bin/python source/design.py
.venv/bin/python source/prepare_receivers.py
.venv/bin/python source/finish.py
.venv/bin/python source/guide_pads.py
.venv/bin/python source/export.py
.venv/bin/python source/drawings.py
```

Run the geometry and packaging checks:

```sh
.venv/bin/python source/validate.py motion
.venv/bin/python source/validate.py assembly
.venv/bin/python source/validate.py hardware
.venv/bin/python source/validate.py retention
.venv/bin/python source/validate.py midturn
.venv/bin/python source/validate.py feet
.venv/bin/python source/validate.py printability
.venv/bin/python source/guide_validation.py
.venv/bin/python source/neck_check.py
.venv/bin/python source/package_check.py
```

The baseline defaults reproduce the v7 72 mm nominal design at 144 radial segments. `design.py` defines the cut angles, three spherical retaining bands, four family floors and original hardware stack. `prepare_receivers.py` opens inward-accessible receiving grooves without cutting the captured feet. `finish.py` rounds radial ridges and the outside. `guide_pads.py` adds the non-retaining integral E/W core bearings. `export.py` emits print-oriented STLs, geometry-only named 3MF plates, a solved assembly and reversible transforms.

Do not uniformly rescale the STLs: the core and hardware dimensions must remain fixed. Parameter changes need the full set of checks again. The scripts produce geometry and numerical reports; the explanatory Markdown files are maintained separately. Mesh Boolean and simplification choices may cause small tessellation differences across platforms or library versions.

## Apply the published finishing steps

The supplied `source/rounding-correction/` contains the eight archived v7 meshes, fitting records and a deterministic geometric correction (mesh triangle order can differ). To reproduce the published C/F print shapes directly:

```sh
.venv/bin/python source/rounding-correction/regenerate.py rebuilt/stl/puzzle
```

This replaces C01–C04 and F01–F04 only. Its saved transforms match the v7 print poses. It corrects the supplied baseline; for a parametrically changed design, refit the fillets and revalidate rather than using archived parts.

The tighter compatible core and coupons are independently parametric:

```sh
IVY_CORE_RELEASE="$PWD/rebuilt-core" .venv/bin/python source/core-update/build.py
```

Use `rebuilt-core/stl/core-nut-seat-5.25.stl` as the new-build core. The 5.20 alternative and coupons are also generated. The delivered manifest contains the core transform and hashes. Keep the core geometry fixed if changing the outer size.

The baseline exporter produces v7 plate layouts and the original core reference. After the finishing steps, regenerate plates and the solved reference from the final meshes using `source/repack.py`; the supplied v7.1 manifest serves as the inventory and pose template:

```sh
.venv/bin/python source/repack.py . ../double-ivy-repacked
```

The first argument is a complete v7.1-shaped package with its manifest and final STLs. This command copies it and regenerates hashes, plate geometry, solved reference and plate maps. It is a packaging operation, not a replacement for geometry validation. To run the fresh full motion check on the delivered version:

```sh
.venv/bin/python source/validate.py motion .
```

Original v7 reports are archived separately. Physical feedback applies to the printed v7 baseline, not automatically to regenerated or modified geometry.
