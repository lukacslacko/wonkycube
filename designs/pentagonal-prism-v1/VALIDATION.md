# Validation of the delivered print files

**All listed checks completed on the exported and reloaded meshes.** The owner subsequently reported successful physical assembly and well-tuned nut-slot fit on 2026-09-23. See [physical feedback and print settings](physical-feedback.json). This is not a measured turning-force, strength or lifetime test. The reports are tied to the SHA-256 of `manifest.json`; every STL also has its own recorded hash.

| Check | Result |
|---|---|
| Main puzzle STLs | 33 closed, consistently wound, positive-volume single components |
| C05/C06/C07 alignment | Plane x+y=0; minimum rotation 5.67233332° |
| Turning | All 7 axes, then 24 mixed moves; 919 sampled configurations |
| Largest measured turn overlap | 1.27e-05 mm³ (acceptance limit 0.001 mm³) |
| Assembly | 33 radial insertion/stand removal paths, 2607 positions, including core and installed hardware |
| Largest measured assembly overlap | 1.96e-05 mm³ |
| Washer lands and feet | Full annuli present; shaft, washer loading and hex-key access clear |
| Tight nut loading | Easy entrance, deliberate interference at terminal flats, roof support and rotational obstruction checked |
| Center stalks | Continuous cylindrical annulus around screw passage checked |
| Washer-well roots | Minimum sampled web 1.62 mm |
| Screw heads | Minimum nominal clearance to cube faces 0.58 mm |
| Floating part retention | First aligned rigid radial obstruction at 0.40–0.55 mm of displacement |
| Off-axis retention | Angled pulls and combined rocking/extraction, including 0.10/0.25 mm center lift |
| Mid-turn retention | 30 sets of 13 rigid pull directions across both move families and 0/0.10 mm center lift |
| Radial rounding | R2 exposed arcs checked at 5233 transverse sections, including tracks; worst measured radius error 0.023 mm |
| Layer connectivity | Every main print orientation at 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width pairs; no secondary printable component above 0.03 mm³ |
| Print plates | Bounds, non-overlap, units and alternate-orientation mesh equivalence checked |

The tip-trimming report records only tiny components that were already detached after rounding. They are deliberately absent from the print files. Root-web and annulus checks are geometric measurements, not finite-element strength calculations.

Motion is sampled every 3° from solved positions and every 6° in the mixed-move sequence. The cuts are surfaces of revolution and the move endpoints respect the D5 axis symmetry; the numerical checks additionally cover the actual clipped, rounded, exported parts and hardware. These checks are not an exhaustive search of every puzzle state or every possible elastic escape path.

Track gaps, nut press fits, friction, screw preload, layer adhesion and support removal still depend on the real print. Fixed-width layer connectivity is not a Bambu Studio toolpath simulation and does not eliminate the need for supports. Print the nut and rotor fit coupons before the complete puzzle. Use gentle initial turns and adjustment; no physical load or lifetime rating is claimed.
