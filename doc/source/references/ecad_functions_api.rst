
Basic functions for computing indices
=====================================
The `icclim.models.ecad_indices.py <https://github.com/cerfacs-globc/icclim/blob/master/icclim/models/ecad_indices.py>`_
module contains the enumeration of all ECA&D indices icclim can compute.

The corresponding functions are in
`icclim.ecad_functions.py <https://github.com/cerfacs-globc/icclim/blob/master/icclim/ecad_functions.py>`_ module.

Each instance of EcadIndex has a `compute` method to compute the corresponding climate index.
`compute` uses `IndexConfig` to parameterize the index.

.. automodule:: icclim.models.ecad_indices
    :members: EcadIndex

.. autoclass:: icclim.models.index_config.IndexConfig

.. autoclass:: icclim.models.index_config.CfVariable
