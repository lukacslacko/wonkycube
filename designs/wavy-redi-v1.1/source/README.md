# Rebuilding Wavy Redi v1.1

Use Python 3.11 and install `requirements.txt` in a virtual environment.
Then run:

```sh
python build.py --work ../build --output ../rebuilt
```

The build can take several minutes for the curved-surface Boolean operations.
It caches intermediate geometry in the work directory. Use a **fresh work
directory after changing geometric parameters**; cached meshes are not
automatically invalidated.

`selection.json` preserves the exact submitted profile. `redi_design.py`
contains the printable hidden profile and the approved local 51.6-degree
soft cap that strengthens the exposed core connections. It also defines
clearances, hardware and the nut-seat fit. `round_ridges.py` fits R2 circles
to concentric spherical sections; no straight-cone approximation replaces
the inner rail sections. `finish_parts.py` rounds exposed rims, and
`export_parts.py` creates the print orientations, STLs and geometry-only 3MFs.

`validate_parts.py` reads back those STLs for motion, assembly, retention,
hardware, core thickness, approximate layer connectivity, ridge, exterior-tip and plate
checks. `summarize_validation.py` refuses to report completion unless all
validation jobs passed and file hashes match.

The renders use the exported meshes. Fonts in the assembly images default
to macOS Helvetica; change the font path in `render_parts.py` on other systems.

The finite spherical fillet tool extends beyond the entire cube before being capped. `validate_parts.py exterior` rejects the former clipped-tip geometry. Physical success belongs to v1; v1.1 changes only the core nut fit and four petal tips.
