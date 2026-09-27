# Build and validate the 64 mm conical triangular prism

Python 3.11 with the pinned packages in `requirements.txt`. Generated coordinates are millimetres. The saved cube rotation and all hardware dimensions are in `conical_design.py` and `chosen_rotation.json`.

From this source directory, with a fresh build directory:

```sh
export CONICAL_BUILD_DIR=/tmp/wonky-triangular-build
export MPLCONFIGDIR=/tmp/wonky-triangular-matplotlib
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
python check_corner_capture.py ../regenerated
python check_printability.py ../regenerated
python render_conical.py ../regenerated
python render_mechanism.py ../regenerated
python write_tri_docs.py ../regenerated
python summarize_validation.py ../regenerated
```

Use a fresh build directory after modifying geometry: ridge and final-part caches are reusable checkpoints, not parameter-aware caches. Production uses 240 revolution segments; `CONICAL_SEGMENTS` can lower this for exploratory builds. The shoulder dimensions are designed for 70°, not an arbitrary-angle parameterization.

Exterior finishing defaults to three worker processes. `CONICAL_FINISH_WORKERS=1` limits memory use. Keep generated renderings and reports with the matching export manifest; never transfer physical validation from a different puzzle or STL version.

The documentation generators attach the physical build report only when all puzzle STL hashes match the supplied files associated with that report. Regenerated or modified meshes require their own physical test.
