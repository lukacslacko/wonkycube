# Rebuild

This is an exterior adaptation of the successful spherical-retention Curvy Copter cuboctahedron. It starts from the four SHA-verified, delivered STL masters in `fixed-baseline/`. Their print transforms are inverted before construction. `prepare.py` deliberately preserves the proven internal mesh geometry; it only fills the central screw well above the screw head so a small keyed plug can be separated from it. The retaining mechanism is not regenerated from approximate parameters. `rounding_repair.py` completes the missing halves of five symmetric R2 radial fillets: two on C and three on K. It uses the saved circle centers and radii, extending each arc to the larger of its two tangent angles on both sides. The four separate R1.2 mixed-side center-flange fillets are not altered. The paper contours in `rounding-reference/pockets-v4.json` remain fixed, and their complete backing envelopes are checked against the repaired solids.

Use Python 3.11 or newer with `requirements.txt`. From the containing project directory:

```sh
python -m venv .venv
.venv/bin/pip install -r source/requirements.txt
export OPENBLAS_NUM_THREADS=1
export CUBOCTA_BUILD_DIR="$PWD/build"
export CUBOCTA_RELEASE="$PWD/rebuilt"
export MPLCONFIGDIR="$PWD/build/matplotlib"
.venv/bin/python source/build.py
```

Choose fresh build/release directories. The supplied defaults in `inlays.py` are 0.5 mm pocket depth, 0.8 mm nominal perimeter rim, 1.2 mm minimum backing web, 1.2 mm between adjacent face pockets, and exact paper contours. The laminate plus adhesive must fit inside the pocket depth. `caps.py` defines the 12 × 10.4 mm rounded rectangular key, 0.12 mm side clearance, and localized 0.04 mm interference ribs. The key bottom is at 38 mm along the turn axis, 3 mm above the screw head.

Run `validate.py` whenever dimensions or delivered geometry change. It reloads the actual STL files. Reports cover watertightness/connectivity, preservation of the repaired retaining geometry through pocketing, pocket backing, plug removal, washer/driver access, key rotation, thin-feature layer connectivity, 74 capture probes, all 12 ordinary half turns, the five-step jumble, and a 48-step legal jumbling sequence. Sampling is finite, not a force or fatigue model. Shell assembly inherits the physical assembly evidence of the unchanged mechanism; the new plugs are tested by straight insertion from outside with their paper removed.

`cutting.py` writes 1:1 SVG and R13 ASCII closed-POLYLINE DXF files. It also puts R2000 DXF sources in `$CUBOCTA_BUILD_DIR/cache/dwg-source`. To regenerate genuine DWGs with an installed ODA File Converter:

```sh
ODAFileConverter "$CUBOCTA_BUILD_DIR/cache/dwg-source" "$CUBOCTA_BUILD_DIR/cache/dwg-output" ACAD2000 DWG 0 1 '*.dxf'
export DWG_TOOL_DIR=/path/to/libredwg/programs
.venv/bin/python source/cutting.py --verify-dwg
```

The verifier independently reads each DWG with LibreDWG and compares every closed contour against its source DXF. DXF/SVG need no DWG converter. Do not rename a DXF file to `.dwg`.

The source and fixed baseline are MIT-licensed. Baseline mechanism source is retained in the public `lukacslacko/wonkycube` repository under `designs/curvy-copter-cuboctahedron-v3.2/source`.

## Half-arc regression

A fit that chooses all tangent points within a tiny tolerance of a single maximum can select only one side of a nominally symmetric dihedral. Cutting only from that tangent to the middle of the arc leaves a thin hook on the opposite side. For genuinely symmetric sections, complete both angular extents; do not force that symmetry on offset or mixed-side flange corners. Inspect both sides of the delivered fillet, including where it meets spherical tracks and the exterior, not just its middle point.

`check_rounding.py` compares the actual v4 and v4.1 meshes, checks every completed cutter for remaining material, and measures both half-arcs at a strongly affected full-arc section per family. It also checks that petals/core are byte-identical, plugs have unchanged geometry, and every paper contour is identical. `retention_v2.py` repeats capture checks across solved, partially turned and jumbled states using only the actual feet below R28.5. The spherical bearing faces away from the local edge fillets remain intact. The corner's protected 3.3 mm spine is untouched.
