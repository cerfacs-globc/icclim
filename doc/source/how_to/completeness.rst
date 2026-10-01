.. _completeness_policies:

###############################
 Configure period completeness
###############################

icclim checks whether an output period contains enough valid source observations
before publishing an index value. From icclim 7.3, the default is the ECA&D
index-calculation rule from section 5.1 of the `ECA&D Algorithm Theoretical Basis
Document <https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf#page=21>`_.
The requested output frequency selects the threshold automatically:

.. list-table:: ECA&D minimum valid daily values
   :header-rows: 1

   * - Output period
     - Minimum
   * - Year
     - 350 days
   * - Half-year
     - 175 days
   * - Three-month season
     - 85 days
   * - Month
     - 25 days

For regular sub-daily input, icclim converts these day minima to the equivalent
number of source observations. Unsupported output periods, non-regular input
frequencies, and spatially varying per-cell seasons use strict completeness. This
fallback prevents a threshold defined for a standard calendar period from being
silently applied to a scientifically different period.

The default therefore needs no dataset-specific option::

   result = icclim.index(
       in_files="tasmax.nc",
       index_name="SU",
       slice_mode="year",
   )

Explicit policies and custom fractions
======================================

Use ``completeness`` only when the scientific workflow requires a rule other
than the default:

.. code-block:: python

   # Require every expected source observation.
   strict = icclim.index(..., completeness="strict")

   # Require at least 80% of expected observations in every output period.
   eighty_percent = icclim.index(..., completeness=0.8)

   # Deliberately calculate from any available observations.
   unrestricted = icclim.index(..., completeness="none")

A numeric fraction is inclusive: ``0.8`` accepts a period with exactly 80% valid
observations. For spatially varying per-cell seasons it resolves to strict,
because a shared percentage denominator cannot represent the different expected
time mask in every cell. The legacy ``allow_missing_periods`` parameter remains a 7.2
compatibility bridge. When it is explicitly supplied, ``False`` means strict and
``True`` means none; it cannot be combined with ``completeness``.

Why ECA&D and WMO are not one profile
=====================================

The `WMO Guidelines on the Calculation of Climate Normals
<https://www.agroorbi.pt/livroagrometeorologia/DocsProg/Temas%26Exerc%C3%ADciosExtraPorCap%C3%ADtulo/Cap1_Introdu%C3%A7%C3%A3o/Docs/WMO%20Guidelines%20on%20the%20Calculation%20of%20Climate%20Normals_en.pdf>`_
define different missing-data rules for
monthly means and counts, sums, extremes, and the multi-year values used in a
climate normal. In particular, the WMO 80% criterion concerns the availability
of valid monthly values across the years used for a normal; it is not a generic
daily completeness percentage for every climate index.

For this reason, icclim does not label one generic percentage as a ``wmo``
profile. The ECA&D profile directly specifies when annual, half-yearly,
seasonal, and monthly indices can be calculated. A future WMO profile can use
the same policy resolver, but must first classify the aggregation and normal
being calculated so that means, sums, counts, and extremes retain their distinct
rules.

Output provenance
=================

Every result variable records the resolved policy, execution method, options,
period class, and—when applicable—the source reference and policy version. A
numeric rule also records the requested minimum valid fraction. These attributes
make the completeness decision inspectable in NetCDF outputs and provenance
sidecars without forcing Dask-backed arrays to compute early.
