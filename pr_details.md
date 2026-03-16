PR Title: Integrate external notebooks and add CI synchronization

### Pull Request to resolve #354

# Integrated C3S climate index notebooks and automated synchronization

This PR integrates 6 notebooks from the C3S Copernicus Training repository and adds a synchronization mechanism.

## Proposed Changes

### Notebook Integration
Integrated the following C3S notebooks into the tutorials:
- cold_spell_duration
- diurnal_temperature_range
- heavy_precipitation
- summer_days
- tn90p
- warm_wet_days

All notebooks were updated to be compatible with icclim 7.1.0+ and fixed common issues such as header hierarchy, variable naming, and import ordering.

### Documentation
- Updated tutorials index to include the new C3S notebooks.
- Added necessary image assets for the notebooks.
- Updated release notes for version 7.1.0.

### Automated Synchronization
- Added a GitHub Action to synchronize the notebooks to external repositories (GitLab and GitHub) on every push to the master branch.

## Verification
- Documentation build verified for header consistency and toctree inclusion.
- Notebook linting fixed for E402, N816, ERA001, and S605/S602.
- Synchronization workflow tested.
