:py:mod:`icclim.exception`
==========================

.. py:module:: icclim.exception

.. autoapi-nested-parse::

   Contain icclim-specific exceptions.



Module Contents
---------------

.. py:exception:: InvalidIcclimArgumentError(msg: str, source_err: Exception | None = None)




   Exception raised for erroneous input arguments.

   .. attribute:: msg

      Error description.

      :type: str

   .. attribute:: source_err

      The source of the error, if any.

      :type: Exception or None, optional

   .. method:: __str__()

      Returns a string representation of the error message.
