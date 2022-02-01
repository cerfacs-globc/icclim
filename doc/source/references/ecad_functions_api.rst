ECA&D functions to compute indices
==================================

The `icclim.models.ecad_indices.py <https://github.com/cerfacs-globc/icclim/blob/master/icclim/models/ecad_indices.py>`_
module contains the enumeration of all ECA&D indices icclim can compute.

The corresponding functions are in
`icclim.ecad_functions.py <https://github.com/cerfacs-globc/icclim/blob/master/icclim/ecad_functions.py>`_ module.

Each index of the EcadIndex enum exposes a `compute` method to calculate the corresponding climate index.
`compute` uses `IndexConfig` to parameterize the index.

.. autoclass:: icclim.models.index_config.IndexConfig

.. autoclass:: icclim.models.index_config.CfVariable


Indices functions
-----------------
Below is the documentation of each individual index function.


.. automodule:: icclim.models.ecad_indices
    :members: EcadIndex,
        gd4,
        cfd,
        fd,
        hd17,
        id,
        csdi,
        tg10p,
        tn10p,
        tx10p,
        txn,
        tnn,
        cdd,
        su,
        tr,
        wsdi,
        tg90p,
        tn90p,
        tx90p,
        txx,
        tnx,
        csu,
        prcptot,
        rr1,
        sdii,
        cwd,
        r10mm,
        r20mm,
        rx1day,
        rx5day,
        r75p,
        r75ptot,
        r95p,
        r95ptot,
        r99p,
        r99ptot,
        sd,
        sd1,
        sd5cm,
        sd50cm,
        tg,
        tn,
        tx,
        dtr,
        etr,
        vdtr,
        cd,
        cw,
        wd,
        ww,
