# Conical 3×3 validation and physical feedback

**Owner-printed:** the owner reported that the reinforced v1.1 printed very well. These STL hashes match the supplied set associated with that report.

The owner report is limited to successful printing. It does not supply a separate
turning assessment, instrumented strength or fatigue result, or an inspection of
the printer's input files. Exact settings and the chosen nut-seat variant were
not restated. [Report and supplied STL hashes](physical-feedback.json).

The numerical reports describe the delivered meshes and their explicit assembly
transforms. Each required report is linked to the manifest by SHA-256.

| Check | Result |
|---|---|
| Required report groups | 10 passed |
| Sampled intended turn and scramble poses | 570 |
| R3 transverse ridge sections | 5234 |
| Largest checked circle error | 0.0247 mm |
| Printable layer-graph cases | 54 |
| Smallest measured screwed-piece root web | 2.04 mm |
| Screw projection beyond locknut | 1.85 mm |

Additional checks cover radial insertion, hardware and driver access, stand
withdrawal, exported mesh fidelity, print-plate placement, and sampled extraction
and rocking paths, including intermediate turn positions and modest center lift.

The web measurement tests 720 angular positions per screwed piece. The six
reinforced centers preserve bearing and retaining dimensions; the other 21
puzzle STLs are byte-for-byte unchanged from v1. See
[the revision report](reports/revision.json) and [root measurements](reports/root-web.json).

Connectivity establishes a continuous solid or a modeled printable path; it does
not establish sufficient mechanical strength. Finite pose samples also do not
prove clearance or retention at every possible configuration. Physical loads,
friction, elastic popping, wear and fatigue need separate testing.

[Aggregate report](reports/validation-summary.json) · [Design](DESIGN.md) ·
[Assembly and printing](README.md) · [Regeneration source](source/README.md)
