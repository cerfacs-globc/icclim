:py:mod:`icclim.ecad.registry`
==============================

.. py:module:: icclim.ecad.registry

.. autoapi-nested-parse::

   Module for the ECA&D indices.



Module Contents
---------------

.. py:class:: EcadIndexRegistry




   Registry for ECAD indices.

   This class represents a registry for ECAD indices. It provides a collection of
   standard indices used for climate analysis.

   .. py:method:: get_item_aliases(item: icclim._core.model.standard_index.StandardIndex) -> list[str]
      :staticmethod:

      Get the aliases of an item.


   .. py:method:: to_list() -> list[str]
      :classmethod:

      Get a printable list of all indices in the registry.
