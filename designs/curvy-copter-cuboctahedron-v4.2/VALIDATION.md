# Validation scope

The supplied v4.2 geometry is preserved byte-for-byte from the delivered 1 mm-pocket design. `publication.json` records its geometry, source and report hashes; `SHA256SUMS` covers this publication package.

- [Package audit](reports/package-audit.json): eight closed, connected STL solids and five geometry-only print/test plates; full puzzle quantities total 57 parts including the reusable core.
- [Mechanism preservation](reports/preserved-mechanism.json): byte-identical core and unchanged repaired spherical-retention geometry inside R35, within mesh export tolerance.
- [Pocket construction](reports/inlays.json) and [actual floor support](reports/paper-backing.json): 1 mm depth, 1.2 mm separating webs and 1.2 mm backing before separating the central plug joint. New cutting contours match the deeper pockets.
- [Plug fit](reports/plug-fit.json): outside insertion/removal, keyed orientation, washer/driver access and screw-head clearance.
- [Layer connectivity](reports/layer-connectivity.json): 0.16 and 0.20 mm layers.
- [Motion summary](reports/summary.json): all twelve half turns at 3-degree intervals, five jumbling moves at 49 samples per move, and a 48-step legal jumbling walk. Inlays filling the whole 1 mm recess are included in the collision envelope.
- [Capture](reports/capture.json) and [spherical retention](reports/retention-spherical.json): actual retaining feet, directional extraction probes and nine solved, intermediate and jumbled configurations, including displaced supporting petals.
- [Rounding regression](reports/rounding-regression.json): both halves of the repaired R2 radial fillets remain free of hook remnants.
- [Cutting files](reports/cutting-files.json): 104 exact face inlays; all 30 SVG/DXF/DWG sheet sets; one removable 210 × 297 mm A4 rectangle per sheet. Genuine DWGs were independently decoded and compared with their source contours. [The CSV](inlays/sheet-dimensions.csv) records both framed and inlays-only sizes.

The original spherical-retention mechanism has successful physical print/assembly evidence. The owner reported inadequate inlay guidance in the 0.5 mm-pocket version. **The 1 mm revision is CAD-checked and awaits a physical print**, as recorded in [physical-feedback.json](physical-feedback.json). These finite rigid checks do not measure friction, support scars, paper, adhesive, elastic forces or wear. Shell assembly inherits the unchanged mechanism's physical evidence; plug insertion is checked separately.
