:py:mod:`icclim._core.model.global_metadata`
============================================

.. py:module:: icclim._core.model.global_metadata

.. autoapi-nested-parse::

   Global metadata model to be added to the output netCDF file.



Module Contents
---------------

.. py:class:: GlobalMetadata




   Global metadata model.

   .. attribute:: history

      The CF history attribute.

      :type: str or None

   .. attribute:: source

      The source of the data.

      :type: str or None

   .. attribute:: time_encoding

      The time encoding information to be read from ds.time.encoding.

      :type: dict or None
