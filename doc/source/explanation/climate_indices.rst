What is a climate index
=======================

A climate index is a calculated value that can be used to describe the state and the changes in the climate system.
The climate at a defined place is the average state of the atmosphere over a longer period of, for example, months or years. Changes on climate are much slower than on the weather, that can change strongly day by day.

Climate indices allow a statistical study of variations of the dependent climatological aspects, such as analysis and comparison of time series, means, extremes and trends.


.. note::
    A good introduction for climate indices is on the website of the
    `Integrated Climate Data Center (ICDC) <https://icdc.cen.uni-hamburg.de/en/climate-indices.html>`_
    of the University of Hamburg.

.. seealso::
    - `Climate Variability and Predictability (CLIVAR) <https://www.clivar.org/clivar-panels/etccdi/indices-data/indices-data>`_
    - `Expert Team on Climate Change Detection and Indices (ETCCDI) <https://etccdi.pacificclimate.org/>`_
    - `European Climate Assessment & Dataset (ECA&D) <https://www.ecad.eu>`_
    - `ATBD ECA&D indices <https://www.ecad.eu/documents/atbd.pdf>`_
    - `Article about percentile-based indices <http://etccdi.pacificclimate.org/docs/Zhangetal05JumpPaper.pdf>`_
    - `Sample quantiles in statistical packages <https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_

icclim capabilities
===================

Currently, the 49 climate indices as defined by
`European Climate Assessment & Dataset <https://www.ecad.eu/>`_ based on
air temperature and precipitation variables can be computed with icclim:

    - 11 cold indices (GD4, CFD, FD, HD17, ID, CSDI, TG10p, TN10p, TX10p, TXn, TNn)
    - 1 drought indice (CDD)
    - 9 heat indices (SU, TR, WSDI, TG90p, TN90p, TX90p, TXx, TNx, CSU)
    - 14 rain indices (PRCPTOT, RR1, SDII, CWD, R10mm, R20mm, RX1day, RX5day, R75p, R75pTOT, R95p, R95pTOT, R99p, R99pTOT)
    - 4 snow indices (SD, SD1, SD5cm, SD50cm)
    - 6 temperature indices (TG, TN, TX, DTR, ETR, vDTR)
    - 4 compound indices (CD, CW, WD, WW)

Detailed description of each indice is available at https://www.ecad.eu/documents/atbd.pdf.
See table below for a short description of each indices.
The description is extracted from clix-meta.
Initially icclim was designed for online computing of climate indices through the `climate4impact portal <https://climate4impact.eu>`_.
In spite of existence of other packages able to compute climate indices (`CDO <https://code.mpimet.mpg.de/projects/cdo>`_, `R package <https://etccdi.pacificclimate.org/resources/software-library>`_ ),
it was decided to develop a new software in Python.
Python language was first of all chosen to interface with `PyWPS <https://pywps.org/>`_: Python implementation of Web Processing Service
(WPS) Standard.
Another reason was to interface eventually with the `OpenClimateGIS <https://github.com/NCPP/ocgis/>`_.

