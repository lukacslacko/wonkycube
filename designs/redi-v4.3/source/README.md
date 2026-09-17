# Compact Redi v4.3 CAD

This is the published 64 mm design with the owner's radial-down edge print pose.
The owner has built it and likes its feel apart from loose nut seats. The planned
core-only tighter terminal nut seat is **not implemented** here. See the
[design description](../README.md#known-core-issue-nuts-can-spin).

All lengths are millimeters. Python 3.11+; install `requirements.txt` in a virtual
environment. No OpenSCAD process is used.

```sh
python build.py --from-masters --validate --out ../my-compact-redi-build
```

Choose a new output folder. `build.py` refuses to overwrite an existing one.
It writes intermediate files under `cache` and printable files under `release`
inside that folder. Rendering and full geometric checks take time.

The supplied `masters` hold the checked canonical C and E inner mechanisms and
the R3 sectional records. Omit `--from-masters` to reconstruct these too. Changing
dimensions or tolerances requires a full reconstruction: do not reuse old masters
after changing their parameters.

- `redi_design.py`: 64 mm size, Redi rail profile, 0.03 mm main gap, 0.40 mm swept
  track expansion, inner rounding, core, nut slots, hardware, and fit coupons.
- `mechanism_v4p2.py`: inherited constant-radius transverse ridge construction,
  including stepped track sections; configured by the new generator.
- `finish_redi.py`: actual rotated cube clipping and outer softening, with the
  exterior opening applied before the radial-ridge subtraction as in v4.2.
- `export_redi.py`: print orientations, closed STL export, manifests, 3MF plates.
- `validate_redi.py`: reloaded-STL motion, assembly, hardware, retention, plates.
- `check_ridges_and_shapes.py`: sectional radii and all 66 exterior shape pairs.
- `render_redi.py`: software-rendered previews and actual CAD hardware sections.

The source retains helper modules from v4.2 under the same MIT license. Their
historical constants are not this revision's dimensions; use `redi_design.py`.
`chosen_rotation.json` records the original orientation search at 100 mm and is
retained as provenance. This revision keeps that orientation and checks distinct
edges on the exported compact geometry; it does not rerun the optimization.

Mesh simplification and export cleanup are limited to small numerical tolerances;
the acceptance checks use the reloaded print files. They do not establish physical
friction, holding force, wear, or an exhaustive collision-free motion proof.

The edge print orientation is radial inward down (−Z); the exporter aligns each
edge’s outward mechanism direction to +Z. Other parts keep their previous print
orientations. Changing this print pose does not change the puzzle geometry.

The supplied print meshes preserve the delivered reorientation exactly. A fresh
CAD export can differ in yaw, triangle ordering and numerical cleanup; use the
geometry checks to evaluate it rather than assuming byte-identical output.
`build.py` produces geometry and reports, not a new physical-print endorsement.
