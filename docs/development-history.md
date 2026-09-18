# Development history

This project was developed through printed prototypes and feedback. “Printed” below means an owner report, not an instrumented laboratory test.

| Revision | Change | What was learned |
|---|---|---|
| Initial design | 100 mm rotated exterior, conical/flared interfaces, sleeves and inserts proposed | Exterior asymmetry can be designed independently of the basic turn axes. Hardware/access choices still control the interior. |
| v2 | Direct plastic screw pilots, external washer wells, matching flat corner feet | The full cube printed and assembled on the first attempt. Edges nevertheless pulled out easily even while aligned; pieces were sharp and caught. |
| v3 | 80 mm exterior, stepped retaining shoulders, 0.20 mm nominal gap, nonconvex insertion relief, 1 mm exposed-edge rounding | Positive retention and a more compact shell addressed major weaknesses. The assembled mechanism was still very catchy. |
| v3.1 | Removed the extra print flat from the core; retained eight axle pads | A core can print on an intentional axle pad while keeping its other curved areas spherical. |
| v4 | 0.60 mm internal edge rounding, 0.45 mm corner lead-ins, widened tracks swept from unrounded flanges | The owner described the result as very good and requested more alignment relief at the radial ridges. Track clearance and corner adjustment are different controls. |
| v4.1 | 2 mm outer radial-ridge rounding, blended above the protected inner region | The inner track region retained a visibly smaller radius. Protecting too much geometry can preserve the exact snag being addressed. |
| v4.2 | Intended constant 3 mm radial-ridge rounding through the tracks | The owner confirmed a v4.2 / 3 mm print and reported that it printed very well. Saved exports were later found to span different generation attempts; exact printer input hashes were not recorded. |
| v4.2.1 | Consistent publication export, radius checks across the track transitions, closed STL export, MIT project and reusable documentation | Preserves the printed prototype's design intent and unchanged core/corners while making the current export internally consistent and auditable. This exact export has digital checks, not a separate physical print report. |
| v4.3 compact | 64 mm cube and smaller mechanism; DIN985 M3 nuts, DIN912 M3 × 20 screws, 9 × 1 mm washers; main-face gap reduced to 0.03 mm; 0.40 mm track expansion and R3 ridges retained | The owner built it and reports that everything except nut retention feels very nice. About half of the nut seats allow rotation under locknut installation torque. Axial capture and handling ribs do not establish antirotation capacity. |
| v4.3 print orientation | Edge STLs and plates supplied with their inward radial vectors pointing down | This is the owner's preferred print orientation. Publication preserves the delivered geometry and adds the physical feedback; the proposed tighter terminal nut seat is documented as a pending core-only change. |
| Skewb v1 | 64 mm exterior; four screwed C corners, six floating F faces and four floating K corners; integral stepped rails, K → F → C assembly, narrower final nut seats | The Redi's hardware, close main-face gap, wider tracks and R3 ridge construction transfer to another topology, but its rail and insertion geometry require new checks. The K flanges had three thin perforated tips that sliced into isolated, wastefully supported fragments despite connected CAD meshes. |
| Skewb v1.1 | Subtract the three perforated tips from each K corner, retaining the broad capture lobes; all 18 other STLs unchanged | Layer-connectivity checks eliminate the isolated scraps in 40 tested cases. Sampled motion, insertion and retention still pass. On **2026-09-18**, the owner reported that the trimmed Skewb printed very well and turns very nicely. Publication preserves those delivered STL/3MF bytes and records the qualitative result; detailed print settings and measured strength/wear were not supplied. |

Older complete download bundles and the v4.2 workspace snapshot are preserved as historical release assets. The snapshot is not presented as a verified current print set. Its [manifest](../history/v4.2-workspace-snapshot-sha256.json) records the files as found.

One historical metadata error deserves explicit correction: the original v3/v3.1 `design.json` reported a 100 mm side and 0.50 mm gap because a wildcard import overwrote the labels in the builder. Their actual geometry was 80 mm with 0.20 mm nominal gap. Current metadata and source imports are corrected. Historical archives remain identifiable as historical rather than silently rewritten.

OpenSCAD was tried during early development and crashed. The maintained CAD pipeline uses Python, Manifold and Trimesh; OpenSCAD is not required.
