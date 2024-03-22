:py:mod:`icclim._core.model.in_file_dictionary`
===============================================

.. py:module:: icclim._core.model.in_file_dictionary

.. autoapi-nested-parse::

   Contains the InFileDictionary class.



Module Contents
---------------

.. py:class:: InFileDictionary




   Dictionary grouping in_files and var_name functionnalities.

   .. attribute:: study

      Study input file.

      :type: InFileBaseType

   .. attribute:: thresholds

      Thresholds to apply to the study input file.

      :type: NotRequired[Threshold | None]

   .. rubric:: Examples

   .. code-block:: python

       threshold = build_threshold(operator=">", value=["per-1.nc", "per-2.nc"])
       in_files = {
           "tasmax": {
               "study": "tasmax-store.zarr",
               "threshold": threshold,
           },
           "pr": "pr.nc",
           "tasmin": {"study": "tasmin.nc"},
       }

   .. rubric:: Notes

   It also allows to use a different input for thresholds such as percentiles.
