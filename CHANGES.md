# Changes

## 2026-06-10

- Added SHA-256 integrity checks for the TensorFlow graph, ImageNet labels, and
  bundled sample image.
- Fixed hosted verification to Ubuntu 24.04 with concurrency cancellation and
  made Make targets independent of the caller's working directory.
- Corrected the optional Xcode build target name while documenting its missing
  generated TensorFlow/protobuf archive prerequisites.
- Added a least-privilege GitHub Actions workflow that runs `make check` for
  the static camera baseline with commit-pinned Node 24 actions and a bounded
  runtime.
- Extended project checks to require the CI workflow and completed CI plan.

## 2026-06-09

- Made label loading fail when the labels file cannot be opened and skip empty
  label lines before prediction rendering, with static validation.
- Guarded the freeze/resume camera action when capture setup is unavailable so
  the UI does not toggle state against a missing session.
- Guarded still-image and video-data output setup so missing outputs or video
  connections fail closed before capture starts.
- Released manually retained camera-controller prediction, label, and speech
  state during teardown and guarded the cleanup path statically.
- Guarded front/back camera switching against missing sessions, failed input
  creation, and rejected replacement inputs.
- Corrected frame preprocessing source coordinate mapping and row-stride usage
  before feeding camera pixels into TensorFlow.
- Extended static behavior checks to preserve resize-loop `x`/`y` mapping and
  `CVPixelBuffer` row-byte addressing.
- Replaced fatal bundle-resource lookup logging in TensorFlow utilities with
  non-fatal error logging.
- Added a missing-resource guard for memory-mapped model loading.
- Extended static behavior checks to preserve non-fatal model resource lookup.

## 2026-06-08

- Replaced fatal model and label load failures with user-visible errors and
  static checker coverage.
- Ignored Python bytecode caches produced by local checker syntax validation.
- Guarded TensorFlow output and label indexing before rendering predictions,
  with static checker coverage.
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
- Added canonical `docs/plans` coverage and made project checks require
  completed plans.
