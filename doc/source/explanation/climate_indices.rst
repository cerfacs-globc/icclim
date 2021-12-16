What is a climate index
=======================
A climate index is a calculated value that can be used to describe the state and the changes in the climate system.
The climate at a defined place is the average state of the atmosphere over a longer period of, for example, months or years. Changes on climate are much slower than on the weather, that can change strongly day by day.

Climate indices allow a statistical study of variations of the dependent climatological aspects, such as analysis and comparison of time series, means, extremes and trends.


.. note::
   A good introduction for climate indices is on the website of the`Integrated Climate Data Center (ICDC) <https://icdc.cen.uni-hamburg.de/en/climate-indices.html>`_
   of the University of Hamburg.

.. seealso::
   - `Climate Variability and Predictability (CLIVAR) <https://www.clivar.org/clivar-panels/etccdi/indices-data/indices-data>`_
   - `Expert Team on Climate Change Detection and Indices (ETCCDI) <https://etccdi.pacificclimate.org/>`_
   - `European Climate Assessment & Dataset (ECA&D) <https://www.ecad.eu>`_
   - `ATBD ECA&D indices <https://www.ecad.eu/documents/atbd.pdf>`_
   - `Article about percentile-based indices <http://etccdi.pacificclimate.org/docs/Zhangetal05JumpPaper.pdf>`_
   - `Sample quantiles in statistical packages <https://www.amherst.edu/media/view/129116/original/Sample+Quantiles.pdf>`_

Icclim capabilities
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

Initially Icclim was designed for online computing of climate indices through the `climate4impact portal <https://climate4impact.eu>`_.
In spite of existence of other packages able to compute climate indices (`CDO <https://code.mpimet.mpg.de/projects/cdo>`_, `R package <https://etccdi.pacificclimate.org/resources/software-library>`_ ),
it was decided to develop a new software in Python.
Python language was first of all chosen to interface with `PyWPS <https://pywps.org/>`_: Python implementation of Web Processing Service
(WPS) Standard.
Another reason was to interface eventually with the `OpenClimateGIS <https://github.com/NCPP/ocgis/>`_.
