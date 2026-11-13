#########################
 What is a climate index
#########################

A climate index is a calculated value that can be used to describe the
state and the changes in the climate system. The climate at a defined
place is the average state of the atmosphere over a longer period of,
for example, months or years. Changes on climate are much slower than on
the weather, that can change strongly day by day.

Climate indices allow a statistical study of variations of the dependent
climatological aspects, such as analysis and comparison of time series,
means, extremes and trends.

.. note::

   A good introduction for climate indices is on the website of the
   `Integrated Climate Data Center (ICDC)
   <https://icdc.cen.uni-hamburg.de/en/climate-indices.html>`_ of the
   University of Hamburg.

 .. seealso::

   - `Climate Variability and Predictability (CLIVAR) <https://www.clivar.org/clivar-panels/etccdi/indices-data/indices-data>`_
   - `Expert Team on Climate Change Detection and Indices (ETCCDI) <https://etccdi.pacificclimate.org/>`_
   - `European Climate Assessment & Dataset (ECA&D) <https://www.ecad.eu>`_
   - `ATBD ECA&D indices <https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf>`_
   - `Article about percentile-based indices <http://etccdi.pacificclimate.org/docs/Zhangetal05JumpPaper.pdf>`_
   - `Sample quantiles in statistical packages <https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_

#####################
 icclim capabilities
#####################

Currently, the climate indices as defined by `European Climate
Assessment & Dataset <https://www.ecad.eu/>`_ based on air temperature
and precipitation variables can be computed with icclim:

   -  11 cold indices (GD4, CFD, FD, HD17, ID, CSDI, TG10p, TN10p,
      TX10p, TXn, TNn)
   -  3 drought indices (CDD, HI, BEDD)
   -  9 heat indices (SU, TR, WSDI, TG90p, TN90p, TX90p, TXx, TNx, CSU)
   -  14 rain indices (PRCPTOT, RR1, SDII, CWD, R10mm, R20mm, RX1day,
      RX5day, R75p, R75pTOT, R95p, R95pTOT, R99p, R99pTOT)
   -  4 snow indices (SD, SD1, SD5cm, SD50cm)
   -  6 temperature indices (TG, TN, TX, DTR, ETR, vDTR)
   -  4 compound indices (CD, CW, WD, WW)

Detailed description of each indice is available at
https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf. See
table below for a short description of each indices. Most descriptions
are extracted from clix-meta. Initially icclim was designed for online
computing of climate indices through the `climate4impact portal
<https://climate4impact.eu>`_. In spite of existence of other packages
able to compute climate indices (`CDO
<https://code.mpimet.mpg.de/projects/cdo>`_, `R package
<https://etccdi.pacificclimate.org/resources/software-library>`_ ), it
was decided to develop a new software in Python. Python language was
first of all chosen to interface with `PyWPS <https://pywps.org/>`_:
Python implementation of Web Processing Service (WPS) Standard. Another
reason was to interface eventually with the `OpenClimateGIS
<https://github.com/NCPP/ocgis/>`_.

