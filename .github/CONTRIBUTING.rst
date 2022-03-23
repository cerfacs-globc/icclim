Welcome to icclim contribution guide
------------------------------------

This document aim to guide you on how to contribute to icclim.
Everyone is welcomed and contribution are appreciated!

Contents:
    #. :ref:`Getting started`
    #. :ref:`Documentation contribution`
    #. :ref:`Add new standard indices`
    #. :ref:`Add new operators for user indices`
    #. :ref:`Improve icclim API`


Getting started
---------------

Let's first see how to get icclim up and running.
icclim sources are stored in `github <https://github.com/cerfacs-globc/icclim>`_.
To contribute to icclim you will need to clone this repository using git.
Assuming you have configured a ssh key to your github account, you can clone icclim with:
``git clone git@github.com:cerfacs-globc/icclim.git``.
Alternatively you can clone without a ssh key using ``git clone https://github.com/cerfacs-globc/icclim.git``.
With HTTPS, you will have to authenticate using your github account.

Afterward, you must install the python environment to build icclim code and documentation.
We provide a conda environment file and a pip requirement file to install the necessary libraries.
With conda, run ``conda env create -f environment.yml`` from sources' root.
With pip, run ``pip install -r requirement_dev.txt`` from sources' root.

You will also need to fork icclim in github.
See `this tutorial <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_.
To add a fork to your local git config you can run the following ``git remote add my_fork git@github.com:<your github id here>/icclim.git``

Your are set for contributions!

You can now:

    - Create a git branch with ``git checkout -b my_amazing_feature``.
    - Edit the necessary files.
    - Commit them with, for example ``git commit -am "DOC: Add simple tutorial"``.
    - Push your changes to your forked remote ``git push -u my_fork HEAD``.
    - Create a pull request from your fork to icclim main repository. The PR should target ``master`` branch.

Documentation contribution
--------------------------

One of the most important aspect of any open source project is its documentation.
It's both the entry point for most new users and the gallery of the project.
icclim documentation is still in writing, you can help us improve it.

icclim documentation try to follow the `dia-axis principles <https://diataxis.fr/how-to-use-diataxis/>`_.
This divide the documentation into 5 sections:

#. Tutorials. These should introduce the basic functionalities of icclim.
#. "How To..." recipes. They should explain how to work around specific issues.
#. References. Targeting experienced users, they should explain in details the API and internal mechanisms of icclim.
#. Explanation. Topic oriented pages, they can be used explain topics related to icclim and discussions on why and how icclim exists.
#. Development. Not part of the original dia-axis principles. This contains documents used only by icclim dev team such as the release process, how the CI work...

More practically, icclim's documentation is located in the sources under `/doc/source` directory.
Documents are written in `.rst format <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_.

To contribute to icclim documentation you can either improve existing documents or choose one of the category listed above and create
the content you think is missing.
We would especially appreciate contribution to "how to..." and "tutorials" if you have tried icclim in real world scenarios.

To build the documentation, from source root:
#. ``cd doc``
#. ``make html``

Alternatively, you can use `sphinx-autobuild <https://pypi.org/project/sphinx-autobuild/>`_ to detect changes and build the doc automatically.
First install it with pip. Then, in a separate terminal, cd into doc directory and run `sphinx-autobuild source _build`
By default it will serve the documentation on ``localhost://8000``.


Add new standard indices
------------------------

Existing index in xclim
~~~~~~~~~~~~~~~~~~~~~~~

If you would like to use a specific climate index which is not yet available in icclim there are two possibilities.
Either this index exist in `xclim <https://xclim.readthedocs.io/en/stable/indicators.html>`_  and you only need to create
the binding between icclim and xclim.
Or it does not exist in xclim. In that case refer to `Missing standard index in xclim`_ below.

In case xclim has the index, in order to bind icclim to it, there are two files to modify:

