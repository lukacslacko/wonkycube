# Frozen v4.1 baseline

This is the numerical starting point for the v4.2.1 publication export.

- `reference/assembly_meshes.npz`: named vertex and triangle arrays in mechanism coordinates, including the earlier edge shapes.
- `reference/design.json`: the matching dimensions and print transforms.
- `parts/`: unchanged core and eight corner print STLs, copied byte-for-byte by the builder.
- `calibration/`: seven baseline fixture/jig STLs; the three moving edge segments are regenerated.

The baseline avoids rebuilding expensive earlier rounding operations and preserves the exact earlier shape and print frames. It is original project geometry covered by the root MIT license. The source for the preceding operations is retained one directory above. Historical full release bundles contain the earlier complete builds.

Changing an upstream constant does not retroactively change these frozen meshes. Rebuild the upstream stages explicitly when changing the core, rail, exterior or track design; do not expect the latest subtract-only edge builder to resize them.
