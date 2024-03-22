:orphan:

:py:mod:`icclim.logger`
=======================

.. py:module:: icclim.logger


Module Contents
---------------

.. py:class:: VerbosityRegistry




   Registry classes acts as fancy enums.

   It allows to easily store and find constants of similar type.
   Registries are namespaces, so there is no need to instantiate it or any of
   its subclasses, every item is a class attribute.

   .. rubric:: Notes

   Registries are not meant to store large collections, they are just fancy lookup
   tables for items with aliases and no case sensitivity.

   .. py:method:: get_item_aliases(item: Verbosity) -> list[str]
      :staticmethod:

      Get the aliases for the given item.

      :param item: The item to get aliases for.
      :type item: T

      :returns: A list of aliases for the item.
      :rtype: list[str]

      .. rubric:: Notes

      Should be overridden in subclasses.



.. py:class:: IcclimLogger(verbosity: Verbosity)


   Singleton to display and control logs in icclim library.
