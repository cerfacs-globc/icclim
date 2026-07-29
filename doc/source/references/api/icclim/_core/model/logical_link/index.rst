:py:mod:`icclim._core.model.logical_link`
=========================================

.. py:module:: icclim._core.model.logical_link

.. autoapi-nested-parse::

   Contain the LogicalLink class and registry.



Module Contents
---------------

.. py:class:: LogicalLink


   Logical link class to combine multiple threshold.

   This exists mainly for the deprecated user_index compatibility path.
   New custom-index code should use BoundedThreshold with generic indices instead.
   See :ref:`generic_indices_recipes` for how to combine thresholds with generic
   indices.


.. py:class:: LogicalLinkRegistry




   Registry for LogicalLink objects.
