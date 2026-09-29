# Physical build and geometry checks

On **2026-09-29**, the owner reported: **“The cuboctahedron curvy copter shape mod printed and built very well.”** This confirms successful full printing and assembly. Earlier spherical-retainer test pieces were also reported to work well with the old core. The [physical-feedback record](physical-feedback.json) associates the report with the supplied v3.2 files; exact final slicer settings and optional/reused core selection were not independently verified.

The publication preserves every supplied STL, 3MF, manifest, geometry-generating source file and original numerical report byte for byte. `publication.json` records their hashes. Original reports saying “not yet printed” describe the earlier CAD-check stage; the physical report supersedes that status. Their `assembly_validated: false` still correctly means that no complete insertion path was established numerically. Successful physical assembly does not turn that into a computed path proof.

The preserved exported-mesh checks cover all twelve ordinary 180° turns at 3° increments, a five-step jumbling sequence, a 48-step legal jumbling walk, hardware fit, nut loading, layer connectivity, and spherical retaining faces. Retention probes count only the inner feet, excluding outer-body obstruction. Petals were checked against screwed centers displaced outward 0.15 mm, and corners against petals displaced outward 0.8 mm. These checks address the support chain rather than relying only on a pull against perfectly fixed neighboring floating pieces.

The four center-flange outline corners were measured at three radial stations each: measured tessellated radii span 1.177–1.209 mm for nominal R1.2. The center's inner spherical bearing area remains about 169.05 mm² per part. This is a geometry measurement, not a load rating. Layer-connectivity checks include 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width combinations; they are not actual slicer toolpaths.

The new publication audit checks supplied-file hashes, quantities, unchanged CAD/reports, license, local documentation links and archive checksums. Since the print geometry is unchanged, the full CAD simulation was not rerun for publication.

The successful build report does not separately establish turning torque, friction, endurance, elastic pop resistance or every possible jumbling state. It supplies physical assembly evidence alongside the finite geometric checks, without converting either into an exhaustive guarantee.
