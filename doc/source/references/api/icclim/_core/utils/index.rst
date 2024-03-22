:py:mod:`icclim._core.utils`
============================

.. py:module:: icclim._core.utils

.. autoapi-nested-parse::

   Contain utility functions for icclim.



Module Contents
---------------

.. py:function:: read_date(in_date: str | datetime.datetime) -> datetime.datetime

   Read a date from a string or return the date if it is already a datetime object.

   :param in_date: A string representing a date or a datetime object.
   :type in_date: str | datetime

   :returns: A datetime object.
   :rtype: datetime


.. py:function:: is_number_sequence(values: object) -> bool

   Return True if values is a sequence of numbers.
