# Validation of the delivered print files

**All listed checks completed on the exported and reloaded meshes.** On **2026-09-27**, the owner reported that this **64 mm non-wavy triangular prism printed, assembled and turns well**. The [physical feedback record](physical-feedback.json) identifies the associated supplied STL files. Exact slicer settings and the chosen optional core were not restated; no endurance or holding-force measurement was reported. The reports are tied to the SHA-256 of `manifest.json`; every STL also has its own recorded hash.

| Check | Result |
|---|---|
| Main puzzle STLs | 21 closed, consistently wound, positive-volume single components |
| Alignment | Same cube rotation as the pentagonal prism, with five D3 turn axes |
| Turning | All 5 axes, then 24 mixed moves; 909 sampled configurations |
| Largest measured turn overlap | 2.2e-05 mm³ (acceptance limit 0.001 mm³) |
| Assembly | 21 radial insertion/stand removal paths, 1659 positions, including core and installed hardware |
| Largest measured assembly overlap | 0 mm³ |
| Washer lands and feet | Full annuli present; shaft, washer loading and hex-key access clear |
| Tight nut loading | Easy entrance, deliberate interference at terminal flats, roof support and rotational obstruction checked |
| Center stalks | Continuous cylindrical annulus around screw passage checked |
| Washer-well roots | Minimum sampled web 3.92 mm |
| Screw heads | Minimum nominal clearance to cube faces 0.58 mm |
| Floating part retention | First aligned rigid radial obstruction at 0.35–0.45 mm of displacement |
| Off-axis retention | Angled pulls and combined rocking/extraction, including 0.10/0.25 mm center lift |
| Mid-turn retention | 30 sets of 13 rigid pull directions across both move families and 0/0.10 mm center lift |
| Separated-neighbor corner capture | All six corners, 13 directions, 0.10 mm screwed-center lift and 0/0.20 mm outward shift of every other floating piece; obstruction curves to 6 mm |
| Radial rounding | R2 exposed arcs checked at 3196 transverse sections, including tracks; worst measured radius error 0.025 mm |
| Layer connectivity | Every main print orientation at 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width pairs; no secondary printable component above 0.03 mm³ |
| Print plates | Bounds, non-overlap, units and alternate-orientation mesh equivalence checked |

The tip-trimming report records tiny components already detached after rounding. The terminal-trimming report separately records the deliberate removal of about 11.57 mm³ per corner at the three flange tips, eliminating nonprinting webs while retaining broad capture lobes. All checks here use the trimmed exports. Root-web and annulus checks are geometric measurements, not finite-element strength calculations.

The radius check follows the matching circular-arc boundary when a cross-section has multiple intersections. Near-tangent sections can gain or lose a foreground intersection under tiny mesh regularization; comparing only the first intersection can incorrectly compare unrelated surfaces. Independent bidirectional surface samples constrain export fidelity as well.

Motion is sampled every 3° from solved positions and every 6° in the mixed-move sequence. The cuts are surfaces of revolution and the move endpoints respect the D3 axis symmetry; the numerical checks additionally cover the actual clipped, rounded, exported parts and hardware. These checks are not an exhaustive search of every puzzle state or every possible elastic escape path.

Track gaps, nut press fits, friction, screw preload, layer adhesion and support removal still depend on the real print. Fixed-width layer connectivity is not a Bambu Studio toolpath simulation and does not eliminate the need for supports. Print the nut and rotor fit coupons before the complete puzzle. Use gentle initial turns and adjustment; no physical load or lifetime rating is claimed.
