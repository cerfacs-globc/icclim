:py:mod:`icclim._core.model.quantile_interpolation`
===================================================

.. py:module:: icclim._core.model.quantile_interpolation

.. autoapi-nested-parse::

   Contain the classes for quantile interpolation.

   QuantileInterpolation class and the QuantileInterpolationRegistry class
   are defined here.



Module Contents
---------------

.. py:class:: QuantileInterpolation


   Class for performing quantile interpolation.

   :param name: The name of the interpolation method.
   :type name: str
   :param alpha: The alpha parameter for the interpolation.
   :type alpha: float
   :param beta: The beta parameter for the interpolation.
   :type beta: float


.. py:class:: QuantileInterpolationRegistry




   Registry of quantile interpolation methods.

   Only 2 methods are available: LINEAR and MEDIAN_UNBIASED.
