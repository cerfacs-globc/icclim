.. _validation:

#########################################
 How the indices are validated
#########################################

This page describes how the results of icclim are checked, which sources the
checks rely on, what they found, and what they do not cover. It is written for
users who need to know how far the values can be trusted, and for contributors who
add an index.

Scope and sources
=================

The checks concern the 66 ECA&D indices of the registry, the 32 DCSC indices and the
generic indices. The definitions come from the following sources:

- the ECA&D indices follow the `Algorithm Theoretical Basis Document (ATBD), version
  11 <https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf>`_;
- for the indices that RClimDex and climdex also define, in particular the
  consecutive dry and wet days (``CDD`` and ``CWD``), the ATBD is compared with the
  RClimDex manual and with climdex.pcic. The three agree that a run of days is
  counted in the period where it ends;
- the DCSC indices follow the catalogue of the DRIAS portal of Météo-France, which is
  the only definition available for them;
- the Huglin Index (``HI``) follows the ATBD, which cites Huglin (1978) for the index
  and gives the table of the daylength coefficient.

Where the sources differ, the ATBD is the reference for the ECA&D indices and the
difference is written in the documentation of the index.

Independent reference calculations
==================================

An audit of the ECA&D indices against their definitions was carried out for the 7.3
releases. For each index the definition was written again as an independent
reference calculation: plain numpy and pandas code, written from the text of the
definition, day by day, without any call to icclim or xclim. The result of icclim is
compared with it on small datasets that can be checked by hand (a few years, a
handful of grid points, values chosen so that the expected result is known).

The reference calculations are run on the following edge cases:

- **missing values**, with the completeness check switched off and with the default
  completeness policy;
- **seasons that cross the end of the year**, for example ``ONDJFM``, and runs of
  days that cross the end of an output period;
- **units**: temperatures in K, degC and degF, precipitation in kg m-2 s-1 and
  mm/day, snow depth in m and cm;
- **calendars**: ``standard``, ``noleap``, ``360_day`` and ``all_leap`` for the
  growing season length, and ``noleap`` for the percentile indices;
- **in memory and chunked**: every case is also run with Dask chunks of 1 and 7
  days.

The reference-calculation tests (in tests/ecad_oracles/) cover 64 of the ECA&D
indices. ``HI`` and ``BEDD`` have their own tests with their own reference
calculation (``tests/test_ecad_hi.py`` and ``tests/test_ecad_bedd.py``). Therefore
**all 66 ECA&D indices have an independent reference calculation**; none is missing.
They are grouped in four families:

- family A: indices with a specific algorithm (``GSL``, ``SPI3``, ``SPI6``);
- family B: indices based on percentiles, including the spell indices ``WSDI`` and
  ``CSDI``;
- family C: counts, runs and sums above or below a fixed threshold, and the compound
  indices;
- family D: statistics (means, extremes, ranges) and the wind and weather counts.

A second set of tests of the ECA&D values, in the ``tests`` directory, repeats the
comparison for most indices with other datasets.

Consistency tests
=================

These tests need no expected value. They transform the input or the call in a way
whose effect on the result is known, and check that the result follows.

- **Unit equivalence** (``tests/test_unit_equivalence.py``): the same data given in
  K, degC and degF, or in kg m-2 s-1 and mm/day, must give the same result, in memory
  and chunked, and the units of the output must be equivalent. The test runs on 122
  cases: 56 of the ECA&D registry (51 indices with a temperature or precipitation
  input, five of them called twice in one process because the text of the units
  changes after the first call), the 32 DCSC indices and 34 generic indices. It is
  built from the registries, so a new index is included without any change.
- **Dask chunks and dimension order**: the result must not depend on how the data are
  chunked (``tests/test_metamorphic_properties.py``), nor on the order of the
  dimensions, nor on the type of the time index.
- **Subset against slice**: a yearly result on a subset of the period must be the
  one of the same year on the whole period, and monthly counts and sums must add up to
  the yearly ones.
- **Missing days**: a missing day masks only its own period and grid point by
  default, and complete data are never masked.
- **Bootstrap paths**: the routing and the primitives of the percentile bootstrap are
  tested (``tests/test_bootstrap_capability.py`` and
  ``tests/test_bootstrap_primitives.py``), and the fast path is compared with the
  reference bootstrap path on real data, see the next section.

Comparisons between releases and performance
============================================

