# DCSC independent-reference coverage

The written source is the Meteo-France DRIAS-2020 indicator definition page
provided as a PDF capture. The registry identifies the family as DCSC
(Direction de la Climatologie et des Services Climatiques).

| name | definition source | oracle written Y/N | result |
|---|---|---:|---|
| TAV | DRIAS-2020 temperature indicators | Y | pass |
| TXAV | DRIAS-2020 temperature indicators | Y | pass |
| TRAV | DRIAS 2023-12-01 indicator table | Y | xfail #668: sign reversed |
| TX10 | DRIAS-2020 temperature indicators | N | pending |
| TX90 | DRIAS-2020 temperature indicators | N | pending |
| TN10 | DRIAS-2020 temperature indicators | N | pending |
| TN90 | DRIAS-2020 temperature indicators | N | pending |
| TNFD | DRIAS 2023-12-01 indicator table | Y | pass; older source says <= 0 C |
| TXFD | DRIAS 2023-12-01 indicator table | Y | pass; older source says <= 0 C |
| SD | DRIAS-2020 temperature indicators | Y | pass |
| TX35 | DRIAS-2020 temperature indicators | Y | pass |
| TR | DRIAS-2020 temperature indicators | Y | pass |
| TXND | DRIAS 2023-12-01 indicator table | Y | pass |
| TNHT | DRIAS 2023-12-01 indicator table | Y | pass |
| TNND | DRIAS 2023-12-01 indicator table | Y | pass |
| TNCWD | DRIAS 2023-12-01 indicator table | Y | values pass; dims xfail #669 |
| TXHWD | DRIAS 2023-12-01 indicator table | Y | values pass; dims xfail #669 |
| HDD | DRIAS-2020 temperature indicators | Y | pass |
| CDD | DRIAS-2020 temperature indicators | Y | pass |
| PAV | DRIAS 2023-12-01 indicator table | Y | pass |
| PINT | DRIAS 2023-12-01 indicator table | Y | pass |
| RR | DRIAS 2023-12-01 indicator table | Y | pass |
| RR1MM | DRIAS 2023-12-01 indicator table | Y | pass |
| PN20MM | DRIAS 2023-12-01 indicator table | Y | pass |
| PXCDD | DRIAS 2023-12-01 indicator table | Y | pass |
| PXCWD | DRIAS 2023-12-01 indicator table | Y | pass |
| R99 | DRIAS-2020 precipitation indicators | N | pending |
| PFL90 | DRIAS-2020 precipitation indicators | N | pending |
| PQ90 | DRIAS-2020 precipitation indicators | N | pending |
| PQ99 | DRIAS-2020 precipitation indicators | N | pending |
| FFAV | DRIAS-2020 wind indicators | N | pending |
| FF98 | DRIAS-2020 wind indicators | N | pending |
