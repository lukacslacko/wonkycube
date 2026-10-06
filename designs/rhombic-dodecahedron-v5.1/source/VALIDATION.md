# Physical build and geometry checks

The owner reports that the complete puzzle **printed and built very well, and turns smoothly**. The published main-piece, petal, plug and core STLs are byte-identical to that supplied build. The [physical-feedback record](../physical-feedback.json) distinguishes this direct build report from the CAD checks and lists the associated hashes.

The owner printed the rigid inlays both at the supplied reduced size and with **+0.15 mm contour compensation** cancelling the reduction. The compensated inserts fit **very nicely snugly**; the reduced ones were noticeably less satisfactory. The published inserts therefore use the **exact original pocket contours**, with zero contour offset and 2 mm thickness. Print them with **0.00 mm XY contour compensation**. The exact regenerated toolpaths were not separately reprinted; their nominal fit is supported by that physical comparison.

## What was checked

- The main puzzle has 53 printed parts including the core and fourteen keyed plugs, forming 38 moving units. All delivered individual STLs are closed and connected. Each face-inlay STL deliberately contains eight separate closed inserts.
- All fourteen axes clear at 3° sampling intervals with hardware present. Threefold axes turn 120°, fourfold axes 90°. Destination symmetries, washer-root walls, screw/nut reach and nut loading are checked.
- Retention probes include intermediate turns, outward/tilted extraction and the inner petal feet against screwed centers alone with 0.15 mm center lift. Measured inner spherical bearing area is approximately 161 mm² per threefold center and 232 mm² per fourfold center.
- A constructive assembly check inserts pieces into an expanded loose shell, then contracts it with centers unscrewed. Physical assembly was also reported successful; the numerical sequence is not a measurement of the exact hand sequence used.
- Layer connectivity covers 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width combinations. These are geometric checks, not recorded Bambu toolpaths.
- Keyed plugs clear the screws, resist unintended rotation and can be removed after the relevant inlays are removed. The inlays bridge the plug/base joint.
- Exact-size printed inlays are reloaded from their STL exports and checked against the original pocket contours. At nominal contact, an inset audit probe excludes a 0.006 mm skin to account for the body's bounded 0.005 mm mesh simplification; this does not reduce the delivered inlays. Installed exact inlays are tested at flush height through all fourteen axes and the assembly path.
- All 38 DWG sheets were encoded with ODA and independently read back with LibreDWG. DXF contours are closed, SVG units are millimetres, and the foam cutting files are unchanged.

The reports describe finite rigid-geometry checks. They do not measure hand torque, print roughness, elasticity, adhesive strength, fatigue or every possible escape path. Physical feedback supplies the separate evidence about assembly and smooth turning. Original numerical reports retain their scope at the time of computation; the build status above records the later user report.
