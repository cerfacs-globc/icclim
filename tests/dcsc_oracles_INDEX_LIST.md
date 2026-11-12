# DCSC independent-reference coverage

The written source is the Meteo-France DRIAS-2020 indicator definition page
provided as a PDF capture. The registry identifies the family as DCSC
(Direction de la Climatologie et des Services Climatiques).

| name | definition source | oracle written Y/N | result |
|---|---|---:|---|
| TAV | DRIAS-2020 temperature indicators | Y | pass |
| TXAV | DRIAS-2020 temperature indicators | Y | pass |
| TRAV | DRIAS 2023-12-01 indicator table | Y | xfail #668: sign reversed |
| TX10 | DRIAS 2023-12-01 TXQ10 definition | Y | xfail #670: returns count, not q10 value |
| TX90 | DRIAS 2023-12-01 TXQ90 definition | Y | xfail #670: returns count, not q90 value |
| TN10 | DRIAS 2023-12-01 TNQ10 definition | Y | xfail #670: returns count, not q10 value |
| TN90 | DRIAS 2023-12-01 TNQ90 definition | Y | xfail #670: returns count, not q90 value |
| TNFD | DRIAS 2023-12-01 indicator table | Y | pass; older source says <= 0 C |
| TXFD | DRIAS 2023-12-01 indicator table | Y | pass; older source says <= 0 C |
| SD | DRIAS-2020 temperature indicators | Y | values pass; degF equality xfail #675 |
| TX35 | DRIAS-2020 temperature indicators | Y | values pass; degF equality xfail #675 |
| TR | DRIAS-2020 temperature indicators | Y | values pass; degF equality xfail #675 |
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
| R99 | DRIAS-2020 reference-q99 definition | Y | xfail #672: undocumented wet-day floor |
| PFL90 | DRIAS 2023-12-01 indicator table | Y | xfail #671: wet-only percentile and denominator |
| PQ90 | DRIAS 2023-12-01 indicator table | Y | values pass; metadata xfail #676 |
| PQ99 | DRIAS 2023-12-01 indicator table | Y | values pass; metadata xfail #676 |
| FFAV | DRIAS 2023-12-01 wind indicators | Y | xfail #673: base-period call errors |
| FF98 | DRIAS 2023-12-01 wind indicators | Y | xfail #674: undocumented one-knot floor |
