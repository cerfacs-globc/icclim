:py:mod:`icclim._core.model.registry`
=====================================

.. py:module:: icclim._core.model.registry

.. autoapi-nested-parse::

   Contain the Registry class, a fancy enum replacement.



Module Contents
---------------

.. py:class:: Registry




   Registry classes acts as fancy enums.

   It allows to easily store and find constants of similar type.
   Registries are namespaces, so there is no need to instantiate it or any of
   its subclasses, every item is a class attribute.

   .. rubric:: Notes

   Registries are not meant to store large collections, they are just fancy lookup
   tables for items with aliases and no case sensitivity.

   .. py:method:: lookup(query: T | str) -> T
      :classmethod:

      Look up an item in the registry.

      :param query: The item to look up. It can be either an instance of the item class or a
                    string.
      :type query: T or str

      :returns: The found item.
      :rtype: T

      :raises InvalidIcclimArgumentError: If the item is not found in the registry.

      .. rubric:: Notes

      This method performs a case-insensitive lookup.
      It first checks if the query is an instance of the item class, and if so,
      returns a deep copy of the query.


   .. py:method:: lookup_no_error(query: T | str) -> T | None
      :classmethod:

      Also look up an item in the registry, but return None if not found.

      :param query: The item to look up. It can be either an instance of the item class or a
                    string.
      :type query: T or str

      :returns: The found item, or None if not found.
      :rtype: T or None


   .. py:method:: every_aliases() -> list[T]
      :classmethod:

      Return a list of all aliases for items in the registry.

      :returns: A list of all aliases for items in the registry.
      :rtype: list[T]


   .. py:method:: get_item_aliases(item: T) -> list[str]
      :staticmethod:

      Get the aliases for the given item.

      :param item: The item to get aliases for.
      :type item: T

      :returns: A list of aliases for the item.
      :rtype: list[str]

      .. rubric:: Notes

      Should be overridden in subclasses.


   .. py:method:: catalog() -> dict[str, T]
      :classmethod:

      Return a dictionary of all items in the registry.

      :returns: A dictionary containing all items in the registry, where the keys are the
                item names and the values are the item instances.
      :rtype: dict[str, T]


   .. py:method:: values() -> list[T]
      :classmethod:

      Return a list of all items in the registry.

      :returns: A list containing all items in the registry.
      :rtype: list[T]
