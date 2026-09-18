# Validation and physical feedback — Skewb v1.1

These checks use the exported, reloaded delivery meshes, in millimeters. They
establish sampled geometric fit and explicit assembly routes.

**Owner-tested v1.1:** on 2026-09-18 the owner reported that the trimmed Skewb printed very well and turns very nicely. The STL hashes match the delivered revision associated with that report.

The owner feedback adds a successful physical build and a qualitative assessment
of turning. It is distinct from the computational results below. Exact slicer
settings and nut-seat variant were not restated; holding force, turn torque,
wear life and a corner-cutting angle have not been measured. The report and
original export hashes are in [physical-feedback.json](physical-feedback.json).

| Check | Result |
|---|---|
| STL integrity | 22 closed, consistently wound, positive-volume, single-component meshes |
| Print plates | 9 named 3MF plates within 256 × 256 mm, without bounding-box overlap |
| Alternative orientations | 10 face-down 3MFs preserve the default meshes by rigid transformation |
| Aligned turns | 4 axes × 41 samples over 0–120°, with core, screws and washers |
| Scrambled turns | 16 mixed-axis moves × 21 intermediate samples; signatures updated after each move |
| Largest sampled turn intersection | 6.23e-06 mm³, below the 0.001 mm³ numerical acceptance threshold |
| Whole-piece insertion | All 14 pieces, 79 offsets each, plus stand withdrawal |
| Largest sampled insertion intersection | 2.33e-08 mm³, below the 0.001 mm³ threshold |
| Retention | All 10 floating pieces have positive internal obstruction under outward pull |
| Further retention paths | 114 directional pulls and 72 ramped rocking paths, all obstructed |
| Lifted screwed corners | Retention paths repeated at nominal, +0.10 and +0.25 mm C lift |
| Radial fillets | 2854 exposed transverse arc sections checked; no radius taper in the cutter |
| Largest sampled R3 circle deviation | 0.0209 mm |
| Largest sampled original-CAD vs STL ridge-profile difference | 0.0122 mm |
| Sampled export surface distance after regularization | At most 0.000453 mm bidirectionally |

The first detected nominal radial obstruction is about 0.55 mm for F pieces and
0.50 mm for K pieces. These are sampled pull travel against fixed rigid neighbors,
not looseness measured in an assembled hand-held puzzle. The retention tests use
only inner geometry within radius 30 mm, so the decorative exterior is not credited
as a retainer. The two canonical floating families are probed along 19 directions
and 12 rocking paths at each of three C lifts. This is not an exhaustive search
of every possible combined six-degree-of-freedom escape or flexing of printed feet.

## Floating-corner revision

Only K01–K04 differ from the previous release. The CAD edit is subtraction within
radius 22.262 mm; the exterior shape is unaffected. At 0.16 mm layers and 0.42 mm
fixed extrusion width, the old K01 has six small detached layer-graph components
around its three tips. The revised K pieces have a single connected printable
layer graph in all 40 tested combinations: four pieces, two orientations and five
layer-height/line-width pairs (0.12/0.42, 0.16/0.40, 0.16/0.42, 0.16/0.48, 0.20/0.42).

All tested pull and rocking paths remain obstructed, including lifted C pieces.
The first-contact distances match v1 in these sampled checks. That establishes
geometric retention after trimming, not equal breaking strength or measured force.

Bambu Studio 02.05.00.66's CLI test failed while loading the stock printer/filament
configuration (exit 139). No completed automated Bambu slice or toolpath check
was obtained during that validation run. The later owner report confirms an
actual successful print; its G-code was not inspected here. The layer checks are geometric simulations using a fixed line width;
they do not model Arachne's variable width, bridges, supports or slicer heuristics.
The revised parts still need appropriate support for their normal overhangs.

## Hardware

All four screw envelopes clear the core and each other. Washer insertion and
hex-key access are checked through each C well. The washer land and flat bearing
annulus are present. Each nut has a free outer loading route, intended interference
at its final seat, an axial retaining roof and a clear Ø3 mm press-rod route.
Rotating the nominal hex nut into the pocket walls produces additional geometric
interference; this does not predict the pocket's torque capacity. The alternate
core sizes clear the same mechanism envelope.

## Shape distinction

The minimum sampled exterior RMS difference between pairs, after trying proper
mounting rotations, is 2.685 mm for C,
4.196 mm for F and
2.480 mm for K. Reflections are not identified
with rotations. These are sampled comparisons, not an optimality proof.

## Mesh and sampling limits

The cutter circles are checked in planes transverse to radial ridges, through the
inner track region and toward the exterior. The middle 80% of each exposed arc is
sampled; other fillets, the core cavity and the cube can terminate an arc. Exposure
is selected from pre-export CAD rather than from the mesh being tested. A fillet's
intersection with another surface need not itself be circular.

Export uses 0.001 mm normal-error mesh regularization before float32 STL conversion.
That tolerance is not a bound on the motion of every vertex: nearly zero-thickness
CSG whiskers can disappear. Regularization's added/removed volumes are reported
separately. Bidirectional surface samples compare the regularized export input with
the reloaded STL; the circle/profile checks also compare against original CAD.
Any extra cleanup is recorded per part in the manifest. Finite holes are not filled
as a mesh-repair shortcut. Face-down alternatives use indexed, double-precision
3MF to avoid a second STL quantization.

Turn samples are 3° apart for single-axis tests and 6° for the mixed sequence.
The analytic axisymmetric interfaces motivate intermediate motion, but the numerical
reports are sampled checks, not a formal continuous-motion proof. Small residual
intersection volumes at coincident mesh boundaries are treated as numerical noise.
First-layer section areas are also recorded; they do not predict support performance.

Machine-readable results are in `reports/`. `manifest.json` records dimensions,
orientations and STL hashes. `SHA256SUMS` covers the delivered package contents.