+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| short name      | Description                                                                                                                         |
+=================+=====================================================================================================================================+
| TG              | Mean of daily mean temperature                                                                                                      |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TN              | Mean of daily minimum temperature                                                                                                   |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TX              | Mean of daily maximum temperature                                                                                                   |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| DTR             | Mean Diurnal Temperature Range                                                                                                      |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| ETR             | Intra-period extreme temperature range                                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| vDTR            | Mean day-to-day variation in Diurnal Temperature Range                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SU              | Number of Summer Days (Tmax > 25C)                                                                                                  |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TR              | Number of Tropical Nights (Tmin > 20C)                                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| WSDI            | Warm-spell duration index                                                                                                           |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TG90p           | Percentage of days when Tmean > 90th percentile                                                                                     |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TN90p           | Percentage of days when Tmin > 90th percentile                                                                                      |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TX90p           | Percentage of days when Tmax > 90th percentile                                                                                      |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TXx             | Maximum daily maximum temperature                                                                                                   |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TNx             | Maximum daily minimum temperature                                                                                                   |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CSU             | Maximum number of consecutive summer days (Tmax >25 C)                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| GD4             | Growing degree days (sum of Tmean > 4 C)                                                                                            |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| FD              | Number of Frost Days (Tmin < 0C)                                                                                                    |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CFD             | Maximum number of consecutive frost days (Tmin < 0 C)                                                                               |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| HD17            | Heating degree days (sum of Tmean < 17 C)                                                                                           |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| ID              | Number of sharp Ice Days (Tmax < 0C)                                                                                                |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TG10p           | Percentage of days when Tmean < 10th percentile                                                                                     |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TN10p           | Percentage of days when Tmin < 10th percentile                                                                                      |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TX10p           | Percentage of days when Tmax < 10th percentile                                                                                      |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TXn             | Minimum daily maximum temperature                                                                                                   |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| TNn             | Minimum daily minimum temperature                                                                                                   |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CSDI            | Cold-spell duration index                                                                                                           |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CDD             | Maximum consecutive dry days (Precip < 1mm)                                                                                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| PRCPTOT         | Total precipitation during Wet Days                                                                                                 |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| RR1             | Number of Wet Days (precip >= 1 mm)                                                                                                 |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SDII            | Average precipitation during Wet Days (SDII)                                                                                        |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CWD             | Maximum consecutive wet days (Precip >= 1mm)                                                                                        |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R10mm           | Number of heavy precipitation days (Precip >=10mm)                                                                                  |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R20mm           | Number of very heavy precipitation days (Precip >= 20mm)                                                                            |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| RX1day          | Maximum 1-day precipitation                                                                                                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| RX5day          | Maximum 5-day precipitation                                                                                                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R75p            | (in discussion) Days with RR > 75th percentile of daily amounts (wet days)                                                          |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R75pTOT         | (in discussion) Precipitation fraction due to very wet days (> 75th percentile)                                                     |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R95p            | (in discussion) Days with RR > 95th percentile of daily amounts (very wet days)                                                     |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R95pTOT         | (in discussion) Precipitation fraction due to very wet days (> 95th percentile)                                                     |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R99p            | (in discussion) Days with RR > 99th percentile of daily amounts (extremely wet days)                                                |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| R99pTOT         | (in discussion) Precipitation fraction due to very wet days (> 99th percentile)                                                     |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SD              | Mean of daily snow depth                                                                                                            |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SD1             | Snow days (SD >= 1 cm)                                                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SD5cm           | Number of days with snow depth >= 5 cm                                                                                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| SD50cm          | Number of days with snow depth >= 50 cm                                                                                             |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| HI              | Huglin Index: sum from 1 April to 30 September of ((TG - 10) + (TX - 10)) / 2 * K (see the note below)                              |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| BEDD            | Biologically Effective Degree Days: sum from 1 April to 30 September of min(max((TX + TN) / 2 - 10, 0), 9)                          |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CD              | Days with TG < 25th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| CW              | Days with TG < 25th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| WD              | Days with TG > 75th percentile of daily mean temperature and RR <25th percentile of daily precipitation sum                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| WW              | Days with TG > 75th percentile of daily mean temperature and RR >75th percentile of daily precipitation sum                         |
+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+

.. note::

   **Huglin Index (HI), ECA&D ATBD v11.** K is the daylength coefficient of the
   latitude. Each band includes its upper boundary:

   - latitude from 0 to 40 N: K = 1.00
   - above 40 and up to 42 N: K = 1.02
   - above 42 and up to 44 N: K = 1.03
   - above 44 and up to 46 N: K = 1.04
   - above 46 and up to 48 N: K = 1.05
   - above 48 and up to 50 N: K = 1.06

   The index is defined for the northern hemisphere only: the result is missing at
   latitudes below 0 (southern hemisphere) and above 50 degrees north. The latitude is
   read from the coordinates of the data. The daily terms are not clipped at 0.

.. _two_variable_indices_order:

******************************************************
Indices with two variables: the order of ``var_name``
******************************************************

For the indices that take two variables, the order of the names of ``var_name`` is
positional: the first name is the first term of the formula. The result of the
following indices depends on it:

- ``DTR`` is the mean of ``TX - TN``: the first name is the daily maximum temperature,
  the second one is the daily minimum temperature,
  ``icclim.dtr(ds, var_name=["tasmax", "tasmin"])``. With the names in the other order
  the result is the mean of ``TN - TX``, negative.
- ``ETR`` is ``max(TX) - min(TN)`` over each period,
  ``icclim.etr(ds, var_name=["tasmax", "tasmin"])``. With the names in the other order
  it is ``max(TN) - min(TX)``, a different quantity, not the opposite.
- ``CD``, ``CW``, ``WD`` and ``WW`` take the daily mean temperature first and the daily
  precipitation second, ``icclim.cd(ds, var_name=["tas", "pr"],
  base_period_time_range=["1961-01-01", "1990-12-31"])``. The two variables are not
  interchangeable: swapped, the temperature is compared with a precipitation threshold
  and the units do not match.

``vDTR``, ``HI`` and ``BEDD`` do not depend on the order of their two variables. The
same rule holds for the generic indices ``mean_of_difference`` and
``difference_of_extremes`` (the first and the second variable, see
:ref:`generic_indices_recipes`), and for ``difference_of_means`` with two variables (the
study first, then the reference).