Beyond synthetic data, the results are compared on real model data. The 65 years of
daily ACCESS-CM2 historical simulations (1950--2014) over a subset of 28 latitudes
and 21 longitudes are used, and the tasmax of EC-Earth3 for part of the checks. The
tools ``tools/run_real_data_validation.py`` and
``tools/compare_real_data_validation.py`` run an index with two versions of the
code on the same files and compare the outputs: numerical variables must agree within
an absolute and relative tolerance of 1e-10, other variables must be equal, and the
number of grid points that changed is reported.

Examples recorded in the developer documentation (:doc:`../dev/percentile_bootstrap`
and :doc:`../dev/bootstrap_optimization_summary`):

- the annual ``TG90p`` with the fast bootstrap path differs from the reference
  bootstrap path by at most 8.6e-14, with no Dask task instead of 4,691,198;
- the mask of a spell index matched all 13,959,708 daily values of the reference, and
  the annual average of the same data matched all 38,220 grid-point values of the
  reference, with identical coordinates and attributes;
- the date-event indices, computed with vectorized reducers, went from about 2 hours
  to about 1 minute on the ACCESS-CM2 benchmark with identical results.

Performance benchmarks of the paths that do not use the bootstrap are described in
:doc:`../dev/non_bootstrap_benchmarking`, and the invariants that a performance change
must keep in :doc:`../dev/non_bootstrap_performance`.

What the validation found
=========================

The audit and the consistency tests found differences with the definitions. They
are fixed and documented in the :doc:`release notes <../references/release_notes>`:

- growing season length: the onset must be strict (``TG > 5 degC``) and the
  completeness must be honoured for isolated missing values
  (`#537 <https://github.com/cerfacs-globc/icclim/issues/537>`_ and
  `#538 <https://github.com/cerfacs-globc/icclim/issues/538>`_);
- the leave-one-year-out bootstrap of the temperature percentile counts was not
  averaged (`#540 <https://github.com/cerfacs-globc/icclim/issues/540>`_);
- ``CD`` and ``WD`` did not restrict the precipitation to wet days, and the thresholds
  of the compound indices ignored the requested base period and window
  (`#541 <https://github.com/cerfacs-globc/icclim/issues/541>`_ and
  `#560 <https://github.com/cerfacs-globc/icclim/issues/560>`_);
- the dimension order of the run indices followed the version of xclim
  (`#542 <https://github.com/cerfacs-globc/icclim/issues/542>`_);
- a run of days across the end of an output period is now attributed to the period
  where it ends, and can be split with ``split_runs_at_period_boundary``
  (`#580 <https://github.com/cerfacs-globc/icclim/issues/580>`_ and
  `#543 <https://github.com/cerfacs-globc/icclim/issues/543>`_);
- ``RX5day`` did not accept a precipitation flux
  (`#544 <https://github.com/cerfacs-globc/icclim/issues/544>`_);
- the DCSC indices ``TXHWD``, ``TNCWD``, ``TNND``, ``TXND`` and ``TNHT`` did not follow
  the DRIAS catalogue
  (`#616 <https://github.com/cerfacs-globc/icclim/issues/616>`_ and
  `#620 <https://github.com/cerfacs-globc/icclim/issues/620>`_);
- the DCSC indices that use a normal failed with input in degC or degF
  (`#617 <https://github.com/cerfacs-globc/icclim/issues/617>`_), and the
  unit-equivalence test then found that ``PQ90`` and ``PQ99`` declared a percent as
  output unit for precipitation in mm/day
  (`#643 <https://github.com/cerfacs-globc/icclim/issues/643>`_) and that the generic
  ``excess`` and ``deficit`` of a precipitation failed with recent versions of xarray
  (`#644 <https://github.com/cerfacs-globc/icclim/issues/644>`_).

Limits of the validation
========================

- The reference calculations use small synthetic datasets. They show that the code
  implements the definition, not that the definition is the best choice for a given
  study. The comparisons on real model data are comparisons between versions and
  between code paths, not with an external product.
- The 32 DCSC indices have no independent source other than the DRIAS catalogue: they
  are checked against the definition of the catalogue and by the consistency tests.
- Nine indices of the ATBD are not implemented (``CC``, ``CC2``, ``CC6``, ``UTCI``,
  ``TCI``, ``TCI60``, ``TCI80``, ``PET`` and ``SSp``); the list is followed in
  `#204 <https://github.com/cerfacs-globc/icclim/issues/204>`_.
