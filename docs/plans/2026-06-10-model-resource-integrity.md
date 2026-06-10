# Model Resource Integrity

Status: Completed

## Context

The application depends on a 54 MB TensorFlow graph, an ordered ImageNet label
set, and a bundled sample image. Presence checks alone could not detect silent
truncation or replacement. The portable workflow also used a moving runner,
and Make targets assumed the repository was the current directory.

The Xcode project cannot link from a clean checkout because generated
TensorFlow/protobuf archives are absent and legacy search paths point outside
the repository. This gate therefore validates reproducible checked-in inputs
without implying a full application build.

## Changes

- Added streaming SHA-256 checks for the graph, labels, and sample image.
- Fixed CI to Ubuntu 24.04 and added concurrency cancellation.
- Added exact action-version comments while retaining immutable SHA pins.
- Anchored Makefile paths to the repository root.
- Corrected the optional Xcode target from `tensorflow_camera` to
  `CameraExample` for environments that provide the generated dependencies.
- Documented the remaining full-link prerequisites explicitly.

## Verification

- `make check`
- `make -f /path/to/tensorflow-camera-ios/Makefile check` from outside the repository
- negative resource and workflow mutation checks
- `git diff --check`
- GitHub Actions contract job