- ``ecad_functions.py``
    Create the binding function named with the index short name, full lowercase (e.g tg90p).
    Your function should take one parameter ``config`` typed by ``IndexConfig`` and return a ``xarray.DataArray``.
    Fill your function with your pre-processing and a call to xclim index function (usually located in xclim.atmos module).

- ``models/ecad_indices.py``
    Create a new value for the EcadIndex enum. You must fill it with :

    #. Index short_name, case sensitive (it is used in the output netCDF).
    #. Ihe ``ecad_functions.py`` function to call.
    #. Index group.
    #. List of standard variables needed to compute this index.
    #. Qualifier, used to extract individual function into Copernicus CDS. If you have any issue with this one we can help.

That's it! Your index can now be called from ``icclim.index`` using its short_name.

.. note::

    If the index is not part of ECA&D specification you should create an issue on icclim's github.
    We will then study what would be the best approach to include your index in icclim.

Once the binding is done, don't forget to add unit tests and to update the documentation.
For the unit tests you can add them in ``tests/unit_tests/test_ecad_indices.py``.
For the documentation:

    #. Add a line in the indices' table of ``doc/explanation/climate_indices.rst``.
    #. Add a binding to the function in ``doc/references/ecad_functions_api.rst``.
    #. Add the index in the proper group in table of ``doc/references/icclim_index_api.rst``.


Missing standard index in xclim
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your index might not exist in xclim indicators.
For now, the icclim dev team prefers to group all standard index implementations in xclim.

Thus, you will need to implement the index function in their repository first.
To do so, we recommend you to read their contribution guide and open an issue on
`xclim github <https://github.com/Ouranosinc/xclim>`_, xclim has a very welcoming community.

Once the index is implemented in xclim and they did a new release, xclim version must be updated in icclim.
This should not be an issue as icclim try to always enforce the latest xclim version.
Then you have to bind the new index into icclim.
This process is described in section `Existing index in xclim`_ above.


Add new operators for user indices
----------------------------------

icclim provides a convenient way to quickly write simple index, we call this features "user indices".
A few operators are already available but if you think icclim could benefit from adding new ones, your contribution is most welcomed.
First you need to open an issue on icclim's github to describe what kind of operator you would like to add.

Then, you will need to edit ``icclim/user_indices`` package.

In ``icclim/user_indices/operators.py`` you add the logic of your new operator.
The new operator must be interoperable with the other user_index parameters.
For example, user_index allows a threshold filtering which should be available for most operators.

In ``icclim/user_indices/dispatcher.py`` you must:

    - Create a binding function taking a ``UserIndexConfig`` parameter and calling your operator
    - Add a new value to CalcOperation enum with
        - The operator name
        - A reference to the binding function in ``dispatcher.py``

That's it! Your operator can be called with ``icclim.index``'s ``user_index`` parameter!

Once the binding is done, don't forget to add unit tests and to update the documentation.
For the unit tests, you can add them in ``tests/unit_tests/test_user_indices.py``.
For the documentation, you should add an explanation of the operator behavior in section ``user_index`` of ``doc/references/icclim_index_api.rst``.

Improve icclim API
------------------

icclim features pre-processing and post-processing steps over the index computation:
This includes:

- Input time selection.
- Reference period selection.
- Output time resampling.
- Leap day filtering.
- Metadata updates.
- ...

If you think icclim would benefit from another pre/post-processing step, we would greatly appreciate your contribution.

First, you should create an issue on icclim's github, explaining what kind of step you want to include.
Then it depends a lot on what kind of processing step you wish to include.

The pre-processing steps are separated in ``icclim/main.py`` module and in ``IndexConfig``'s constructor.

For post-processing steps:

    - At DataArray level, the changes should be done either in ``icclim/ecad_functions.py`` module or directly in xclim.
    - At Dataset level, you should probably edit ``icclim/main.py`` module.


Other contributions
-------------------

If you would like to see any other change in icclim not listed here, you can always open an issue on
`icclim's github <https://github.com/cerfacs-globc/icclim>`_ and we will work with you on how to implement it.