- ``SPI3`` and ``SPI6`` are compared with a direct gamma fit by maximum likelihood
  with scipy. The two fits do not give the same parameters, and the comparison accepts
  an absolute difference of 0.30 in the index. It shows that the values have the
  right size and sign and follow the precipitation, not that they agree to the
  last digit with another implementation.
- For ``CDD`` and ``CWD`` the ATBD states that a spell is counted in the year where it
  ends, and RClimDex agrees. For ``CFD``, ``CSU`` and the other run-length indices no
  rule is written, and the reference calculations follow the convention decided in
  `#580 <https://github.com/cerfacs-globc/icclim/issues/580>`_: a run is credited,
  whole, to the period where it ends. ``run_index="first"`` and
  ``split_runs_at_period_boundary=True`` are available as options.
- ``CD``, ``WD`` and ``WW`` can differ by one day at the edges of a subset base period
  (`#559 <https://github.com/cerfacs-globc/icclim/issues/559>`_).
- There is **no bit-for-bit guarantee between versions**. The results depend on the
  versions of xclim, xarray, numpy and scipy; a change of version can change the last
  digits, and the comparisons between versions accept a tolerance of 1e-10.

Table of the ECA&D indices
==========================

The table is built from the tests of the repository. "Unit equivalence" means that the
index is in the unit-equivalence test; the indices without it have an input that is
neither a temperature nor a precipitation (snow depth, wind, pressure, sunshine and
humidity). The families are described above.

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - Index
     - Reference source
     - Validation tests
     - Notes
   * - TG
     - ATBD v11
     - family D; unit equivalence
     -
   * - TN
     - ATBD v11
     - family D; unit equivalence
     -
   * - TX
     - ATBD v11
     - family D; unit equivalence
     -
   * - DTR
     - ATBD v11
     - family D; unit equivalence
     -
   * - ETR
     - ATBD v11
     - family D; unit equivalence
     -
   * - vDTR
     - ATBD v11
     - family D; unit equivalence
     - Day-to-day differences across the boundary of a period are excluded.
   * - SU
     - ATBD v11
     - family C; unit equivalence
     -
   * - TR
     - ATBD v11
     - family C; unit equivalence
     -
   * - WSDI
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - TG90p
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - TN90p
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - TX90p
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison. Also compared with the leave-one-year-out bootstrap of the ATBD.
   * - TXx
     - ATBD v11
     - family D; unit equivalence
     -
   * - TNx
     - ATBD v11
     - family D; unit equivalence
     -
   * - CSU
     - ATBD v11
     - family C; unit equivalence
     - A run is attributed to the period where it ends; with ``split_runs_at_period_boundary=True`` the result is checked.
   * - GD4
     - ATBD v11
     - family C; unit equivalence
     -
   * - FD
     - ATBD v11
     - family C; unit equivalence
     -
   * - CFD
     - ATBD v11
     - family C; unit equivalence
     - A run is attributed to the period where it ends, as in the ATBD, RClimDex and climdex; with ``split_runs_at_period_boundary=True`` the result is checked.
   * - HD17
     - ATBD v11
     - family C; unit equivalence
     -
   * - ID
     - ATBD v11
     - family C; unit equivalence
     -
   * - TG10p
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - TN10p
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - TX10p
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - TXn
     - ATBD v11
     - family D; unit equivalence
     -
   * - TNn
     - ATBD v11
     - family D; unit equivalence
     -
   * - CSDI
     - ATBD v11
     - family B; unit equivalence
     - Day-of-year percentile of a 5-day window (type 8), strict comparison.
   * - CDD
     - ATBD v11; RClimDex; climdex
     - family C; unit equivalence
     - A run is attributed to the period where it ends, as in the ATBD, RClimDex and climdex.
   * - PRCPTOT
     - ATBD v11
     - family D; unit equivalence
     -
   * - RR1
     - ATBD v11
     - family C; unit equivalence
     -
   * - SDII
     - ATBD v11
     - family D; unit equivalence
     -
   * - CWD
     - ATBD v11; RClimDex; climdex
     - family C; unit equivalence
     - A run is attributed to the period where it ends, as in the ATBD, RClimDex and climdex.
   * - RR
     - ATBD v11
     - family D; unit equivalence
     -
   * - R10mm
     - ATBD v11
     - family C; unit equivalence
     -
   * - R20mm
     - ATBD v11
     - family C; unit equivalence
     -
   * - RX1day
     - ATBD v11
     - family D; unit equivalence
     -
   * - RX5day
     - ATBD v11
     - family D; unit equivalence
     - Also checked with the precipitation in kg m-2 s-1.
   * - R75p
     - ATBD v11
     - family B; unit equivalence
     - Percentile of the wet days (RR >= 1 mm).
   * - R75pTOT
     - ATBD v11
     - family B; unit equivalence
     - Percentile of the wet days (RR >= 1 mm).
   * - R95p
     - ATBD v11
     - family B; unit equivalence
     - Percentile of the wet days (RR >= 1 mm).
   * - R95pTOT
     - ATBD v11
     - family B; unit equivalence
     - Percentile of the wet days (RR >= 1 mm).
   * - R99p
     - ATBD v11
     - family B; unit equivalence
     - Percentile of the wet days (RR >= 1 mm).
   * - R99pTOT
     - ATBD v11
     - family B; unit equivalence
     - Percentile of the wet days (RR >= 1 mm).
   * - SD
     - ATBD v11
     - family C
     - Snow depth in m and cm.
   * - SD1
     - ATBD v11
     - family C
     - Snow depth in m and cm.
   * - SD5cm
     - ATBD v11
     - family C
     - Snow depth in m and cm.
   * - SD50cm
     - ATBD v11
     - family C
     - Snow depth in m and cm.
   * - CD
     - ATBD v11
     - family C; unit equivalence
     - Compound index; the precipitation is restricted to wet days (RR >= 1 mm).
   * - CW
     - ATBD v11
     - family C; unit equivalence
     - Compound index; the precipitation is restricted to wet days (RR >= 1 mm).
   * - WD
     - ATBD v11
     - family C; unit equivalence
     - Compound index; the precipitation is restricted to wet days (RR >= 1 mm).
   * - WW
     - ATBD v11
     - family C; unit equivalence
     - Compound index; the precipitation is restricted to wet days (RR >= 1 mm).
   * - FXx
     - ATBD v11
     - family D
     -
   * - FG6Bft
     - ATBD v11
     - family D
     -
   * - FGcalm
     - ATBD v11
     - family D
     -
   * - FG
     - ATBD v11
     - family D
     -
   * - DDnorth
     - ATBD v11
     - family D
     -
   * - DDeast
     - ATBD v11
     - family D
     -
   * - DDsouth
     - ATBD v11
     - family D
     -
   * - DDwest
     - ATBD v11
     - family D
     -
   * - GSL
     - ATBD v11
     - family A; unit equivalence
     - Calendars standard, noleap, 360_day and all_leap; data in degC and K.
   * - SPI6
     - ATBD v11
     - family A; unit equivalence
     - Agrees within 0.30 with a direct scipy gamma fit (see the limits).
   * - SPI3
     - ATBD v11
     - family A; unit equivalence
     - Agrees within 0.30 with a direct scipy gamma fit (see the limits).
   * - PP
     - ATBD v11
     - family D
     -
   * - SS
     - ATBD v11
     - family D
     -
   * - RH
     - ATBD v11
     - family D
     -
   * - HI
     - ATBD v11; Huglin (1978)
     - dedicated tests (HI); unit equivalence
     - Daylength coefficient K by latitude band; no value above 50 N; the daily terms are not clipped at 0.
   * - BEDD
     - ATBD v11
     - dedicated tests (BEDD); unit equivalence
     - Each daily term is limited to the range 0 to 9 degree_Celsius.

Adding the validation of a new index
====================================

1. Write the definition as a function of plain numpy or pandas, from the text of
   the source (the ATBD, the RClimDex manual or the catalogue of DRIAS), day by day
   and without any call to icclim or xclim. Keep the source and the page of the
   definition in the docstring.
2. Build a small dataset that can be checked by hand, with a known expected value, and
   add the edge cases that apply: missing values, a season or a run that crosses the
   end of a year, the units of the input, a non-standard calendar.
3. Compare the result of icclim with the reference calculation in memory and with
   Dask chunks (1 and 7 days), the chunked run being given in other units.
4. If a difference with the definition is found, do not hide it: mark the test as a
   strict expected failure with the number of the issue, so that the test fails when
   the difference is fixed and the mark can be removed.
5. The new index is included in the unit-equivalence test as soon as it is in a
   registry. Check that it passes, and that its output units are equivalent for each
   input unit.
6. Add a row to the table of this page and describe the choices of the definition in
   the documentation of the index. The steps of the registration are in
   :doc:`../dev/add_climate_index`.
