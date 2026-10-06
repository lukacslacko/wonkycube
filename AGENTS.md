# Design defaults

For new puzzle designs and retention revisions, the owner's default is **concentric spherical-shell retaining shoulders centered on the puzzle origin**. The broad surfaces that hold floating pieces down must be perpendicular to the local radius. Exterior cuts may still be conical, planar or wavy. Flat washer seats and matching axle-bearing pads are separate interfaces and remain appropriate.

Preserve substantial overlap after swept-track clearance, rounding and assembly access. Round flange ends in their radial outline without unnecessarily rolling away the spherical bearing lands. Keep close body clearance separate from supported sliding-track clearance. Check the delivered meshes for capture by the actual retainers, legal motion, layer connectivity, hardware fit and an assembly path. Report physical print evidence separately from CAD checks.

Use **5.25 mm terminal across flats** for the confirmed DIN985 M3 nut seat, with the wider mouth and tapered lead-in specified in `docs/design.md`. Do not treat a loose entrance as a reason to enlarge the terminal seat.

Read `docs/mechanism-principles.md` for the reusable geometry and validation guidance. These are defaults; an explicit user request may change them.

For the rhombic-dodecahedron v5.1 rigid inlays, use **exact nominal pocket contours**, 2 mm thickness and **zero contour offset**. Do not reinstate the earlier 0.15 mm shrink allowance. These files are sliced with **0.00 mm XY contour compensation**; the owner’s snug-fit evidence came from cancelling the earlier reduction. Foam cutting allowances are a separate setting.
