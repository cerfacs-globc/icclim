:py:mod:`icclim.ecad.binding`
=============================

.. py:module:: icclim.ecad.binding

.. autoapi-nested-parse::

   Proxy icclim indicators that redirect to xclim indicators.



Module Contents
---------------

.. py:class:: GrowingSeasonLength




   Proxy for xclim.growing_season_length.

   icclim indicator that redirect to xclim `growing_season_length` indicator.

   .. py:method:: preprocess(*args, **kwargs) -> list[xarray.DataArray]
      :abstractmethod:

      Not implemented as xclim indicator already handle pre/post processing.


   .. py:method:: postprocess(*args, **kwargs) -> xarray.DataArray
      :abstractmethod:

      Not implemented as xclim indicator already handle pre/post processing.



.. py:class:: StandardizedPrecipitationIndex3




   Proxy for xclim.atmos.standardized_precipitation_index.

   icclim indicator that redirect to xclim `standardized_precipitation_index`
   indicator, with 3 MS frequency preconfigured.

   .. py:method:: preprocess(*args, **kwargs) -> list[xarray.DataArray]
      :abstractmethod:

      Not implemented as xclim indicator already handle pre/post processing.


   .. py:method:: postprocess(*args, **kwargs) -> xarray.DataArray
      :abstractmethod:

      Not implemented as xclim indicator already handle pre/post processing.



.. py:class:: StandardizedPrecipitationIndex6




   Proxy for xclim.atmos.standardized_precipitation_index.

   icclim indicator that redirect to xclim `standardized_precipitation_index`
   indicator, with 6 MS configured.

   .. py:method:: preprocess(*args, **kwargs) -> list[xarray.DataArray]
      :abstractmethod:

      Not implemented as xclim indicator already handle pre/post processing.


   .. py:method:: postprocess(*args, **kwargs) -> xarray.DataArray
      :abstractmethod:

      Not implemented as xclim indicator already handle pre/post processing.
