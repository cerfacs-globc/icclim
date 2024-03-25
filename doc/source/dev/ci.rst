.. _Continuous integration:

########################
 Continuous integration
########################

icclim continuous integration (CI) aims to assist development by:
   -  Avoiding introducing bugs in the code base.
   -  Ensuring all new code follow the same code style.
   -  Measuring how much icclim code base is tested by automated unit
      tests. This is known as code coverage.
   -  Making sure the documentation generation is functioning well.

These goals are reached using multiple tools:
   -  pre-commit CI enforces the code style rules. It is run on new pull requests
      and may commit automatically to fix the source code.
      If it fails to fix the code base, it woill block the PR from being merged.
      The relevant configuration file is ``.pre-commit-config.yaml``.

   -  readthedocs, it serves our documentation on https://icclim.readthedocs.io/en/stable/.
      It is configured with ``.readthedocs.yml`` and runs the generation of the
      documentation on each new pull request.

   -  github actions are used to run unit tests and report the results
      in each pull request. They are configured in ``../.github/workflows/ci.yml``
