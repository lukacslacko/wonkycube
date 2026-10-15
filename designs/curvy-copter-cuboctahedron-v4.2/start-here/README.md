# Fit check

This optional tray contains one real center and plug, plus the small plug/socket and paper-pocket coupons. These are extras if you also print all four full-puzzle plates.

Print with the same PLA and XY settings you intend to use for the puzzle. Keep XY contour compensation at **0.00 mm** initially. The keyed plugs have 0.12 mm clearance per side and four small crush ribs; the fit should be firm but removable before the paper is applied.

Cut `inlays/fit-test/paper-size-options.svg` or `.dxf`/`.dwg` from your actual laminated paper. Left to right, the outlines are exact size, 0.05 mm inset per side, and 0.10 mm inset per side. All three fit the same coupon. Use the smallest inset that lies flat. The full exact set is in `inlays/faces/`; a full 0.05 mm inset set is in `inlays/fit-variants/easy/`. Do not add contour compensation to the cutting files. Every sheet includes a removable A4 rectangle: select everything, set width 210 mm and height 297 mm with aspect ratio locked, then ungroup if necessary and delete only the outer rectangle before cutting.

The pocket is 1.0 mm deep, including adhesive. The paper must sit flush or below the plastic rim, not bow up. The coupon's pocket is horizontal: a 0.10 mm layer height reproduces its floor and depth exactly in Z. The puzzle pockets are angled and will have some normal FDM stepping.

The 20 mm calibration square is a separate cut-only file. Check its physical size before cutting all 104 inlays.
