# CAD and reproduction — 80 mm v4.2.1

This directory and the root `scripts/reproduce.py` reproduce the older 80 mm
version. For compact v4.3 use [its source and build instructions](../designs/redi-v4.3/source/README.md).

Python 3.11 was used for the publication export. Dependencies are pinned in [requirements.txt](../requirements.txt). No OpenSCAD or proprietary CAD runtime is required.

From the repository root:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/reproduce.py --out build/reproduced
```

On Windows, use `.venv\Scripts\python.exe`. The reproduction script builds into a new directory and runs the mechanism, revision, radius and shape checks. It stops on any failure and will not overwrite an existing output directory. Computation can take several minutes. Exact STL byte ordering can depend on library/platform details; the geometric checks are the acceptance criteria. Released file hashes identify the specific checked export.

## Source map

| File | Role |
|---|---|
| `mechanism.py` | Shared geometry, axes, transforms and original prototype primitives |
| `poc_mechanism.py` | Direct-to-plastic screw core and early flat-foot prototype |
| `mechanism_v3.py` | 80 mm stepped-rail geometry, proper feet, exterior rounding and hardware envelopes |
| `exact_assembly_sweep.py` | Nonconvex axial insertion envelope |
| `mechanism_v4.py` | Unrounded flange sweep, wider tracks and internal rounding |
| `mechanism_v4p1.py` | Earlier 2 mm ridge fillets with an inner blend |
| `mechanism_v4p2.py` | Constant 3 mm transverse ridge fillets following the inner track |
| `build_v4p2.py` | Current export, using the fixed v4.1 baseline |
| `v3_io.py` | Closed STL export and geometry-only 3MF writer |
| `verify_v3.py` | General saved-mesh, motion, hardware and assembly verifier (name retained) |
| `verify_v4p2.py` | Revision locality, mixed old/new motion, retention and misalignment probe |
| `verify_radii_v4p2.py` | Section fits on the actual print STLs |
| `check_edge_shapes_v3.py` | All 66 edge-exterior pair comparisons |
| `optimize_rotation.py` | Original exterior-orientation search |
| `draw_v4p2.py`, `mesh_render.py` | Actual mesh-section diagrams and software-rendered previews |

## Changing the design

The fast current build starts from [baseline](baseline), not from a single fully parametric solid. That is intentional: the latest revision removes only ridge material while preserving printed interfaces. Adjust `RADIAL_RIDGE_ROUND` in `mechanism_v4p2.py` to experiment with that cut, then update the radius verifier's explicit target and rerun all relevant checks. A bigger radius can remove retention material and is not automatically safe.

To change the exterior, hardware, core or original rail, rebuild the chain from its source. Run these from the repository root, using fresh output paths:

```sh
.venv/bin/python cad/build_v3.py --out build/v3p1
.venv/bin/python cad/build_v4.py --base build/v3p1 --out build/v4
.venv/bin/python cad/build_v4p1.py --base build/v4 --out build/v4p1
.venv/bin/python cad/build_v4p2.py --base build/v4p1 --out build/new-design
```

These earlier generators are preserved for design work. The publication check starts at the supplied baseline; a complete fresh upstream rebuild is not claimed byte-identical to historical archives. Rounding is expensive, and parameter changes can produce thin/disconnected geometry that requires redesign rather than export repair. Validate each stage before relying on the next. Any source constants used by verification must agree with the generated geometry.

The original optimization uses a 100 mm cube for scoring. Uniform exterior size changes scale those scores, not the selected orientation. Its `rotation.json` output is an exploration result; the retained `chosen_rotation.json` also includes an equivalent symmetry relabeling. Do not automatically replace the chosen rotation when reproducing the released shape.

For individual current checks:

```sh
.venv/bin/python cad/verify_v3.py --out models/current
.venv/bin/python cad/verify_v4p2.py --base cad/baseline --out models/current
.venv/bin/python cad/verify_radii_v4p2.py --out models/current
.venv/bin/python cad/check_edge_shapes_v3.py --out models/current
```

These commands rewrite their JSON reports. Use a copied output folder when preserving a published checksum manifest.
