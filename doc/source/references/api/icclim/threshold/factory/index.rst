:py:mod:`icclim.threshold.factory`
==================================

.. py:module:: icclim.threshold.factory

.. autoapi-nested-parse::

   Factory to build a `Threshold` from a query or from its components.



Module Contents
---------------

.. py:function:: build_threshold(query: str | None = None, *, operator: icclim._core.model.operator.Operator | str | None = None, value: icclim._core.model.threshold.ThresholdValueType = None, unit: str | None = None, threshold_min_value: str | float | pint.Quantity | None = None, thresholds: collections.abc.Sequence[icclim._core.model.threshold.Threshold | str] | None = None, logical_link: str | icclim._core.model.logical_link.LogicalLink | None = None, offset: str | float | pint.Quantity | None = None, **kwargs) -> icclim._core.generic.threshold.bounded.BoundedThreshold | icclim._core.generic.threshold.percentile.PercentileThreshold | icclim._core.generic.threshold.basic.BasicThreshold

   Build a `Threshold`.

   This function is a factory for `Threshold` instances.
   It can build a `BasicThreshold`, a `PercentileThreshold` or a `BoundedThreshold`.
   See :ref:`generic_indices_recipes` for how to combine thresholds with generic
   indices.

   :param query: string query describing a threshold.
                 It must include: an operator, a threshold value and optionally a unit
                 such as "> 10 degC".
                 It acts as a shorthand for ``operator``, ``value`` and ``unit`` parameters for
                 simple threshold.
                 Don't use ``query`` when value is a DataArray, a Dataset or a path to a
                 netcdf/zarr storage, instead use ``operator``, ``value`` and ``unit``.
                 ``query`` supersede `operator`, `value` and `unit` parameters.
   :type query: str | None = None
   :param operator: keyword argument only.
                    The operator either as an instance of Operator or as a compatible string.
                    See :py:class:`OperatorRegistry` for the list of all operators.
                    When ``query`` is None and operator is None, the default ``Operator.REACH`` is
                    used.
   :type operator: Operator | str = None
   :param value: keyword argument only.
                 The threshold value(s), default to None.
                 It can be:
                 * a simple scalar threshold
                 * a percentile that will be computed per-grid cell (in combinaison with `unit`)
                 * per-grid cell thresholds defined by a DataArray, a Dataset or a string path to
                 a netcdf/zarr.
                 * a sequence of scalars, the indicator will then be computed for each value and
                 a specific dimension will be created (also work with percentiles).
   :type value: str | float | int | Dataset | DataArray | Sequence[float | int | str] | None
   :param unit: Keyword argument only.
                The threshold unit.
                When ``unit`` is None, if ``value`` is a dataset and a "units"
                can be read from its `attrs`, this unit will be used. If value is a scalar or
                a sequence of scalar, the exceedance will be computed by assuming threshold has
                the same unit as the studied value is it compared to.
                When unit is a string it must be a valid unit of our shared pint registry with
                xclim or a special percentile unit:
                * "doy_per" for day of year percentiles (in ECAD, used for temperature indices
                such as TX90p)
                * "period_per" for per period percentiles (in ECAD, used for rain indices such
                as R75p)
   :type unit: str | None = None
   :param threshold_min_value: A minimum value used to pre-filter computed threshold values.
                               This is particularly useful to compute a percentile threshold for rain where
                               dry days are usually ignored. In that case threshold_min_value would be set to
                               "1 mm/day".
                               If threshold_min_value is a number, ``unit`` is used to quantify
                               ``threshold_min_value``.
   :type threshold_min_value: str | float | pint.Quantity
   :param offset: Optional. An offset applied to the threshold. This is particularly useful when
                  the threshold is an existing dataset (netcdf file or zarr store) and the data
                  should be compared to this dataset + an offset
                  (e.g. to compute days when T > 5 degC above normal)
   :type offset: float | None
   :param kwargs: Additional arguments to build a PercentileThreshold.
                  See :py:class:`PercentileThreshold` constructor for the complete list
                  of possible arguments.

   .. rubric:: Examples

   .. code-block:: python

       # -- Scalar threshold
       scalar_t = build_threshold(">= 30 degC")
       assert isinstance(scalar_t, BasicThreshold)

       # -- Daily percentile threshold
       doy_t = build_threshold(">= 30 doy_per")
       assert isinstance(doy_t, PercentileThreshold)

       # -- Per grid-cell threshold, with offset
       grided_t = build_threshold(
           operator=">=", value="path/to/tasmax_thresholds.nc", unit="K", offset=5
       )
       assert isinstance(grided_t, BasicThreshold)

       # -- Daily percentile threshold, from a file
       tasmax = xarray.open_dataset("path/to/tasmax_thresholds.nc").tasmax
       doys = xclim.core.calendar.percentile_doy(tasmax)
       doy_file_t = build_threshold(operator=">=", value=doys)
       assert isinstance(doy_file_t, PercentileThreshold)

       # -- Bounded threshold
       bounded_t = build_threshold(">= -20 degree AND <= 20 degree ")
       # equivalent to:
       x = build_threshold(">= -20 degree")
       y = build_threshold("<= 20 degree")
       bounded_t2 = x & y
       assert bounded_t == bounded_t2
       # equivalent to:
       bounded_t3 = build_threshold(thresholds=[x, y], logical_link="AND")
       assert bounded_t == bounded_t3
       assert isinstance(bounded_t, BoundedThreshold)
