# Wonkycube

Open-source, 3D-printable Redi and Skewb shape mods. Their cube-shaped exterior is rotated away from the mechanism's axes, giving interchangeable pieces distinct outside shapes. Scramble either puzzle and the cube changes shape.

The newest release is **Wonky Skewb v1.1, 64 mm, with trimmed floating-corner flange tips**. On 2026-09-18 the owner reported that it printed very well and turns very nicely.

![Wonky Skewb, solved and exploded](designs/skewb-v1.1/images/overview.png)

Designed and physically iterated by **László Lukács**, with CAD, optimization and documentation developed with OpenAI Codex. Source, documentation and original generated models are available under the [MIT license](LICENSE).

## Print one

| Design | Download | Build guide | Puzzle parts and hardware |
|---|---|---|---|
| **Skewb v1.1 — 64 mm** | [Full set or four-corner upgrade](https://github.com/lukacslacko/wonkycube/releases/tag/skewb-v1.1) | [Assembly](designs/skewb-v1.1/ASSEMBLY.md) · [Neighbors](designs/skewb-v1.1/NEIGHBORS.md) | 15 printed parts; 4 screws, washers and locknuts |
| **Redi v4.3 — 64 mm** | [Full set](https://github.com/lukacslacko/wonkycube/releases/tag/v4.3) | [Assembly](designs/redi-v4.3/ASSEMBLY.md) · [Neighbors](designs/redi-v4.3/NEIGHBORS.md) | 21 printed parts; 8 screws, washers and locknuts |

Both use **DIN912 M3 × 20 socket-head screws**, **Ø9 × 1 mm washers with M3 clearance holes**, and **DIN985 M3 nylon-insert locknuts**. Nuts load sideways into the core. Retaining features are integral with the pieces; no glue or separate hidden printed carriers are needed.

Use millimetres and **100% scale**. Development used a Bambu Lab P1S with a 0.4 mm nozzle and PLA as the baseline. The supplied 3MFs contain geometry, not a validated slicer profile or G-code. Check the version's assembly guide, nut-fit coupons and support placement. Exact slicer settings, chosen orientation and nut-seat variant were not restated in the latest success report.

The Skewb has four screwed corners C01–C04, six floating faces F01–F06 and four floating corners K01–K04 around one core. Assembly order is **K → F → C**. Its core implements a wide nut-loading entrance leading to a narrower final torque seat, with alternative fits supplied. The v1.1 correction trims three thin perforated tips from each K flange, leaving broad retaining lobes. Only K01–K04 need replacing in an existing v1 build; every other STL is byte-for-byte unchanged. Read the [tip revision and checks](designs/skewb-v1.1/TIP-REVISION.md).

The Redi has eight screwed corners and twelve movable edges around one core. Its owner reports that everything except nut retention feels very nice. **Known Redi v4.3 core issue:** about half the nut seats allowed nuts to spin under installation torque. A narrower final seat is documented as a [pending Redi core improvement](docs/design.md#known-core-issue-and-next-change); the published Redi core has not been changed by this Skewb release.

The [80 mm Redi v4.2.1 release](https://github.com/lukacslacko/wonkycube/releases/tag/v4.2.1) and [its files](models/current) remain available. **Do not mix parts between these different mechanisms or sizes.** The historical `models/current` directory still denotes the 80 mm set.

## Why they turn well

Different surfaces do different jobs. Flat retaining shoulders obstruct withdrawal. Wider tracks accommodate the swept flange shape. Rounded entrances and continuous radial ridges reduce snagging, while flat axle feet and lightly adjusted screws support rotation. A compact exterior brings the grip closer to the mechanism.

The Skewb adds a printing lesson: a connected CAD flange can have webs too thin to form extrusion paths. Removing its nonfunctional perforated tips eliminated isolated scraps while preserving capture in the checked paths. The owner then confirmed successful printing and nice turning. This qualitative result supports the combined design; it does not isolate the contribution of each feature or measure strength and wear.

The [mechanism design guide](docs/mechanism-principles.md) collects these transferable lessons about capture, clearance, rounding, assembly, sizing, nut retention and printable connectivity, including failures and ways to diagnose them.

## Explore or modify

| Resource | Purpose |
|---|---|
| [Mechanism principles](docs/mechanism-principles.md) | Reusable design knowledge, including flange-tip trimming |
| [Skewb design](designs/skewb-v1.1/DESIGN.md) | Four-axis mechanism, retaining rails, hardware and assembly hierarchy |
| [Skewb validation](designs/skewb-v1.1/VALIDATION.md) | Geometry checks, physical feedback and their limits |
| [Skewb CAD](designs/skewb-v1.1/source/README.md) | Python/Manifold source, regeneration and checks |
| [Redi design](docs/design.md) | Dimensions, rotation and pending core improvement |
| [Redi CAD](designs/redi-v4.3/source/README.md) | Compact Redi source and regeneration |
| [Development history](docs/development-history.md) | How printed feedback changed both mechanisms |

The exterior rotation is a best-found numerical result for sampled Redi edge distinction, reused for the Skewb. It is not a proof of global or perceptual optimality. Attachments intentionally interchange during play; exterior shapes distinguish solved locations. Mirror images count as different.
