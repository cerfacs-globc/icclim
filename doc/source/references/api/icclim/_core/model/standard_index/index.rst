:py:mod:`icclim._core.model.standard_index`
===========================================

.. py:module:: icclim._core.model.standard_index

.. autoapi-nested-parse::

   Contain the StandardIndex data class.



Module Contents
---------------

.. py:class:: StandardIndex


   Standard Index data class.

   It is used to describe how a GenericIndicator should be setup to compute a climate
   index that has been defined in the literature (such as ECA&D's ATBD document).


   .. attribute:: short_name

      The index name used in the output.

      :type: str

   .. attribute:: compute

      The function to compute the index. It usually wraps a xclim functions.

      :type: Callable

   .. attribute:: group

      The index group category.

      :type: IndexGroup

   .. attribute:: variables

      The Cf variables needed to compute the index.
      The variable are individually described by a list of aliases.

      :type: List[List[str]]

   .. attribute:: qualifiers

      ``optional`` List of configuration to compute the index.
      Used internally to generate modules for C3S.

      :type: List[str] | None

   .. attribute:: source

      Where the index definition comes from.

      :type: str | None

   .. attribute:: definition

      A formal definition of the index. It should describe what kind of output
      the user is expected to obtain.

      :type: str | None

   .. py:method:: clone() -> StandardIndex

      Return a deep copy of the index.
