:py:mod:`icclim._core.model.operator`
=====================================

.. py:module:: icclim._core.model.operator

.. autoapi-nested-parse::

   Module for the Operator class and OperatorRegistry.



Module Contents
---------------

.. py:class:: Operator


   Represents an operator used in computations.

   :param short_name: The short name of the operator,
                      used when templating the output metadata.
   :type short_name: str
   :param long_name: The long name of the operator,
                     used when templating the output metadata.
   :type long_name: str
   :param standard_name: The standard name of the operator,
                         used when templating the output metadata.
   :type standard_name: str
   :param operand: The operand symbol of the operator.
   :type operand: str
   :param compute: The computation function of the operator.
   :type compute: Callable[[DataArray, DataArray | int | float], DataArray]
   :param aliases: The list of aliases for the operator.
   :type aliases: list[str]


.. py:class:: OperatorRegistry




   Registry of operators.

   Contains the predefined operators used to build ``Threshold``.

   .. py:method:: get_item_aliases(op: Operator) -> list[str]
      :staticmethod:

      Get the aliases of an operator.

      :param op: The operator.
      :type op: Operator

      :returns: The list of aliases for the operator.
      :rtype: list[str]
