# Regeneration

Python 3.11, manifold3d, numpy, scipy, trimesh, shapely, Pillow, matplotlib and rtree are used. See requirements.txt. OpenSCAD is not required.

From this source directory, use fresh empty build/release directories:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
FC_BUILD_DIR="$PWD/build" FC_RELEASE="$PWD/release" OPENBLAS_NUM_THREADS=1 .venv/bin/python build.py
```

Default resolution is 192 circular segments. FC_SEG can override it for development, but coarse trial meshes are not interchangeable with the release. Do not reuse cached geometry after changing dimensions: finishing and fillet sections are cached.

`design.py` defines 14 axes, two different rotational profiles, 38 external pieces, and straight center-insertion relief. `hardware.py` constructs the one-piece nut core and the two seat depths for M3×20 screws and 7×0.5 mm washers. `finish.py` softens rims; `ridge_rounding.py` applies R2 circular transverse fillets along both petal tips, continuing through the inner tracks. Tiny detached numerical/rounding remnants are removed with volume limits and recorded.

Triangular centers have continuous integral screw stems up to their washer seats. `stem_sweep()` encloses that stem in a capsule and revolves its profile about a neighboring square axis. `finish.py` subtracts this continuous clearance envelope from the petals before rounding. The raw petals used for center-insertion relief remain conservative supersets of the final petals.

`export.py` makes three repeated exterior STL types, one core, fit coupons, optional cores, an optional stand, and geometry-only 3MF plates. Export cleanup has small bounded geometric allowances and the resulting meshes are reloaded for verification.

`validate.py` checks the actual STL meshes, representative assembly paths, every turn axis, intermediate petal retention, tilt probes, washer-root webs, hardware clearance, nut loading and print-layer connectivity. `render.py` renders the supplied meshes and the painting map. `supplements.py` records the parameters and neighbors and bundles the source.

These are finite rigid-geometry checks and a fixed-linewidth layer model. They do not establish measured turning torque, fatigue, elastic pop force, or a particular slicer's exact toolpath.
