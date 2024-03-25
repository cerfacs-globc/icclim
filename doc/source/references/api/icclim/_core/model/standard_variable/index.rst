:py:mod:`icclim._core.model.standard_variable`
==============================================

.. py:module:: icclim._core.model.standard_variable

.. autoapi-nested-parse::

   Define the StandardVariable class and the StandardVariableRegistry class.

   The StandardVariable class represents a standard variable used in climate data analysis.
   The StandardVariableRegistry class is a registry that stores instances of
   `StandardVariable`.

   StandardVariable are mainly used to compute the metadata of the output of the generic
   indices.



Module Contents
---------------

.. py:class:: StandardVariable




   StandardVariable represents a typical variable used in climate data analysis.

   :param short_name: The short name of the variable.
   :type short_name: str
   :param standard_name: The standard name of the variable.
   :type standard_name: str
   :param long_name: The long name of the variable.
   :type long_name: str
   :param aliases: A list of aliases for the variable.
   :type aliases: list[str]
   :param default_units: The default units of the variable.
   :type default_units: str

   .. py:method:: get_metadata() -> dict[str, str]

      Get the metadata of the StandardVariable object.



.. py:class:: StandardVariableRegistry




   StandardVariableRegistry stores instances of StandardVariable such as PR, TAS.

   .. py:method:: get_item_aliases(item: StandardVariable) -> list[str]
      :staticmethod:

      Return a list of aliases for the given StandardVariable.

      :param item: The StandardVariable object for which to retrieve the aliases.
      :type item: StandardVariable

      :returns: A list of aliases for the given StandardVariable.
      :rtype: list[str]
