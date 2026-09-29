# Optional retention test patch

The full spherical-v3.2 puzzle has now printed and assembled successfully. This patch is optional for checking your own print fit before making all the pieces.

Print `retention-test-7-pieces.3mf`: three centers, three petals and one corner. These are the exact full-puzzle STLs, so they count toward the complete print if the test succeeds. The file contains geometry and placement, not Bambu slicing settings.

Reuse the **old 64 mm vertex-turning cuboctahedron core**, three M3×20 DIN912 screws, three 9×1 mm washers and three installed DIN985 nuts. The new body is 72 mm, but its core mounts are unchanged. Reuse spherical-v3 or v3.1 floating corners freely. Petals should be the accepted v3.1 design; previous cylindrical-retention parts are not compatible.

The reference assembly is for viewing, not printing. The other named print plates are also printable; never print the assembled reference.

| Family | Actual locations |
|---|---|
| C | C01, C02, C05 |
| P | P01, P05, P06 |
| K | K01 |

1. Use the reference to position the corner, petals and centers. Keep centers absent or loose while manipulating the floating pieces. The complete spherical shoulders were not trimmed for straight insertion, and no complete insertion path was established numerically. Full assembly has since been achieved physically.
2. Once interlocked, install the three screws and washers. Seat gently; do not use the screws to force a blocked part past a shoulder.
3. Remove the temporary tape. With the centers seated, the three petals and the corner should stay captured when the patch is lifted or turned over. Gently tug each outward and rock it a little.
4. Back the center screws off only enough for the parts to move without binding. Confirm the loose parts remain captured with that setting.
5. If a petal or corner still comes out readily, stop before printing the rest and report which part and direction. This is a physical test of the new geometry, not a promise of pop resistance.

This open patch is a **retention fixture**, not a complete turning puzzle. Do not try full turns on it: missing neighboring sectors do not provide the normal transfer of support. No destructive pull force is prescribed.

After a satisfactory test, print the remaining **9 centers, 21 petals and 7 corners**. The three full-set plates include the test pieces again; remove those copies if you use the plates.

## Reusing your spherical-v3 test pieces

`upgrade-test-6-pieces.3mf` contains the three revised centers and three revised petals only. Reuse the old core and the previously printed K01 corner. The corner and core STLs are unchanged; the revised centers/petals work with them. For a full upgrade, replace all twelve centers and twenty-four petals.

## Center-only correction from v3.1

`centers-only-test-3-pieces.3mf` contains the three corrected centers for the existing patch. `centers-only-full-12-pieces.3mf` contains all twelve centers without a core or floating pieces. v3.1 petals, floating corners and core are unchanged byte for byte. Only the center files changed in v3.2.
