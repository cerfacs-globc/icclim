.. _completeness_policies:

###############################
 Configure period completeness
###############################

icclim checks whether an output period contains enough valid source observations
before publishing an index value. From icclim 7.3, the default is the ECA&D
index-calculation rule from section 5.1 of the `ECA&D Algorithm Theoretical Basis
Document <https://knmi-ecad-assets-prd.s3.amazonaws.com/documents/atbd.pdf#page=21>`_.
The requested output frequency selects the threshold automatically:

.. warning::

   Workflows created before 7.2 can produce new ``NaN`` values after upgrading,
   because those releases generally calculated incomplete periods from the
   observations available. To preserve that historical behavior, add
   ``completeness="none"`` explicitly. Read `Upgrading workflows created before
   7.2`_ before comparing results across versions.

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

   # Apply WMO rules selected from the index aggregation.
   wmo = icclim.index(..., completeness="wmo")

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

WMO rules depend on the aggregation
====================================

The `WMO Guidelines on the Calculation of Climate Normals
<https://library.wmo.int/idurl/4/55797>`_
define different missing-data rules for monthly means and counts, sums,
extremes, and the multi-year values used in a climate normal. Consequently,
``completeness="wmo"`` selects the rule from the index aggregation:

.. list-table:: WMO daily-to-monthly completeness rules
   :header-rows: 1

   * - Aggregation
     - Rule
   * - Mean or threshold count
     - Mask a month with at least 11 missing days or at least 5 consecutive
       missing days. A longer output period is masked if one of its constituent
       months is masked.
   * - Sum
     - Require complete daily data.
   * - Simple maximum or minimum
     - Calculate from available daily data; an all-missing period remains
       missing naturally.
   * - Derived or custom operation
     - Use strict completeness unless its ``GenericIndicator`` declares a WMO
       aggregation class.

These rules require daily input and standard calendar output periods. Other
input frequencies and spatially varying per-cell seasons use strict
completeness. The output attribute ``completeness_aggregation`` records which
class was selected.

The WMO 80% criterion is different: it concerns the availability of valid
monthly values across the years used to calculate a climate normal. It is not a
generic daily completeness percentage and is therefore not silently applied to
ordinary index calculations. Use a numeric ``completeness`` value only when a
minimum valid fraction is the intended index-level rule.

Upgrading workflows created before 7.2
======================================

Before icclim 7.2, an incomplete month, season, or year was generally calculated
from whatever observations were available. Starting with 7.2, icclim began
masking incomplete periods; 7.3 makes the default scientifically explicit by
using ECA&D thresholds. Existing scripts still run, but results can contain
``NaN`` where older releases returned a value.

Choose the migration that matches the workflow rather than the dataset:

.. list-table:: Migration choices
   :header-rows: 1

   * - Intended behavior
     - Script update
   * - Adopt ECA&D index completeness (recommended default)
     - No change, or set ``completeness="ecad"`` explicitly for provenance.
   * - Preserve the pre-7.2 calculate-from-available behavior exactly
     - Set ``completeness="none"`` explicitly.
   * - Preserve 7.2 strict behavior
     - Replace ``allow_missing_periods=False`` with
       ``completeness="strict"`` when convenient.
   * - Use WMO aggregation-specific rules
     - Set ``completeness="wmo"``.
   * - Require a project-specific valid fraction
     - Set a numeric value such as ``completeness=0.8`` and document the
       project standard that motivates it.

Do not add a flag selected from the contents of each dataset. The policy is a
scientific-method choice and should stay stable across comparable runs. During
migration, compare the number and location of masked output periods and inspect
the ``completeness_*`` attributes before accepting changed statistics.

Output provenance
=================

Every result variable records the resolved policy, execution method, options,
period class, aggregation class, and—when applicable—the source reference and
policy version. A numeric rule also records the requested minimum valid
fraction. These attributes make the completeness decision inspectable in NetCDF
outputs and provenance sidecars without forcing Dask-backed arrays to compute
early.
