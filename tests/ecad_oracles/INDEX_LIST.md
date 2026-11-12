# ECA&D independent reference calculations: inventory

Generated from `EcadIndexRegistry` on master. Definitions are the ECA&D ATBD v11 registry text.
All 66 indices have an independent reference calculation and pass: 64 in the families A to D of this directory
(A: GSL, SPI3, SPI6; B: percentile indices; C: counts, runs, sums and compound indices; D: statistics and weather
counts), and HI and BEDD in their own test files (family E).
A run of days that crosses the end of a year is counted in the year where it ends (`run_index="last"`, the rule
of the ATBD, RClimDex and climdex), also in the reference calculation of the run indices (CSU, CFD, CDD, CWD).

| name | family | group | source variables | threshold | definition | reference calculation written | result |
|---|---|---|---|---|---|---|---|
| TG | D | temperature | tg | — | Mean of daily mean temperature. | Y | pass |
| TN | D | temperature | tn | — | Mean of daily minimum temperature. | Y | pass |
| TX | D | temperature | tx | — | Mean of daily maximum temperature. | Y | pass |
| DTR | D | temperature | tx, tn | — | Mean Diurnal Temperature Range. | Y | pass |
| ETR | D | temperature | tx, tn | — | Intra-period extreme temperature range. | Y | pass |
| vDTR | D | temperature | tx, tn | — | Mean day-to-day variation in Diurnal Temperature Range, using only differences within each output period and dividing by the number of valid differences (not the ATBD's number of days in the period). | Y | pass |
| SU | C | heat | tx | > 25 degree_Celsius | Number of Summer Days (Tmax > 25C). | Y | pass |
| TR | C | heat | tn | > 20 degree_Celsius | Number of Tropical Nights (Tmin > 20C). | Y | pass |
| WSDI | B | heat | tx | > 90 doy_per | Warm-spell duration index (days). | Y | pass |
| TG90p | B | heat | tg | > 90 doy_per | Days when Tmean > 90th percentile. | Y | pass |
| TN90p | B | heat | tn | > 90 doy_per | Days when Tmin > 90th percentile. | Y | pass |
| TX90p | B | heat | tx | > 90 doy_per | Days when Tmax > 90th daily percentile. | Y | pass; bootstrap compared with the leave-one-year-out reference |
| TXx | D | heat | tx | — | Maximum daily maximum temperature. | Y | pass |
| TNx | D | heat | tn | — | Maximum daily minimum temperature. | Y | pass |
| CSU | C | heat | tx | > 25 degree_Celsius | Maximum number of consecutive summer days (Tmax >25 C). | Y | pass |
| GD4 | C | cold | tg | 4 degree_Celsius | Growing degree days (sum of Tmean > 4 C). | Y | pass |
| FD | C | cold | tn | < 0 degree_Celsius | Number of Frost Days (Tmin < 0C). | Y | pass |
| CFD | C | cold | tn | < 0 degree_Celsius | Maximum number of consecutive frost days (Tmin < 0 C). | Y | pass |
| HD17 | C | cold | tg | 17 degree_Celsius | Heating degree days (sum of Tmean < 17 C). | Y | pass |
| ID | C | cold | tx | < 0 degree_Celsius | Number of sharp Ice Days (Tmax < 0C). | Y | pass |
| TG10p | B | cold | tg | < 10 doy_per | Days when Tmean < 10th percentile. | Y | pass |
| TN10p | B | cold | tn | < 10 doy_per | Days when Tmin < 10th percentile. | Y | pass |
| TX10p | B | cold | tx | < 10 doy_per | Days when Tmax < 10th percentile. | Y | pass |
| TXn | D | cold | tx | — | Minimum daily maximum temperature. | Y | pass |
| TNn | D | cold | tn | — | Minimum daily minimum temperature. | Y | pass |
| CSDI | B | cold | tn | < 10 doy_per | Cold-spell duration index (days). | Y | pass |
| CDD | C | drought | pr | < 1 mm/day | Maximum consecutive dry days (Precip < 1mm). | Y | pass |
| PRCPTOT | D | rain | pr | >= 1 mm/day | Total precipitation during Wet Days. | Y | pass |
| RR1 | C | rain | pr | >= 1 mm/day | Number of Wet Days (precip >= 1 mm). | Y | pass |
| SDII | D | rain | pr | >= 1 mm/day | Average precipitation during Wet Days (SDII). | Y | pass |
| CWD | C | rain | pr | >= 1 mm/day | Maximum consecutive wet days (Precip >= 1mm). | Y | pass |
| RR | D | rain | pr | — | Precipitation sum (mm). | Y | pass |
| R10mm | C | rain | pr | >= 10 mm/day | Number of heavy precipitation days (Precip >=10mm). | Y | pass |
| R20mm | C | rain | pr | >= 20 mm/day | Number of very heavy precipitation days (Precip >= 20mm). | Y | pass |
| RX1day | D | rain | pr | — | Maximum 1-day total precipitation. | Y | pass |
| RX5day | D | rain | pr | — | Maximum 5-day total precipitation. | Y | pass |
| R75p | B | rain | pr | {'query': '> 75 period_per', 'threshold_min_value': '1 mm/day'} | Days with RR > 75th percentile of daily amounts (moderate wet days) (d). | Y | pass |
| R75pTOT | B | rain | pr | {'query': '> 75 period_per', 'threshold_min_value': '1 mm/day'} | Precipitation fraction due to moderate wet days (> 75th percentile). | Y | pass |
| R95p | B | rain | pr | {'query': '> 95 period_per', 'threshold_min_value': '1 mm/day'} | Days with RR > 95th percentile of daily amounts (very wet days) (days). | Y | pass |
| R95pTOT | B | rain | pr | {'query': '> 95 period_per', 'threshold_min_value': '1 mm/day'} | Precipitation fraction due to very wet days (> 95th percentile). | Y | pass |
| R99p | B | rain | pr | {'query': '> 99 period_per', 'threshold_min_value': '1 mm/day'} | Days with RR > 99th percentile of daily amounts (extremely wet days). | Y | pass |
| R99pTOT | B | rain | pr | {'query': '> 99 period_per', 'threshold_min_value': '1 mm/day'} | Precipitation fraction due to extremely wet days (> 99th percentile). | Y | pass |
| SD | C | snow | snd | — | Mean of daily snow depth. | Y | pass |
| SD1 | C | snow | snd | >= 1 cm | Snow days (SD >= 1 cm). | Y | pass |
| SD5cm | C | snow | snd | >= 5 cm | Number of days with snow depth >= 5 cm. | Y | pass |
| SD50cm | C | snow | snd | >= 50 cm | Number of days with snow depth >= 50 cm. | Y | pass |
| CD | C | temperature_rain | tg, pr | ['< 25 doy_per', {'query': '< 25 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG < 25th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (cold/dry days). | Y | pass |
| CW | C | temperature_rain | tg, pr | ['< 25 doy_per', {'query': '> 75 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG < 25th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (cold/wet days). | Y | pass |
| WD | C | temperature_rain | tg, pr | ['> 75 doy_per', {'query': '< 25 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG > 75th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (warm/dry days). | Y | pass |
| WW | C | temperature_rain | tg, pr | ['> 75 doy_per', {'query': '> 75 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG > 75th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (warm/wet days). | Y | pass |
| FXx | D | wind | wsgs_max | — | Maximum value of daily maximum wind gust. | Y | pass |
| FG6Bft | D | wind | sfcWind | >= 10.8 m s-1 | Days with daily averaged wind ≥ 6 Bft (10.8 m s-1). | Y | pass |
| FGcalm | D | wind | sfcWind | <= 2 m s-1 | Calm days, days with daily averaged wind <= 2 m s-1. | Y | pass |
| FG | D | wind | sfcWind | — | Mean of daily mean wind strength. | Y | pass |
| DDnorth | D | wind | DD | > 315 degree OR <= 45 degree | Days with northerly winds (DD > 315° or DD ≤ 45°). | Y | pass |
| DDeast | D | wind | DD | > 45 degree AND <= 135 degree | Days with easterly winds (45° < DD <= 135°). | Y | pass |
| DDsouth | D | wind | DD | > 135 degree AND <= 225 degree | Days with southerly winds (135° < DD <= 225°). | Y | pass |
| DDwest | D | wind | DD | > 225 degree AND <= 315 degree | Days with westerly winds (225° < DD <= 315°). | Y | pass |
| GSL | A | cold | tg | — | Growing season length. | Y | pass (calendars standard, noleap, 360_day, all_leap) |
| SPI6 | A | rain | pr | — | 6-Month Standardized Precipitation Index. | Y | pass (in memory; chunks 1 and 7; within 0.30 of a direct scipy gamma fit) |
| SPI3 | A | rain | pr | — | 3-Month Standardized Precipitation Index. | Y | pass (in memory; chunks 1 and 7; within 0.30 of a direct scipy gamma fit) |
| PP | D | pressure | psl | — | Mean of daily sea level pressure (hPa). | Y | pass |
| SS | D | sunshine | sund | — | Sunshine duration (hours). | Y | pass |
| RH | D | humidity | hurs | — | Mean of daily relative humidity (%). | Y | pass |
| HI | E | drought | tg, tx | — | Huglin Index (degree_Celsius day): sum from 1 April to 30 September of ((TG - 10) + (TX - 10)) / 2 * K, K being the daylength coefficient of the latitude (the ATBD gives no K above 50 degrees north: the result is missing there). | Y | pass (dedicated tests: tests/test_ecad_hi.py) |
| BEDD | E | drought | tn, tx | — | Biologically Effective Degree Days (degree_Celsius day): sum from 1 April to 30 September of min(max((TX + TN) / 2 - 10, 0), 9). | Y | pass (dedicated tests: tests/test_ecad_bedd.py) |
