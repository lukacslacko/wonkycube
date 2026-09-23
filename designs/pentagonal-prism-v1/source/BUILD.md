# Regenerate the design

Use Python 3.11+ and a virtual environment. Install `requirements.txt`. All dimensions are millimetres. No OpenSCAD, Blender or proprietary CAD is required.

Run from this source directory, with a fresh build directory. The environment variable retains its name from the shared conical-mechanism code:

```sh
export CONICAL_BUILD_DIR=/tmp/wonky-pentagonal-build
export MPLCONFIGDIR=/tmp/wonky-matplotlib
python build.py
python export_conical.py ../regenerated
python validate_conical.py hardware ../regenerated
python validate_conical.py assembly ../regenerated
python validate_conical.py motion ../regenerated
python validate_conical.py retention ../regenerated
python validate_conical.py plates ../regenerated
python check_structure.py ../regenerated
python check_ridges.py ../regenerated
python check_export_fidelity.py ../regenerated
python check_midturn_capture.py ../regenerated
python check_printability.py ../regenerated
python render_conical.py ../regenerated
python render_mechanism.py ../regenerated
python write_docs.py ../regenerated
python summarize_validation.py ../regenerated
```

`build.py` creates exact Boolean solids, insertion relief, local internal rounding, radial ridge rounding and the rounded exterior. It checkpoints the resulting meshes. Use a new build directory after changing geometry: existing final checkpoints are deliberately skipped for resumability.

`chosen_rotation.json` contains both the prior matrix and the new minimum-angle alignment. Cube-to-mechanism uses column vectors: `mechanism = R @ cube`. The manifest stores mechanism-to-print transforms. To restore a row-vector print vertex `v`, use `(v - translation) @ rotation`.

`conical_design.py` defines five symmetry orbits: equatorial centers, polar centers, vertical petals, horizontal petals and corners. The proper D5 group copies the internals within each orbit; clipping against the rotated cube creates the individual outside shapes. Seven directed 60° cones are used. Do not replace the 72°/180° move types with uniform 90° turns.

The fixed-linewidth printability check models connected printable regions between layers; it does not generate Bambu toolpaths. A CAD validation pass cannot establish wear, friction, elastic retention force or real printer accuracy.

## Physical feedback

The supplied `physical-feedback.json` records the successful assembly and nut fit of the published STL set. Documentation generation attaches it only when every puzzle STL matches the recorded hash. Regenerating or modifying meshes does not automatically confer physical validation.
