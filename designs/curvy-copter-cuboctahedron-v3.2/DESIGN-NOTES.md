# Design notes · spherical v3.2

The center flange has a rounded **outline seen along a radial direction**, while retaining broad spherical bearing rims. The owner reported a successful full print and assembly on 2026-09-29; see [physical feedback](physical-feedback.json).

## Radial outline fillets

The additional 0.95 mm ball opening introduced in v3.1 is removed. Center construction again starts from the spherical-v3 center body: original 0.35 mm small-edge treatment, existing R2 radial fillets and full spherical shoulders. It then rounds the four outline corners at the two flange ends using a **1.2 mm transverse circle swept radially**. Hardware features are installed afterward, as before.

The hidden collar lies between nominal radii 28.5 and 33.5 mm, where the cutting cones have 40° half-angle. Each actual outline-corner direction comes from intersecting two of these 40° cones. Using the exterior 45° intersection instead would aim the cutter at the wrong radial line. Extended conical reference surfaces define the tangencies, so the spherical shoulders cannot divert the fitting circle. The resulting fillets are cylindrical in character and follow the radial corner through the flange. They remove material only near the outline corners; no band mask creates a stopping ridge on a bearing face.

The original small-edge rounding remains. The broad spherical bearing areas regain the material removed by v3.1's extra ball opening. The exterior shape, screw bore, washer seat, axle-bearing foot and core interfaces retain their original dimensions. Retessellation and final 0.005 mm mesh simplification cause tiny numerical differences outside the intended cuts; these are measured separately in `reports/revision-v3.2.json`.

## Accepted petal changes retained

The petal STL is byte-for-byte identical to v3.1. Its two tips at the floating corner retain R2 radial rounding right through the outer face, fitted against an unclipped reference body. Its center-facing groove is widened by 0.20 mm total, divided equally between the two spherical bearing walls.

| Dimension | Current value |
|---|---:|
| Center flange nominal radial thickness | 4.42 mm |
| Petal groove nominal radial width | 5.28 mm |
| Gap at each center–petal spherical face | 0.43 mm |
| Total radial groove/flange clearance | 0.86 mm |
| Corner–petal bearing gap | 0.33 mm |
| Main conical body gap | 0.08 mm |
| Flange outline corner rounding | R1.2 mm |

The core and floating-corner STLs are also byte-identical to v3.1 and spherical v3. Print orientations and hardware are unchanged.

## Validation scope

Checks run on reloaded exported STLs, including all twelve axes in 3° steps through 180°, the five-step jumbling sequence with 49 positions per step, and a 48-step legal jumbling walk. Retention probes count only the inner feet below R28.5, excluding accidental outer-body obstruction. Petals are tested against screwed centers lifted 0.15 mm; corners against petals displaced outward 0.8 mm. Straight extraction directions, collective expansion and eight limited radial-translation/tilt searches are included.

All four flange outline corners are measured in transverse sections at radial stations 29, 30.5 and 32 mm. The geometry checks distinguish the new outline fillets from the removed v3.1 ball opening. The measured outline radii span 1.177–1.209 mm on the tessellated STL (nominal R1.2). The center inner spherical bearing area is 169.05 mm² per part, compared with 169.10 mm² in v3 and 118.87 mm² after the discarded v3.1 rounding. This geometric face area is not a force rating. See `reports/spherical-shoulders.json`.

Mesh and printability checks include watertightness, one connected component, and geometric layer connectivity at 0.16/0.42 mm and 0.20/0.45 mm layer-height/line-width combinations. Hardware checks and plate audits are included. These calculations do not predict support finish, friction, elastic retention, torque or fatigue. The subsequent physical report confirms a successful full print and assembly of the supplied design. It does not isolate the effects of flange rounding, track clearance and surface finish.

No assembly relief was cut. The owner assembled the full puzzle by hands-on interlocking; a detailed insertion sequence remains unrecorded. There is no new assembly requirement, hardware or change to the accepted floating parts.
