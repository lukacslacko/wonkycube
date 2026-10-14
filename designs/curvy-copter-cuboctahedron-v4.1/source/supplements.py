"""Small first-print tray using the same delivered plug and center STLs."""
from design import *
from print_3mf import save_3mf
def run():
 (DEST/'start-here').mkdir(exist_ok=True)
 pairs=[('one-center','stl/puzzle/axial-center-print-12.stl',[50,65,0]),('one-plug','stl/puzzle/keyed-plug-print-12.stl',[90,60,0]),('key-test','stl/fit-coupons/plug-key-fit-test.stl',[120,60,0]),('socket-test','stl/fit-coupons/plug-socket-fit-test.stl',[120,90,0]),('paper-test','stl/fit-coupons/paper-pocket-test.stl',[90,90,0])]
 save_3mf(DEST/'start-here/fit-check.3mf',[(name,trimesh.load(DEST/path,force='mesh'),t) for name,path,t in pairs])
 (DEST/'start-here/README.md').write_text('''# Fit check

This optional tray contains one real center and plug, plus the small plug/socket and paper-pocket coupons. These are extras if you also print all four full-puzzle plates.

Print with the same PLA and XY settings you intend to use for the puzzle. Keep XY contour compensation at **0.00 mm** initially. The keyed plugs have 0.12 mm clearance per side and four small crush ribs; the fit should be firm but removable before the paper is applied.

Cut `inlays/fit-test/paper-size-options.svg` or `.dxf`/`.dwg` from your actual laminated paper. Left to right, the outlines are exact size, 0.05 mm inset per side, and 0.10 mm inset per side. All three fit the same coupon. Use the smallest inset that lies flat. The full exact set is in `inlays/faces/`; a full 0.05 mm inset set is in `inlays/fit-variants/easy/`. Do not add contour compensation to the cutting files.

The pocket is 0.5 mm deep, including adhesive. The paper must sit flush or below the plastic rim, not bow up. The coupon's pocket is horizontal: a 0.10 mm layer height reproduces its floor and depth exactly in Z. The puzzle pockets are angled and will have some normal FDM stepping.

The 20 mm calibration square is a separate cut-only file. Check its physical size before cutting all 104 inlays.
''')
if __name__=='__main__':run()
