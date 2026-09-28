# Build feedback and validation

On **2026-09-28**, the owner reported that the **face-turning cuboctahedron printed and assembled well**, with one usability limitation: **the square faces are not very easy to turn**. [The physical-feedback record](physical-feedback.json) identifies the associated supplied files. Exact print settings and the chosen optional core were not restated.

The publication preserves the supplied geometry, 3MF layouts, geometry-generating CAD, manifest and original numerical reports byte for byte. `publication.json` records their hashes. The numerical summary's “physical print ... untested” wording describes the CAD-validation stage before this build report; the physical-feedback record above supersedes that status for the supplied v1 parts.

The original exported-mesh checks cover all fourteen axes at 3° turn increments, ordinary-turn destinations, assembly and removable-stand paths, nut loading, hardware clearance, washer-root and bore-wall material, petal retention during turns, tilted extraction, and layer connectivity at 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width pairs. The `reports/` directory contains the results, and `reports/summary.json` records their successful completion.

Finite rigid-geometry checks do not measure hand torque, friction, elastic retention or endurance. Successful assembly and difficult square-face turns can coexist. Grip and leverage are plausible contributors, but their contribution relative to support finish, screw adjustment and friction has not been isolated.

A vertex-turning **rhombic dodecahedron**, the cuboctahedron's dual, is a possible future exterior with a projecting shape to grasp around each of the same fourteen axis directions. Better grip is an expectation to test, not a measured improvement or an existing printable alternative. No such geometry is included in this release.
