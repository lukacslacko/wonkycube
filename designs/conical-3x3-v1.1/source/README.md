# Regenerating the 70° conical 3×3

This is a Python 3.11 / Manifold mesh-CAD workflow. OpenSCAD is not needed.
Units are millimetres. From this source directory:

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python build.py --build-dir ./build --output ./wonky-conical-3x3-70deg-64mm-v1p1
```

The full build runs geometry generation, export and all required checks before
packaging. It takes several minutes. Rebuild everything after changing a
parameter; the previous caches are not a separately maintained design source.
Byte-identical exports across library versions are not promised.

- `conical_design.py`: axes, stepped cuts, tracks, insertion relief, inner
  rounding, core, nut seats, hardware envelopes and fit coupons.
- `ridge_rounding.py`: adaptive circular R3 sections along every radial ridge.
- `regularize.py`: bounded normal-error mesh simplification before finishing.
- `finish_conical.py`: exterior R0.8 softening, axle features, optional stand.
- `export_conical.py`, `mesh_io.py`, `print_3mf.py`: closed float32 STLs and 3MF
  plates, print orientations and explicit assembly transforms.
- `validate_conical.py`: reloaded-mesh motion, insertion, hardware, retention
  and plate checks.
- `check_midturn_capture.py`: additional extraction probes during turns.
- `check_ridges.py`: circle sections in exported meshes, including the tracks.
- `section_connectivity.py`, `check_printability.py`: fixed-width layer graphs.
- `check_export_fidelity.py`: export regularization and sampled surface error.
- `render_conical.py`, `mesh_render.py`: previews from actual delivered meshes.
- `package_release.py`: guide, neighbor map, source and checksummed ZIP.

Individual scripts use `CONICAL_BUILD_DIR` for their caches/release directory.
Set `CONICAL_SEGMENTS=192` for the supplied build resolution. Coarser trials are
not equivalent to the delivered geometry. Keep the geometry check reports
paired with the exact exported hashes in `manifest.json`.

The saved matrix maps exterior-cube coordinates into mechanism coordinates.
`manifest.json` gives `print = Q @ mechanism + t`; its inverse restores assembly
positions. E prints inward-down; K and C print broad-face-down. The solved reference 3MF is expressed in
exterior-cube coordinates and is deliberately not a print plate.

MIT license covers both this source and the generated design. The earlier
published Redi and Skewb releases are separate and are not modified by this build.

## Version 1.1

The washer seat is 28.8 mm from the core origin, 1.5 mm farther outward than v1.
`check_root_web.py` measures the root ligament on all six exported centers and
checks screw engagement/head containment. `v1-root-reference.json` preserves
the measured v1 baseline and an actual exported C01 section for the illustration.

`reinforce_from_v1.py` can create the compatible patch from a v1 release folder,
keeping E/K/core STL bytes. It adds material inside the old washer wells,
updates C meshes and plates, and retains original fidelity records for unchanged
parts by hash. The normal complete CAD build does not require the v1 STLs.

## Physical feedback

`physical-feedback.json` stores the owner's successful-print report and hashes
of the supplied v1.1 STLs. Packaging associates the report with a build only if
its STL set matches. A regenerated or modified set receives no automatic physical
validation. The report does not state a strength rating or a separate turning
assessment.
