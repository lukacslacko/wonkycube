# Validation and physical feedback

The v7 build printed and assembled well, remained captive and solid, and **now turns quite well after repeated turning**. Initial severe binding on two deep axes improved with use. Its cause was not established. See [physical-feedback.json](physical-feedback.json) for the scope and supplied v7 hashes.

v7.1 replaces only eight C/F outer fillets and offers the compatible 5.25 mm nut-seat core as the new-build default. **The corrected fillets have not been reprinted.** The eighteen W/E STLs are unchanged. The correction is outside the retaining shells; its protected-inner and added-volume checks have residuals below 0.01 mm³. All eight corrected STLs are closed single solids and have connected 0.20 mm / 0.45 mm layer graphs. They passed 520 nominal poses after export, with no detected interference; these reports are in `reports/rounding`.

The current core's archived checks in `reports/core` cover nut loading, antirotation, hardware, the preserved envelope and clearance to the exported v7 outer pieces. Its R19.2 sphere and 17.6 mm axle pads are unchanged. The final assembled release also receives a fresh movement check including the supplied core, screws and washers: `reports/motion.json`. Publication checks cover hashes, complete plates, closed meshes and the 27-piece inventory.

## Baseline v7 checks

The archived v7 motion, assembly, hardware, retention, foot and layer-connectivity checks read the actual exported v7 STLs and restore their solved positions with the transforms in `manifest.json`. Each report records the manifest hash and asserts the STL hashes. The original core is loaded from its existing print mesh.

| Check | Coverage and result |
|---|---|
| Meshes and plates | All 26 new pieces are closed, consistently oriented, single-component solids. Four 3MF plates contain exactly the corresponding STL meshes, without overlaps, within a 256 mm bed. Core and stand reference meshes are unchanged. |
| Turns | 536 sampled poses: all four axes at both depths every 3° from solved, plus a 16-move mixed-depth sequence sampled every 10°. Maximum measured intersection was about 0.0000036 mm³, below the 0.002 mm³ numerical tolerance. Includes the old core, screws and washers. |
| Assembly | 27 paths, 3,483 sampled poses. Each F, E, W can enter radially after its inner families; C enters last. Also checks withdrawal of the optional stand. Maximum measured intersection was 0.000341 mm³. |
| Intended retaining hierarchy | 572 isolated-foot checks across both turn types, every 10° on one tetrahedrally representative axis. Each foot meets its intended holder family, F→E→W→C, by 0.4 mm outward displacement. Minimum peak obstruction within a 2 mm pull was 20.26 mm³. |
| Holder displacement | All 22 floating feet tested against their intended holder family at 0, 0.15 and 0.30 mm outward holder displacement: 66 traces. Every foot remained obstructed, with first contact no later than 0.7 mm and peak overlap at least 86.96 mm³ within a 3 mm pull. |
| Other withdrawal directions | All 22 individual radial pulls plus 243 finite outward/tangential and rocking trajectories on representative W/E/F parts, with C lifts of 0, 0.10 and 0.25 mm. All encountered obstruction. This holds other pieces fixed; it is not a proof against every collective escape path. |
| Hardware | Four M3×20 screw/washer stacks fit the old core, original bearing foot and unchanged washer seat. Washer insertion and driver access checked; original nut capture checked. C stems retain a nominal 1.6 mm upper wall around the access bore. |
| Layer connectivity | All 26 print orientations checked at 0.16 mm / 0.42 mm extrusion width and 0.20 mm / 0.45 mm width: 52 connected layer graphs. This is a model of connected extrusion paths, not a Bambu Studio slice or an overhang/support guarantee. |

The finite collision tolerance is a numerical Boolean-volume threshold, not an additional mechanical clearance.

## Bearing webs and necks

The E/W bearing webs are non-retaining spherical backstops. Their nominal inner radius is 19.4 mm around the old 19.2 mm core. The guide primitives were tested against the exact old core, including its nut channels, at **1,968 moving-web poses**, every 3° across all four axes and both turn depths. At every sampled pose, an inward shift of 0.25 mm met the core. The smallest intersection at that shift was 0.254 mm³, increasing to 1.217 mm³ at 0.4 mm in that weakest pose. This gives evidence that the webs bridge the old nut openings rather than dropping into them. It is not a contact-pressure or wear analysis.

A 0.6 mm radius morphological erosion of the common internal C/W/E/F geometry leaves each captured foot connected to its outer body. The same probe on complete guided canonical E/W bodies leaves the near-core bearing portion connected to the main attachment. This is an approximate 1.2 mm connected-thickness probe of faceted geometry, not a mechanical strength simulation. Guide additions are unioned with more than 3 mm³ attachment volume; individual values are in `bearing-attachments.json`.

Opening the receiving grooves for assembly removes **zero volume from the protected captured-foot regions** in the preparation step. The following rounding intentionally softens their edges. The footprint study compares assembly-relief openings on 68/70/72/74 mm cube skins; 72 mm keeps the meaningful assembly openings internal. Tiny Boolean/facet slivers remain in that diagnostic, rather than literal zero area.

## Scope of the conclusion

These checks support a printable, geometrically captured mechanism with the requested assembly order and legal sampled turns. They do **not** establish zero play, smooth friction under load, support quality, fatigue strength, or exhaustive motion/escape behavior in every scramble. The physical build now supplies qualitative evidence of capture, assembly and turning after bedding-in. The eight revised exterior fillets have not yet been physically reprinted.

These original reports are preserved in `reports/baseline-v7`, with their original manifest in `reference/baseline-v7-manifest.json`. They must not be mistaken for newly computed v7.1 reports.
