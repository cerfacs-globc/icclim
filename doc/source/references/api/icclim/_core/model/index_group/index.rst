:py:mod:`icclim._core.model.index_group`
========================================

.. py:module:: icclim._core.model.index_group

.. autoapi-nested-parse::

   Contain the IndexGroup class and the IndexGroupRegistry class.



Module Contents
---------------

.. py:class:: IndexGroup(name: str, values: list[IndexGroup] | None = None)


   Class representing a group of climate indices.

   :param name: The name of the index group.
   :type name: str
   :param values: The list of index groups contained within this group. Defaults to None.
   :type values: list[IndexGroup] | None, optional

   .. attribute:: name

      The name of the index group.

      :type: str

   .. attribute:: values

      The list of index groups contained within this group.

      :type: list[IndexGroup]

   .. py:method:: get_indices() -> list[Any]

      Get the list of indices belonging to this group.

      :returns: The list of indices belonging to this group.
      :rtype: list[Any]

      .. rubric:: Notes

      The list of indices is obtained by filtering the EcadIndexRegistry values.
      The others indices are not considered.



.. py:class:: IndexGroupRegistry




   Registry for IndexGroup instances.
