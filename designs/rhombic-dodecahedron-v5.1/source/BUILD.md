# Regeneration

Python 3.11 with `requirements.txt` is the reference environment. Use a **new build directory** after changing geometry or resolution; fillets and bare solids are cached within a build.

```sh
python3.11 -m venv .venv
.venv/bin/pip install -r source/requirements.txt
export OPENBLAS_NUM_THREADS=1
export FC_BUILD_DIR="$PWD/build-new"
export FC_RELEASE="$PWD/output/rhombic-dodecahedron-76mm-v5.1-exact-inlays"
export ODA_FILE_CONVERTER="/path/to/ODAFileConverter"
export DWG_TOOL_DIR="/path/to/libredwg/programs"
.venv/bin/python source/build.py
```

`ODA_FILE_CONVERTER` names the official converter executable, inside `ODAFileConverter.app/Contents/MacOS/` on macOS. `DWG_TOOL_DIR` contains GNU LibreDWG's `dwg2dxf`. The reference conversion uses ODA 27.9 and independent reading with LibreDWG 0.14. These external tools are not distributed in this MIT package; obtain them under their own licenses. ODA's macOS command-line runtime needs desktop services.

The pipeline generates the mechanism and fillets, closes screw wells above the screw heads, cuts the foam pockets, splits only the central screw region into a main piece and keyed plug, exports STL/3MF and key samples, checks meshes/motion/assembly/foam/plugs, makes cutting sheets, renders, converts and independently verifies DWGs, writes documentation and hashes, and packages the ZIP. Failed checks prevent packaging.

The order matters: `finish.py`, `caps.py --prepare`, `inlays.py`, `caps.py`, `export.py`. Preparation reads the finished mechanical solids once; do not rerun it over already split centers. Pocket generation saves separate `pocketed-*` caches so `caps.py` splitting is repeatable without destroying its input. Export precedes all checks so those checks use delivered meshes.

To work without the converters, run through `cutting.py` and `render.py` individually; that produces printable parts and DXF/SVG files, not the complete DWG-verified release.

## Controls

- `design.py`: 38 mm rhombic face distance from origin (76 mm opposite faces), concentric retaining shell radii 28.5/33.5 mm, hidden necks 6° narrower than the exterior cones, body gap 0.06 mm and track-cutter expansion 0.37 mm, core, hardware and symmetry. Internal dimensions are fixed rather than scaled with the exterior.
- `caps.py`: simple rounded triangle/square plugs, female across flats 8 mm, triangle/square corner radii 2.25/1 mm, male clearance 0.12 mm per side, tapered ribs protruding 0.04 mm beyond socket flats. T/S flat plug bottoms lie at 36.6/40 mm along their axes. The keyed column alone is split from the pocketed center; the outside rim and most of the floor remain part of the main piece. There are no carrier skirts, outer cup sockets, support spokes or rim pry notches. Foam intentionally spans both parts and is removed before extracting the plug.
- `inlays.py`: 2 mm foam, 2.1 mm recess depth, nominal 1 mm rim, 1.2 mm floor envelope before splitting, 1.6 mm between adjacent-face pockets, 0.775 mm verified lateral envelope, standard +0.04 mm foam contour offset. Center patterns repeat with exact turn symmetry. Shared backing is checked after splitting, allowing only the narrow fit joint to interrupt the pocket floor.
- `printable_inlays.py`: 2 mm rigid inserts from the pocket contours at exact nominal pocket size (zero contour offset); twelve eight-piece STL/3MF face layouts, 96 individual STLs, map, and exported-mesh fit/insertion/contour checks. Run after `cutting.py`; the moving puzzle solids and foam cutting files remain unchanged.
- `cutting.py`: R13 closed POLYLINE DXF, R2000 DWG source, 1:1 SVG, three foam fits, face map and DWG read-back comparison.
- `finish.py` / `ridge_rounding.py` / `flange_rounding.py`: mild edge softening, full R2 petal radial fillets fitted against an unclipped reference, and R1.2 center-flange outline fillets swept radially. No straight-in assembly relief cuts remove spherical shoulders.
- `spherical_report.py`: actual STL bearing-face measurements and inner-foot capture against screwed centers alone.
- `checks.py`: collision-free placement into an expanded shell followed by coordinated contraction, with centers unscrewed. Keep the shell loose until all pieces are engaged; do not assume a last center can enter a tightly fastened puzzle.
- `retention_drawing.py`: true mesh sections through both retaining interfaces.
- `validate_rigid_inlays.py`: all fourteen axes with actual rigid inlays at flush height, plus the coordinated assembly path.
- `validate.py`, `validate_inlays.py`, `validate_caps.py`: checks and their explicit limits.
- `cap_coupons.py`: local key-fit samples using the same profiles and ribs.

All lengths are millimetres. Print transforms appear in the manifest. Do not resize STLs to alter the puzzle size: screw bores, nut slots, washers, track gaps, plug fits and foam thickness must retain their absolute dimensions.