+-----------------+------------------------------------------------------------+
| short name      |   Description                                              |
+=================+============================================================+
| TG              |   Mean of daily mean temperature                           |
+-----------------+------------------------------------------------------------+
| TN              |   Mean of daily minimum temperature                        |
+-----------------+------------------------------------------------------------+
| TX              |   Mean of daily maximum temperature                        |
+-----------------+------------------------------------------------------------+
| DTR             |   Mean Diurnal Temperature Range                           |
+-----------------+------------------------------------------------------------+
| ETR             |   Intra-period extreme temperature range                   |
+-----------------+------------------------------------------------------------+
| vDTR            |   Mean day-to-day variation in Diurnal Temperature Range   |
+-----------------+------------------------------------------------------------+
| SU              |   Number of Summer Days (Tmax > 25C)                       |
+-----------------+------------------------------------------------------------+
| TR              |   Number of Tropical Nights (Tmin > 20C)                   |
+-----------------+------------------------------------------------------------+
| WSDI            |                                                            |
+-----------------+------------------------------------------------------------+
| TG90p           |   Percentage of days when Tmean > 90th percentile          |
+-----------------+------------------------------------------------------------+
| TN90p           |   Percentage of days when Tmin > 90th percentile           |
+-----------------+------------------------------------------------------------+
| TX90p           |   Percentage of days when Tmax > 90th percentile           |
+-----------------+------------------------------------------------------------+
| TXx             |   Maximum daily maximum temperature                        |
+-----------------+------------------------------------------------------------+
| TNx             |   Maximum daily minimum temperature                        |
+-----------------+------------------------------------------------------------+
| CSU             |   Maximum number of consecutive summer days (Tmax >25 C)   |
+-----------------+------------------------------------------------------------+
| GD4             |   Growing degree days (sum of Tmean > 4 C)                 |
+-----------------+------------------------------------------------------------+
| FD              |   Number of Frost Days (Tmin < 0C)                         |
+-----------------+------------------------------------------------------------+
| CFD             |   Maximum number of consecutive frost days (Tmin < 0 C)    |
+-----------------+------------------------------------------------------------+
| HD17            |   Heating degree days (sum of Tmean < 17 C)                |
+-----------------+------------------------------------------------------------+
| ID              |   Number of sharp Ice Days (Tmax < 0C)                     |
+-----------------+------------------------------------------------------------+
| TG10p           |   Percentage of days when Tmean < 10th percentile          |
+-----------------+------------------------------------------------------------+
| TN10p           |   Percentage of days when Tmin < 10th percentile           |
+-----------------+------------------------------------------------------------+
| TX10p           |   Percentage of days when Tmax < 10th percentile           |
+-----------------+------------------------------------------------------------+
| TXn             |   Minimum daily maximum temperature                        |
+-----------------+------------------------------------------------------------+
| TNn             |   Minimum daily minimum temperature                        |
+-----------------+------------------------------------------------------------+
| CSDI            |                                                            |
+-----------------+------------------------------------------------------------+
| CDD             |   Maximum consecutive dry days (Precip < 1mm)              |
+-----------------+------------------------------------------------------------+
| PRCPTOT         |   Total precipitation during Wet Days                      |
+-----------------+------------------------------------------------------------+
| RR1             |   Number of Wet Days (precip >= 1 mm)                      |
+-----------------+------------------------------------------------------------+
| SDII            |   Average precipitation during Wet Days (SDII)             |
+-----------------+------------------------------------------------------------+
| CWD             |   Maximum consecutive wet days (Precip >= 1mm)             |
+-----------------+------------------------------------------------------------+
| R10mm           |   Number of heavy precipitation days (Precip >=10mm)       |
+-----------------+------------------------------------------------------------+
| R20mm           |   Number of very heavy precipitation days (Precip >= 20mm) |
+-----------------+------------------------------------------------------------+
| RX1day          |   Maximum 1-day precipitation                              |
+-----------------+------------------------------------------------------------+
| RX5day          |   Maximum 5-day precipitation                              |
+-----------------+------------------------------------------------------------+
| R75p            |                                                            |
+-----------------+------------------------------------------------------------+
| R75pTOT         |                                                            |
+-----------------+------------------------------------------------------------+
| R95p            |                                                            |
+-----------------+------------------------------------------------------------+
| R95pTOT         |                                                            |
+-----------------+------------------------------------------------------------+
| R99p            |                                                            |
+-----------------+------------------------------------------------------------+
| R99pTOT         |                                                            |
+-----------------+------------------------------------------------------------+
| SD              |   Mean of daily snow depth                                 |
+-----------------+------------------------------------------------------------+
| SD1             |   Snow days (SD >= 1 cm)                                   |
+-----------------+------------------------------------------------------------+
| SD5cm           |   Number of days with snow depth >= 5 cm                   |
+-----------------+------------------------------------------------------------+
| SD50cm          |   Number of days with snow depth >= 50 cm                  |
+-----------------+------------------------------------------------------------+
| CD              |                                                            |
+-----------------+------------------------------------------------------------+
| CW              |                                                            |
+-----------------+------------------------------------------------------------+
| WD              |                                                            |
+-----------------+------------------------------------------------------------+
| WW              |                                                            |
+-----------------+------------------------------------------------------------+
