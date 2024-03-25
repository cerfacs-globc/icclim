:py:mod:`icclim._core.model.cf_calendar`
========================================

.. py:module:: icclim._core.model.cf_calendar

.. autoapi-nested-parse::

   Contain the CfCalendar class and the CfCalendarRegistry class.

   These classes are used to represent and manage the CF calendars used in the
   climate indices calculation.



Module Contents
---------------

.. py:class:: CfCalendar


   Represents a CF calendar.

   :param aliases: All the possible aliases or poorly typed calendar names targeting the same
                   calendar.
   :type aliases: list[str]
   :param is_leap: It expects a DataArray argument of years such as `da.time.dt.year`.
                   Returns a mask of the input telling if the value is part of a leap year or not.
   :type is_leap: Callable

   .. attribute:: aliases

      All the possible aliases or poorly typed calendar names targeting the same
      calendar.

      :type: list[str]

   .. attribute:: is_leap

      It expects a DataArray argument of years such as `da.time.dt.year`.
      Returns a mask of the input telling if the value is part of a leap year or not.

      :type: Callable

   .. py:property:: name
      :type: str

      Returns the name of the calendar.

      :returns: The name of the calendar.
      :rtype: str


.. py:class:: CfCalendarRegistry




   Calendars known in CF plus some additional custom aliases for convenience.

   :param aliases: All the possible aliases or poorly typed calendar names targeting the same
                   calendar.
   :type aliases: list[str]
   :param is_leap: It expects a DataArray argument of years such as `da.time.dt.year`.
                   Returns a mask of the input telling if the value is part of a leap year or not.
   :type is_leap: Callable

   .. attribute:: _item_class

      The class of the items in the registry.

      :type: type

   .. py:method:: get_item_aliases(item: CfCalendar) -> list[str]
      :staticmethod:

      Get the aliases of a CfCalendar item.

      :param item: The CfCalendar item.
      :type item: CfCalendar

      :returns: The aliases of the CfCalendar item.
      :rtype: list[str]



.. py:function:: _proleptic_gregorian_leap(years: xarray.DataArray) -> xarray.DataArray

   Calculate if the years are part of a leap year in the proleptic Gregorian calendar.

   :param years: The years to check.
   :type years: DataArray

   :returns: A boolean array indicating if the years are part of a leap year.
   :rtype: DataArray


.. py:function:: _julian_leap(years: xarray.DataArray) -> xarray.DataArray

   Calculate if the years are part of a leap year in the Julian calendar.

   :param years: The years to check.
   :type years: DataArray

   :returns: A boolean array indicating if the years are part of a leap year.
   :rtype: DataArray


.. py:function:: _standard_leap(years: xarray.DataArray) -> xarray.DataArray

   Calculate if the years are part of a leap year in the standard Gregorian calendar.

   :param years: The years to check.
   :type years: DataArray

   :returns: A boolean array indicating if the years are part of a leap year.
   :rtype: DataArray
