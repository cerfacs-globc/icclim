:py:mod:`icclim._core.legacy.user_index.parse`
==============================================

.. py:module:: icclim._core.legacy.user_index.parse

.. autoapi-nested-parse::

   Contain the parsing operations to create a user indices.



Module Contents
---------------

.. py:function:: read_indicator(user_index: icclim._core.legacy.user_index.model.UserIndexDict) -> icclim._core.generic.indicator.GenericIndicator

   Read the user index and return the corresponding generic indicator.

   :param user_index: The user index dictionary containing the calculation operation and extreme mode.
   :type user_index: UserIndexDict

   :returns: The corresponding generic indicator based on the user index.
   :rtype: GenericIndicator

   :raises InvalidIcclimArgumentError: If the user index does not contain a calculation operation.
       If the user index's calculation operation is unknown.
   :raises NotImplementedError: If the calculation operation or extreme mode is not implemented.

   .. rubric:: Notes

   This function reads the user index dictionary and maps the calculation operation and
   extreme mode to the corresponding generic indicator.
   It raises errors if the required information is missing or if the operation is not
   implemented.


.. py:function:: read_logical_link(user_index: icclim._core.legacy.user_index.model.UserIndexDict) -> icclim._core.model.logical_link.LogicalLink

   Read the logical link from the user index dictionary.

   :param user_index: The user index dictionary containing the logical link information.
   :type user_index: UserIndexDict

   :returns: The corresponding LogicalLink based on the logical link information in the user
             index dictionary.
   :rtype: LogicalLink

   .. rubric:: Notes

   If the logical link is not specified in the user index dictionary, the default
   logical link is LogicalLinkRegistry.LOGICAL_AND.


.. py:function:: read_coef(user_index: icclim._core.legacy.user_index.model.UserIndexDict) -> float | None

   Read the coefficient value from the user index dictionary.

   :param user_index: The user index dictionary containing the coefficient value.
   :type user_index: UserIndexDict

   :returns: The coefficient value if it exists in the user index dictionary, otherwise None.
   :rtype: float or None


.. py:function:: read_date_event(user_index: icclim._core.legacy.user_index.model.UserIndexDict) -> bool

   Read the 'date_event' key from the given UserIndexDict.

   :param user_index: The dictionary containing user index information.
   :type user_index: UserIndexDict

   :returns: The value associated with the 'date_event' key in the UserIndexDict,
             if missing returns False.
   :rtype: bool


.. py:function:: read_thresholds(user_index: icclim._core.legacy.user_index.model.UserIndexDict, doy_window_width: int, reference_period: collections.abc.Sequence[datetime.datetime | str] | None, only_leap_years: bool, interpolation: icclim._core.model.quantile_interpolation.QuantileInterpolation) -> icclim._core.model.threshold.Threshold | None | list[icclim._core.model.threshold.Threshold]

   Read the thresholds from the user index dictionary.

   :param user_index: The user index dictionary containing the threshold information.
   :type user_index: UserIndexDict
   :param doy_window_width: The width of the day of year window for calculating the threshold.
   :type doy_window_width: int
   :param reference_period: The reference period for calculating the threshold.
   :type reference_period: Sequence[dt.datetime | str] | None
   :param only_leap_years: Whether to consider only leap years when calculating the threshold.
   :type only_leap_years: bool
   :param interpolation: The interpolation method to use for calculating the threshold.
   :type interpolation: QuantileInterpolation

   :returns: The corresponding Threshold object(s) based on the threshold information in the
             user index dictionary.
   :rtype: Threshold or None or list[Threshold]

   .. rubric:: Notes

   This function reads the threshold information from the user index dictionary and
   maps it to the corresponding Threshold object(s).
   If the threshold is already a Threshold object, it is returned as is.
   If the threshold is a tuple or list, multiple Threshold objects are created based
   on the logical operation and link specified in the user index dictionary.
   If the threshold is a single value, a single Threshold object is created.
