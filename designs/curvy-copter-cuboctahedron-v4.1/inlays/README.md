# Cut the laminated-paper inlays

These are the cutting shapes for the **72 mm Curvy Copter cuboctahedron with 0.5 mm pockets**, v4.1. There are **104 inlays**: eight on each of six square faces, and seven on each of eight triangular faces. Cut each of the 14 face sheets once, using the color you want for that face. `S` names square faces; `T` names triangular faces. `+` and `-` indicate face directions, not extra copies.

## Silhouette Cameo on Windows

1. Download the **curvy-copter-cuboctahedron-v4.1-inlays.zip** release asset and choose **Extract All** in Windows. Open the files from the extracted folder.
2. Use **DXF** in Silhouette Studio Basic Edition. SVG is another option with Designer Edition or above. The genuine DWG files are supplied for CAD software; DXF is the straightforward Cameo option. Silhouette documents its [supported file types](https://silhouetteamerica.freshdesk.com/support/solutions/articles/35000282776-file-types-and-features).
3. Open `fit-test/calibration-20mm.dxf` from within Studio. Select its outline and verify **20.00 x 20.00 mm**. Cut it and measure it. Use your laminated stock and an appropriate blade/material test; no machine-specific speed, force or pass count is embedded in these files.
4. Open a face file from `faces/`. Before moving or rotating any outlines, select **all its outlines together**. Lock the aspect ratio, set the selection width to the value in the [bounding-box table below](#dxf-selection-bounding-boxes), and check that its height matches. Check every imported sheet; do not resize the individual inlays separately. Silhouette notes that [DXF import can change scale](https://silhouetteamerica.freshdesk.com/support/solutions/articles/35000276938-importing-and-exporting-troubleshooting); do not rely on fit-to-page. The supplied DXFs are R13 ASCII closed 2D polylines with millimetre coordinates.
5. Keep **zero contour offset** initially. The `faces/` set matches the pocket contours exactly. Cut the small `fit-test/paper-size-options.dxf` first: its left, middle and right outlines are exact size, 0.05 mm inset per side and 0.10 mm inset per side respectively. For material that binds at exact size, `fit-variants/easy/` provides a complete 0.05 mm inset alternative. Choose one face set, not both.
6. The files contain only the cut paths: no lettering or registration marks. Use the [face map](../images/face-map.png) to keep each outline with its face and piece. Do not trace or cut the illustration. Check the cut preview before sending it to the Cameo.
7. Test and tension the assembled puzzle, insert the keyed plugs, then fit the laminated paper. **Paper, laminate and adhesive together must fit within 0.5 mm.** Use a thin adhesive layer if needed. Four inlays on each screwed center span its plug joint; remove those inlays before accessing the screw. No inlay bridges a moving puzzle-piece seam.

## DXF selection bounding boxes

All dimensions below are **millimetres**, measured directly from the DXF cut paths in their original orientation. Each row gives the bounding box of **all contours in one file selected together**. It is not the blank page size, the outer puzzle-face size, or the size of an individual inlay. The same dimensions apply to every file in the indicated group.

| DXF files | Contours per file | Width (mm) | Height (mm) |
| --- | ---: | ---: | ---: |
| `faces/SX+.dxf`, `SX-.dxf`, `SY+.dxf`, `SY-.dxf`, `SZ+.dxf`, `SZ-.dxf` | 8 | 68.781578 | 68.781578 |
| All eight `faces/T*.dxf` triangular-face files | 7 | 46.751362 | 40.683169 |
| All six `fit-variants/easy/easy-S*.dxf` square-face files | 8 | 68.679619 | 68.679619 |
| All eight `fit-variants/easy/easy-T*.dxf` triangular-face files | 7 | 46.649839 | 40.582625 |
| `fit-test/calibration-20mm.dxf` | 1 | 20.000000 | 20.000000 |
| `fit-test/paper-size-options.dxf` — all three test outlines together | 3 | 57.900000 | 10.000000 |

The default `faces/` files use the exact pocket contours. The optional `easy-` files inset each contour by 0.05 mm per side; use their own dimensions if choosing that set. [sheet-dimensions.csv](sheet-dimensions.csv) lists every filename individually.

Entering these dimensions rounded to **0.001 mm** is sufficient. If the height does not match after setting the width with the aspect ratio locked, check that all contours from exactly one file are selected and that none have been rearranged or rotated. A 90-degree rotation swaps width and height; do not stretch the drawing independently in X and Y to compensate.

All SVG/DXF/DWG contours are the delivered v4.1 shapes. The full package includes the matching STL pocket test. Cut-file structure and DWG round trips were checked. The owner reports that Silhouette Studio imports the DXFs enlarged; use the dimensions above to restore their intended size. Physical cutting results and material fit on the owner's Windows/Cameo setup are not yet confirmed.
