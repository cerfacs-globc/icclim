Continuous integration
======================

icclim continuous integration (CI) aims to assist development by:
    - Avoiding introducing bugs in the code base.
    - Ensuring all new code follow the same code style.
    - Measuring how much icclim code base is tested by automated unit tests. This is known as code coverage.
    - Making sure the documentation generation is functioning well.

These goals are reached using multiple tools:
    - pre-commit CI enforce the code style (Black + flake8 + isort) is followed by
      committing changes directly on new pull request and blocking merge if necessary.
      The relevant file is `.pre-commit-config.yaml`.
    - readthedocs, which serve our documentation is also configured to run the documentation generation on each new pull request.
    - github actions are used to run unit tests and report the results in each pull request.
