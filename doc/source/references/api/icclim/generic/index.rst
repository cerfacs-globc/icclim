.. _generic api:

:py:mod:`icclim.generic`
========================

.. py:module:: icclim.generic

.. autoapi-nested-parse::

   Generic indices.

   The generic indices public API, via `icclim.generic` package, is generated from the
   `icclim.generic.registry.GenericIndicatorRegistry` registry definitions.
   icclim's generic indices are a generalization of the climate indices found in
   ECAD and DCSC's registries.
   They can be computed on any dataset and make use of the `Threshold` interface
   to enable the creation of personalized indices.
   The parameters of the functions are specialized to each index but are all taken from
   `icclim.main.index` general function.
   In other words, the generic indices in `icclim.generic` package are specializations
   of `icclim.main.index` for ECAD indices.

   .. rubric:: Examples

   >>> from icclim.generic import count_occurrences
   >>> from icclim import build_threshold
   >>> thresh = build_threshold(">= 25 °C and <= 30 °C")
   >>> result = count_occurrences("tas.nc", thresh).compute()
   >>> print(result.count_occurrences)



Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   registry/index.rst


Package Contents
----------------

.. automodule:: icclim._generated._generic
   :members:

   .. autosummary::
    :nosignatures:

    .. Documentation below is auto-generated with the extract-icclim-funs.py script
    .. Generated API comment:Begin

    count_occurrences
    max_consecutive_occurrence
    sum_of_spell_lengths
    excess
    deficit
    fraction_of_total
    maximum
    minimum
    average
    sum
    standard_deviation
    max_of_rolling_sum
    min_of_rolling_sum
    max_of_rolling_average
    min_of_rolling_average
    mean_of_difference
    difference_of_extremes
    mean_of_absolute_one_time_step_difference
    difference_of_means
    percentile
    custom_index

.. Generated API comment:End
