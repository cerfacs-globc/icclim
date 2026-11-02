# ECAD independent-oracle inventory

Generated from `EcadIndexRegistry` on the 7.3.1 release line. Definitions are ECA&D ATBD v11 registry text.

| name | family | group | source variables | threshold | definition | oracle written | result |
|---|---|---|---|---|---|---|---|
| TG | D | temperature | tg | — | Mean of daily mean temperature. | N | pending |
| TN | D | temperature | tn | — | Mean of daily minimum temperature. | N | pending |
| TX | D | temperature | tx | — | Mean of daily maximum temperature. | N | pending |
| DTR | D | temperature | tx, tn | — | Mean Diurnal Temperature Range. | N | pending |
| ETR | D | temperature | tx, tn | — | Intra-period extreme temperature range. | N | pending |
| vDTR | D | temperature | tx, tn | — | Mean day-to-day variation in Diurnal Temperature Range. | N | pending |
| SU | C | heat | tx | > 25 degree_Celsius | Number of Summer Days (Tmax > 25C). | Y | pass |
| TR | C | heat | tn | > 20 degree_Celsius | Number of Tropical Nights (Tmin > 20C). | Y | pass |
| WSDI | B | heat | tx | > 90 doy_per | Warm-spell duration index (days). | Y | pass; bootstrap xfail #540 |
| TG90p | B | heat | tg | > 90 doy_per | Days when Tmean > 90th percentile. | Y | pass; bootstrap xfail #540 |
| TN90p | B | heat | tn | > 90 doy_per | Days when Tmin > 90th percentile. | Y | pass; bootstrap xfail #540 |
| TX90p | B | heat | tx | > 90 doy_per | Days when Tmax > 90th daily percentile. | Y | pass; bootstrap xfail #540 |
| TXx | D | heat | tx | — | Maximum daily maximum temperature. | N | pending |
| TNx | D | heat | tn | — | Maximum daily minimum temperature. | N | pending |
| CSU | C | heat | tx | > 25 degree_Celsius | Maximum number of consecutive summer days (Tmax >25 C). | Y | xfail #542 dims; xfail #543 cross-year run |
| GD4 | C | cold | tg | 4 degree_Celsius | Growing degree days (sum of Tmean > 4 C). | Y | pass |
| FD | C | cold | tn | < 0 degree_Celsius | Number of Frost Days (Tmin < 0C). | Y | pass |
| CFD | C | cold | tn | < 0 degree_Celsius | Maximum number of consecutive frost days (Tmin < 0 C). | Y | xfail #542 dims; xfail #543 cross-year run |
| HD17 | C | cold | tg | 17 degree_Celsius | Heating degree days (sum of Tmean < 17 C). | Y | pass |
| ID | C | cold | tx | < 0 degree_Celsius | Number of sharp Ice Days (Tmax < 0C). | Y | pass |
| TG10p | B | cold | tg | < 10 doy_per | Days when Tmean < 10th percentile. | Y | pass; bootstrap xfail #540 |
| TN10p | B | cold | tn | < 10 doy_per | Days when Tmin < 10th percentile. | Y | pass; bootstrap xfail #540 |
| TX10p | B | cold | tx | < 10 doy_per | Days when Tmax < 10th percentile. | Y | pass; bootstrap xfail #540 |
| TXn | D | cold | tx | — | Minimum daily maximum temperature. | N | pending |
| TNn | D | cold | tn | — | Minimum daily minimum temperature. | N | pending |
| CSDI | B | cold | tn | < 10 doy_per | Cold-spell duration index (days). | Y | pass; bootstrap xfail #540 |
| CDD | C | drought | pr | < 1 mm/day | Maximum consecutive dry days (Precip < 1mm). | Y | pass values; xfail #542 dims |
| PRCPTOT | D | rain | pr | >= 1 mm/day | Total precipitation during Wet Days. | N | pending |
| RR1 | C | rain | pr | >= 1 mm/day | Number of Wet Days (precip >= 1 mm). | Y | pass |
| SDII | D | rain | pr | >= 1 mm/day | Average precipitation during Wet Days (SDII). | N | pending |
| CWD | C | rain | pr | >= 1 mm/day | Maximum consecutive wet days (Precip >= 1mm). | Y | pass values; xfail #542 dims |
| RR | D | rain | pr | — | Precipitation sum (mm). | N | pending |
| R10mm | C | rain | pr | >= 10 mm/day | Number of heavy precipitation days (Precip >=10mm). | Y | pass |
| R20mm | C | rain | pr | >= 20 mm/day | Number of very heavy precipitation days (Precip >= 20mm). | Y | pass |
| RX1day | D | rain | pr | — | Maximum 1-day total precipitation. | N | pending |
| RX5day | D | rain | pr | — | Maximum 5-day total precipitation. | N | pending |
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
| CD | C | temperature_rain | tg, pr | ['< 25 doy_per', {'query': '< 25 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG < 25th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (cold/dry days). | Y | xfail #541 wet-day floor |
| CW | C | temperature_rain | tg, pr | ['< 25 doy_per', {'query': '> 75 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG < 25th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (cold/wet days). | Y | pass |
| WD | C | temperature_rain | tg, pr | ['> 75 doy_per', {'query': '< 25 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG > 75th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum (warm/dry days). | Y | xfail #541 wet-day floor |
| WW | C | temperature_rain | tg, pr | ['> 75 doy_per', {'query': '> 75 period_per', 'threshold_min_value': '1 mm/day'}] | Days with TG > 75th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum (warm/wet days). | Y | pass |
| FXx | D | wind | wsgs_max | — | Maximum value of daily maximum wind gust. | N | pending |
| FG6Bft | D | wind | sfcWind | >= 10.8 m s-1 | Days with daily averaged wind ≥ 6 Bft (10.8 m s-1). | N | pending |
| FGcalm | D | wind | sfcWind | <= 2 m s-1 | Calm days, days with daily averaged wind <= 2 m s-1. | N | pending |
| FG | D | wind | sfcWind | — | Mean of daily mean wind strength. | N | pending |
| DDnorth | D | wind | DD | > 315 degree OR <= 45 degree | Days with northerly winds (DD > 315° or DD ≤ 45°). | N | pending |
| DDeast | D | wind | DD | > 45 degree AND <= 135 degree | Days with easterly winds (45° < DD <= 135°). | N | pending |
| DDsouth | D | wind | DD | > 135 degree AND <= 225 degree | Days with southerly winds (135° < DD <= 225°). | N | pending |
| DDwest | D | wind | DD | > 225 degree AND <= 315 degree | Days with westerly winds (225° < DD <= 315°). | N | pending |
| GSL | A | cold | tg | — | Growing season length. | Y | xfail #537 strict boundary; xfail #538 completeness; other cases pass |
| SPI6 | A | rain | pr | — | 6-Month Standardized Precipitation Index. | Y | pass (eager; chunks 1, 7) |
| SPI3 | A | rain | pr | — | 3-Month Standardized Precipitation Index. | Y | pass (eager; chunks 1, 7) |
| PP | D | pressure | psl | — | Mean of daily sea level pressure (hPa). | N | pending |
| SS | D | sunshine | sund | — | Sunshine duration (hours). | N | pending |
| RH | D | humidity | hurs | — | Mean of daily relative humidity (%). | N | pending |
