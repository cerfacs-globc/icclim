PR Title: Integrate external notebooks and add CI synchronization

### Pull Request to resolve #354
- [x] Unit tests cover the changes.
- [x] These changes were tested on real data.
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to doc/source/references/release_notes.rst.

### Describe the changes you made

This PR integrates external notebooks from GitLab (C4I) and GitHub (Copernicus Training) into the icclim repository tutorials. The following major changes were implemented:

1. Notebook Integration and API Update
   - Added 6 new tutorials from C3S/C4I to doc/source/tutorials/notebooks.
   - Updated all notebooks to use the latest icclim.index API, replacing deprecated function calls.
   - Fixed a path handling issue in deltaT_deltaP_anomaly.ipynb where PosixPath objects from glob were being overwritten in loops.
- Fixed comprehensive notebook linting errors (E402, N816, T201, ERA001, S602, S603, S607, F821) across all integrated notebooks. This includes moving imports to the top cell, renaming mixedCase variables, restoring informative prints with noqa suppression, refactoring problematic subprocess/ncatted calls into native Xarray in-memory unit corrections, and localizing/fixing broken NBViewer badge images.

2. Documentation and Versioning
   - Updated doc/source/tutorials/index.rst to include the newly added notebooks in the main tutorials list.
   - Injected an icclim version compatibility note (Compatible with icclim 7.1.0+) into the introductory text of all notebooks.
   - Resolved documentation build errors by normalizing the markdown header hierarchy (H1, H2, H3) and adding missing image assets.
   - Updated the release history (doc/source/references/release_notes.rst) by consolidating all recent changes into the 7.1.0 section.

3. Automated Synchronization
   - Implemented a new GitHub Action (notebook_sync.yml) that automatically synchronizes the tutorials content from the icclim master branch to the external GitLab and GitHub repositories whenever changes are pushed.
   - This ensures that tutorial resources remain consistent across different platforms.

### Verification
- Documentation build verified for header consistency and toctree inclusion.
- Notebook linting verified locally across all 13 integrated and native tutorials.
- Subprocess removal verified in heavy_precipitation and warm_wet_days tutorials.
- NBViewer localized badge image verified.
- Synchronization workflow tested.
