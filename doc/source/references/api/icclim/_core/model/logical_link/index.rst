:py:mod:`icclim._core.model.logical_link`
=========================================

.. py:module:: icclim._core.model.logical_link

.. autoapi-nested-parse::

   Contain the LogicalLink class and registry.



Module Contents
---------------

.. py:class:: LogicalLink


   Logical link class to combine multiple threshold.

   This is meant to be used with the old user_indices API.
   It is now reccomended to use BoundedThreshold with generic indices instead.
   See :ref:`generic_indices_recipes` for how to combine thresholds with generic
   indices.


.. py:class:: LogicalLinkRegistry




   Registry for LogicalLink objects.
