:py:mod:`icclim.dcsc.registry`
==============================

.. py:module:: icclim.dcsc.registry

.. autoapi-nested-parse::

   Contain the registry of the DCSC (Meteo France) specific indices.



Module Contents
---------------

.. py:class:: DcscIndexRegistry




   Registry of the DCSC (Meteo France) specific indices.

   .. note:: The indices metadata of this module are in French.

   .. py:method:: get_item_aliases(item: icclim._core.model.standard_index.StandardIndex) -> list[str]
      :staticmethod:

      Duck-typed method to get the aliases of a StandardIndex item.

      :param item: The StandardIndex item.
      :type item: StandardIndex

      :returns: The aliases of the item.
      :rtype: list[str]

      .. rubric:: Notes

      Every StandardIndex registry should implement this method.
