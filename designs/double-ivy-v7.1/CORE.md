# Replacement double-Ivy core with current nut seats

Print **`stl/puzzle/core.stl`** for the current default nut fit. It has **5.25 mm final seats**, **5.85 mm loading entrances**, a 3.0 mm tight channel measured from the screw axis, and a 3.0 mm taper to the entrance. This is the pocket profile used in the recent cuboctahedron designs, adapted to the double Ivy's original core dimensions.

The older double-Ivy core has 5.40 mm final seats. The replacement narrows the seat by 0.15 mm total (0.075 mm per side), while preserving easy entry. An optional **5.20 mm** version supplies the firmer fit used in the successful pentagonal-prism build. Print only one core; both options fit the same puzzle.

## Files

- `stl/puzzle/core.stl`: recommended core.
- `stl/optional/core-nut-seat-5.20.stl`: tighter alternative.
- `stl/fit-coupons/nut-fit-5.25.stl` and `stl/fit-coupons/nut-fit-5.20.stl`: small fit coupons.
- `plates/core-01.3mf` and `optional-plates/core-nut-seat-5.20.3mf`: one-core print plates.
- `optional-plates/nut-fit-coupons.3mf`: both coupons, individually named.
- `reference/reused-core/core.stl`: old core for comparison; **do not print this for the upgrade**.

STLs are already oriented with a flat axle pad on the bed. Files use millimetres: print at **100% scale**. The 3MFs contain geometry and placement only. Use your established P1S / 0.4 mm nozzle process; 0.20 mm layers and four walls are a reasonable starting point. Inspect the nut-slot roofs in the slice and remove any reachable support residue before inserting nuts.

## Compatibility and hardware

Only the core needs reprinting. It preserves the **R19.2 spherical envelope**, four tetrahedral screw axes, **17.6 mm axle-pad distance**, **3.4 mm core bores**, and **15.65 mm nut-roof coordinate**. The nut slots remain 4.25 mm high, leaving the same nominal 1.95 mm roof below each pad.

Use this with the double Ivy's original one-piece-core outer sets, including spherical **v6 at 64 mm** and layered spherical **v7 at 72 mm**. It is not a grooved or split core. Do not substitute a complete cuboctahedron or prism core merely because its nut slots are similar; those cores have different axes or dimensions.

Keep the same **four DIN912 M3×20 screws, four DIN985 M3 nuts and four 9×1 mm washers**. The outer pieces and screw seats stay unchanged. The nominal screw still reaches 3.35 mm beyond the nut's inward face with a seated washer.

The nut's metal face points toward the screw entry; its nylon locking end faces inward. Slide through the wide opening and push fully into the narrower terminal seat with a blunt tool. Keep the nut square. A nominal 5.5 mm nut intentionally interferes with these seats: 0.25 mm total at 5.25, or 0.30 mm at 5.20. The coupon should accept the nut fully without cracking and stop it rotating as a screw passes through the nylon ring. Choose the tighter option if the 5.25 coupon is loose; inclined slots and real nut tolerances can differ from a flat coupon.

## Checks

Both exported cores and coupons are watertight, single-component solids. The replacement was checked against the exact old core: meaningful changes are confined to the nut-pocket regions, with only STL quantization differences elsewhere. Nut-loading gauges, nominal press interference, anti-rotation geometry, screw passage and all four bearing lands were checked.

Compatibility with the actual exported v7 outer pieces is checked using clearance bounds: all floating parts stay outside the core sphere during rotation, and each screwed center stays above its own flat axle pad. Outward radial insertion preserves those separations. This core revision does not alter the flange mechanism or its clearances. Print-plate meshes match the STLs exactly; see `reports/core/validation.json`.

The exact core variant installed in the reported build was not restated. Both supplied variants have geometric checks. The pocket dimensions come from recent builds; they do not guarantee resistance to long-term plastic wear or nut rotation for every printer/nut combination.

## Regeneration

See [BUILD.md](BUILD.md). The original one-piece core can still be reused. The owner requested this tighter replacement before the reported successful build; the exact core variant installed was not restated.
