### Pull Request to resolve #269
- [x] Unit tests cover the changes. (Visual fix, no logic changes)
- [x] These changes were tested on real data. (Verified by inspecting SVG headers)
- [x] The relevant documentation has been added or updated.
- [x] A short description of the changes has been added to doc/source/references/release_notes.rst.

### Describe the changes you made
The version text (e.g., "7.1.0") in the SVG logos was being cropped because the viewBox width was too narrow (652 units). Since the version text starts at approximately x=519, this left very little room for the version string.

I increased the viewBox width from 652 to 750 units in all 6 primary logo variants (colored, grey, and white; both base and displayed versions). This provides sufficient space on the right side of the logo to accommodate the version text without cropping.
