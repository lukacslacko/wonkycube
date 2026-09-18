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
