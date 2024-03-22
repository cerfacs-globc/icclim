:py:mod:`icclim._core.model.indicator`
======================================

.. py:module:: icclim._core.model.indicator

.. autoapi-nested-parse::

   Typing for generic indices.



Module Contents
---------------

.. py:class:: MissingMethodLike




   Workaround xclim missing type.

   .. py:method:: execute(*args, **kwargs) -> xclim.core.missing.MissingBase
      :abstractmethod:

      Execute the missing method.


   .. py:method:: validate(*args, **kwargs) -> bool
      :abstractmethod:

      Validate the missing method.



.. py:class:: Indicator




   Generic indicator abstract class.

   .. attribute:: name

      The name of the indicator.

      :type: str

   .. attribute:: standard_name

      The standard name of the indicator, ideally from the CF conventions.

      :type: str

   .. attribute:: long_name

      The long name of the indicator.

      :type: str

   .. attribute:: cell_methods

      The cell methods of the indicator.

      :type: str

   .. attribute:: qualifiers

      The qualifiers of the indicator, used to classify indicators.

      :type: tuple

   .. attribute:: templated_properties

      The properties that can be templated.
      Theses properties are used to fill the output metadata.

      :type: tuple

   .. py:method:: preprocess(*args, **kwargs) -> list[xarray.DataArray]
      :abstractmethod:

      Preprocess the data.


   .. py:method:: postprocess(*args, **kwargs) -> xarray.DataArray
      :abstractmethod:

      Postprocess the data.


   .. py:method:: clone() -> Indicator

      Clone the indicator.
