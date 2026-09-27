# Piece neighbors

These pieces share an exterior seam in the solved puzzle. Internal retaining contacts can include additional pieces. The axis IDs refer to screwed centers, not cube face names.

| Piece | Turn axes containing it | Exterior neighbors |
|---|---|---|
| C01 | C01 | V01, V02, H01, H02 |
| C02 | C02 | V01, V03, H03, H04 |
| C03 | C03 | V02, V03, H05, H06 |
| C04 | C04 | H01, H03, H05 |
| C05 | C05 | H02, H04, H06 |
| V01 | C01, C02 | C01, C02, K01, K02 |
| V02 | C01, C03 | C01, C03, K03, K04 |
| V03 | C02, C03 | C02, C03, K05, K06 |
| H01 | C01, C04 | C01, C04, K01, K03 |
| H02 | C01, C05 | C01, C05, K02, K04 |
| H03 | C02, C04 | C02, C04, K01, K05 |
| H04 | C02, C05 | C02, C05, K02, K06 |
| H05 | C03, C04 | C03, C04, K03, K05 |
| H06 | C03, C05 | C03, C05, K04, K06 |
| K01 | C01, C02, C04 | V01, H01, H03 |
| K02 | C01, C02, C05 | V01, H02, H04 |
| K03 | C01, C03, C04 | V02, H01, H05 |
| K04 | C01, C03, C05 | V02, H02, H06 |
| K05 | C02, C03, C04 | V03, H03, H05 |
| K06 | C02, C03, C05 | V03, H04, H06 |

A side turn moves its C center, two V petals, two H petals and four K corners. A pole turn moves its C center, three H petals and three K corners.

C01 = (1,0,0), C02 = (−1/2,√3/2,0), C03 = (−1/2,−√3/2,0), C04 = (0,0,1), C05 = (0,0,−1) in mechanism coordinates.
