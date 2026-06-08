# Changes

## 2026-06-08

- Added `make check` as the shared repository verification alias.
- Replaced assert-only camera setup failures with user-visible capture setup
  errors for missing devices, failed inputs, and rejected session inputs.
- Guarded frame preprocessing against null pixel buffers, unsupported pixel
  formats, and pixel-buffer lock failures.
- Added pixel-buffer unlock handling and extended the camera lifecycle checker
  to protect these crash-path contracts.
- Added a Makefile verification gate for iOS project and camera lifecycle
  source checks.
- Fixed teardown to remove the same still-image KVO key path that setup
  observes.
- Added nil-reset guards around released capture resources.
- Documented the local static verification workflow.
