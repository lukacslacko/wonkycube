# Cut the 1 mm-pocket Curvy Copter inlays

These files match the **72 mm Curvy Copter cuboctahedron v4.2 with 1.00 mm pockets**. Their contours were regenerated to leave adequate plastic between the deeper pockets. Recut from this set; the earlier 0.5 mm-pocket outlines are not the matching size.

There are **104 inlays**: eight per square face and seven per triangular face. Cut each of the 14 files in `faces/` once, in your chosen face color. `S` names the six square faces and `T` the eight triangular faces. The signs distinguish face directions, not extra copies.

## Silhouette Studio on Windows

1. Extract the ZIP and open a **DXF** from the extracted folder. DXF is suitable for Basic Edition; SVG is an alternative for editions that support it. DWG copies are also supplied for CAD software.
2. Every file contains its inlay outlines plus **one large A4 rectangle**. Before moving, rotating or deleting anything, select **all objects from that file together**.
3. **Lock the aspect ratio. Set width to 210 mm and check height is 297 mm.** These are the centerline bounds of the imported paths. If the drawing was rotated 90°, width and height are swapped; restoring its original orientation avoids confusion. Do not stretch X and Y independently.
4. Ungroup if needed and **delete only the outer A4 rectangle**. It is one closed outline, separately identified in the DXF/DWG layer or SVG group as `A4_FRAME_DELETE_BEFORE_CUTTING`. Do not assume the cutter ignores that layer automatically. Check the cut preview: only the inlay contours should remain.
5. Rearrange the inlays on your material only after restoring their scale. The A4 frame is a sizing aid; you can then move the inlays onto a smaller scrap or another mat size without resizing them.
6. Start with `fit-test/calibration-20mm.dxf`. Scale and remove its A4 rectangle as above, then cut and measure the remaining **20 × 20 mm** square. Test `fit-test/paper-size-options.dxf` with your laminated paper: left to right, its three outlines are exact size, 0.05 mm inset per side and 0.10 mm inset per side.
7. Keep **zero contour offset** for the default `faces/` files. If the exact contour binds, `fit-variants/easy/` has a full set inset 0.05 mm per side. Choose one complete face set.
8. Use the [face map](../images/face-map.png) to keep each inlay with its piece. Labels appear only on the map, which is not a cutting sheet. Tune the puzzle and fit the screw plugs before applying paper. Laminated paper plus adhesive must fit within **1 mm**.

## Import bounding boxes

| Files | Width with A4 frame (mm) | Height with A4 frame (mm) |
| --- | ---: | ---: |
| All `faces/*.dxf` | **210** | **297** |
| All `fit-variants/easy/*.dxf` | **210** | **297** |
| Both `fit-test/*.dxf` files | **210** | **297** |

The same A4 frame is included in SVG and DWG. [sheet-dimensions.csv](sheet-dimensions.csv) lists each sheet and also gives the inlays-only bounding box, useful as a second check after deleting the rectangle. Always scale using the frame while it is still present.

The cutting files were reloaded and checked for closed contours and exact A4 bounds. Genuine DWGs were independently read back and compared with their source geometry. The 1 mm-pocket parts and these regenerated outlines have not yet been physically tested together on the owner's printer and Cameo.
