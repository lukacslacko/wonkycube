# Printable 2 mm inlays

For the 76 mm vertex-turning rhombic dodecahedron, spherical v5.1 with 2.1 mm pockets. Mix these with the 2 mm foam inlays on any faces. The puzzle parts do not need reprinting.

Open **faces/F01.3mf** through **faces/F12.3mf** for the colors you want to print. Each file contains eight separate inlays for that rhombic face, positioned as viewed from outside. The matching **F01.stl–F12.stl** files contain the same eight disconnected inserts. Print each chosen face once, using either its STL or its 3MF. Do not print both. There is no connecting backing sheet or sprue.

For one replacement insert, use **individual/Fxx/Fxx-PieceID.stl**. The placement map identifies the destination pieces; the inlays themselves carry no printed labels. Keep each face's pieces together after removing them from the bed.

Print at **100% scale**, lying flat as supplied, with the visible side upward. On the P1S with a 0.4 mm nozzle, use your PLA profile, **0.20 mm layers and at least five top and five bottom layers** to make the 2 mm insert solid. No supports or brim are needed. Inspect the first-layer preview, keep elephant-foot compensation enabled, and print one face first to test the fit. The 3MF files contain geometry, not printer or filament presets.

The rigid inlays are **2.00 mm thick and exactly match the nominal pocket outline**, with **no size reduction or enlargement**. Set **XY contour compensation to 0.00 mm** for these files: do not add the earlier +0.15 mm correction. The owner found the nominal-size fit nicely snug; the reduced tiles were noticeably looser. A little glue remains optional. Without adhesive the top sits 0.10 mm below the plastic; use only a thin adhesive layer so it stays flush or recessed. Do not force a tight insert: remove any first-layer burr and test again. Foam and plastic can share the same puzzle without changing its turning geometry.

On screwed centers, an inlay bridges the main piece and central plug. Finish screw adjustment before gluing it. Avoid glue in the key socket and moving seams; removal of an inlay may be needed for later screw access. The cutting sheets remain the foam versions and should not be used to size rigid plastic.

`manifest.json` lists face contents and individual file mappings. Geometry checks cover the exported STLs, nominal contour fidelity, insertion and installed motion. The full puzzle is reported to build very well and turn smoothly. Nominal-size inlay fit was demonstrated by applying +0.15 mm contour compensation to the previous reduced tiles; these exports directly use the original pocket contour, without requiring that slicer correction. Exact regenerated toolpaths were not separately reprinted.
