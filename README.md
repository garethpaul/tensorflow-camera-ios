# tensorflow-camera-ios

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Device Preview

<!-- DEVICE-PREVIEW-IMAGE -->
![Device preview](docs/device-preview.svg)

## Overview

`garethpaul/tensorflow-camera-ios` is an Apple platform application or Swift sample. A tensorflow camera for iOS.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: C++ (142), C/C++ headers (107), Objective-C (1), Objective-C++ (1).

## Repository Contents

- `README.md` - project overview and local usage notes
- `BUILD` - legacy TensorFlow/Bazel build metadata
- `CHANGES.md` - maintenance history for camera lifecycle checks
- `Makefile` - local verification entry points
- `.github/workflows/check.yml` - GitHub Actions baseline for `make check`
- `app` - source or example code
- `docs/plans` - completed maintenance plans for the current baseline
- `plans` - historical implementation notes
- `scripts` - static iOS project and camera behavior validators
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: app
- Dependency and build manifests: none detected
- Entry points or build surfaces: none detected
- Test-looking files: app/common_runtime/constant_folding_test.cc, app/common_runtime/device_set_test.cc, app/common_runtime/direct_session_test.cc, app/common_runtime/direct_session_with_tracking_alloc_test.cc, app/common_runtime/function_test.cc, app/common_runtime/gpu/gpu_allocator_retry_test.cc, app/common_runtime/gpu/gpu_bfc_allocator_test.cc, app/common_runtime/gpu/gpu_debug_allocator_test.cc, and 4 more

## Getting Started

### Prerequisites

- Git
- macOS with Xcode for building Apple platform projects
- Python 3 for repository source checks

### Setup

```bash
git clone https://github.com/garethpaul/tensorflow-camera-ios.git
cd tensorflow-camera-ios
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Open `app/tensorflow_camera.xcodeproj` in Xcode and run the
  `CameraExample` target on an iOS device or simulator with camera support.
- Before attempting a full link, follow the
  [toolchain and model asset guide](docs/toolchain-and-model-assets.md). It
  records the Xcode 8.2-era/iOS 9.2 project metadata, the reviewed TensorFlow
  v0.12.0 reconstruction baseline, required generated archives, model recovery
  checksums, per-file licensing/provenance, and the legacy search paths that
  must be rebound locally. `app/data/PROVENANCE.md` separates the Apache-2.0
  model bundle from the public-domain U.S. Navy sample portrait.

## Testing and Verification

- `make check` runs static project checks and camera lifecycle source checks.
  These checks cover camera permission metadata, KVO teardown, capture setup
  crash paths, guarded camera switching, pixel-buffer lock/unlock handling, and
  model output/label bounds. They also require still-image and video-data
  output setup failures to fail closed before capture starts, and freeze/resume
  actions to fail closed when capture setup is unavailable. Capture runs only
  while the controller is visible, the application is active, and the user has
  requested live capture; lifecycle suspension preserves Freeze/Continue
  intent. Model work already queued on the serial callback path rechecks those
  same gates on the main thread, so stale queued predictions cannot update a
  frozen, hidden, or inactive interface.
  Capture teardown checks require the session to stop, the sample delegate to
  detach, and already-enqueued callbacks to drain before queue release, then
  release the owned session. Queue identity avoids a synchronous
  self-deadlock if cleanup is already executing on the callback queue.
  Frame preprocessing checks center-crop portrait and landscape frames, convert
  supported ARGB/BGRA bytes to TensorFlow RGB order, and preserve
  `CVPixelBuffer` row-stride addressing while rejecting planar, zero,
  oversized, undersized-stride, truncated, or overflow-prone layouts before
  inference. Host-native C++ tests and hostile mutations exercise channel,
  crop, byte-bound, and arithmetic invariants. The checks guard
  missing model or label assets from becoming fatal launch crashes, including the shared
  bundle-resource lookup used by plain and memory-mapped model loading. Label
  loading also fails early when the labels file cannot be opened and skips empty
  label lines before prediction rendering. Prediction rendering also skips and
  logs labels that cannot be converted from UTF-8 instead of inserting a nil
  dictionary key. Finite model predictions are required before scores enter
  Objective-C collections, smoothing, sorting, or display state. Model prediction
  range validation also rejects finite values outside the inclusive `[0, 1]`
  softmax probability range before UI publication. Model output dtype validation
  rejects non-float tensors before typed prediction access. The portable test
  target compiles and executes this probability boundary with a local C++11
  compiler. A second no-camera C++ boundary maps scores to labels, preserves
  the shorter output/label count, applies the strict display threshold, and
  fails closed for non-finite thresholds and malformed scores. The checks also preserve
  manual cleanup of controller-owned prediction and speech state and verify
  SHA-256 digests for the graph, labels, sample image, and reviewed upstream
  credential fixture used by vendored TensorFlow OAuth tests. Repository scans
  reject private-key markers at every other path.
  When
  `xcodebuild` is installed, the `build` target also attempts an iOS simulator
  build with code signing disabled and keeps all products in a temporary
  directory outside the case-sensitive `app/BUILD` source path.
- Static project checks also require completed canonical plans under `docs/plans`.
- `make root-test` exercises repository-root, shell, Make metadata, trusted
  Python/C++/Xcode tool values, and non-executing modes without Xcode.
- GitHub Actions runs the same `make check` baseline on fixed Ubuntu 24.04 for
  pushes and pull requests without requiring Xcode. The workflow has read-only
  repository permissions, credential-free checkout, concurrency cancellation,
  a five-minute timeout, and commit-pinned Node 24 actions. Dependency-free
  mutation tests reject duplicate, relocated, or contradictory credential
  settings and other workflow policy regressions.
- Full Xcode linking still requires regenerated TensorFlow/protobuf static
  archives and replacement of developer-local search paths in the legacy
  project; those generated dependencies are not checked into this repository.
- Xcode's test action or `xcodebuild test` with the appropriate scheme and
  destination can be used on macOS for deeper verification.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- The reviewed upstream credential fixture under
  `app/platform/cloud/testdata/` is public TensorFlow testdata with fake service
  account identifiers and an exact pinned digest. It is not application
  configuration and is the only allowed key-shaped fixture; keep all real
  secrets and any additional credential fixtures out of git. Its introduction,
  TensorFlow v0.12.0 snapshot, reviewed commit, and current dual-path upstream
  comparison are recorded in `app/platform/cloud/testdata/PROVENANCE.md`.

## Security and Privacy Notes

- Review changes touching authentication or token handling; examples from the scan include app/CameraExampleViewController.h, app/CameraExampleViewController.mm, app/common_runtime/constant_folding.cc, app/common_runtime/costmodel_manager.h, and 6 more.
- Review changes touching network requests, sockets, or service endpoints; examples from the scan include app/CameraExampleAppDelegate.h, app/CameraExampleAppDelegate.m, app/CameraExampleViewController.h, app/CameraExampleViewController.mm, and 6 more.
- Review changes touching mobile permissions or privacy-sensitive device data; examples from the scan include app/CameraExampleAppDelegate.h, app/CameraExampleAppDelegate.m, app/CameraExampleViewController.h, app/CameraExampleViewController.mm, and 6 more.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include app/Info.plist, app/common_runtime/gpu/gpu_device.cc, app/common_runtime/step_stats_collector.cc, app/common_runtime/sycl/sycl_device.cc, and 6 more.
- Review changes touching shell execution, subprocess, or dynamic evaluation; examples from the scan include app/debug/debug_grpc_io_utils_test.cc, app/distributed_runtime/rpc/grpc_testlib.cc, app/distributed_runtime/rpc/grpc_testlib.h.
- Review changes touching database, model, or persistence code; examples from the scan include app/CameraExampleViewController.mm, app/common_runtime/costmodel_manager.cc, app/common_runtime/device.h, app/common_runtime/device_set.h, and 6 more.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-tensorflow-camera-ios-baseline.md` for the
  canonical camera lifecycle baseline.
- See `docs/plans/2026-06-08-model-output-bounds.md` for the model output and
  label bounds guard.
- See `docs/plans/2026-06-08-model-load-errors.md` for the missing model/label
  asset error guard.
- See `docs/plans/2026-06-09-nonfatal-resource-lookup.md` for the shared
  bundle-resource lookup guard.
- See `docs/plans/2026-06-09-label-load-guard.md` for the label file open and
  empty-label guard.
- See `docs/plans/2026-06-09-frame-preprocessing-stride.md` for the camera
  frame coordinate and row-stride guard.
- See `docs/plans/2026-06-09-camera-switch-guard.md` for the front/back camera
  switch guard.
- See `docs/plans/2026-06-09-camera-controller-retained-state.md` for the
  retained controller state cleanup guard.
- See `docs/plans/2026-06-09-camera-output-guard.md` for the still/video output
  setup guard.
- See `docs/plans/2026-06-09-take-picture-session-guard.md` for the
  freeze/resume missing-session guard.
- See `docs/plans/2026-06-10-ci-baseline.md` for the portable GitHub Actions
  contract gate.
- See `docs/plans/2026-06-10-model-resource-integrity.md` for model, label, and
  sample-image integrity verification.
- See `docs/plans/2026-06-10-capture-teardown-order.md` for ordered capture
  callback shutdown and session pointer cleanup.
- See `docs/plans/2026-06-12-capture-callback-drain.md` for deadlock-safe
  draining of already-enqueued camera callbacks during teardown.
- See `docs/plans/2026-06-13-sampling-coordinate-arithmetic.md` for overflow-safe
  frame sampling coordinate arithmetic.
- See `docs/plans/2026-06-14-make-root-override-protection.md` for authoritative
  repository-root selection across all Make aliases.
- See `docs/plans/2026-06-21-make-authority-isolation.md` for quoted checkout
  paths, fixed shell authority, Make mode rejection, and startup boundaries.
- See `docs/plans/2026-06-14-finite-model-predictions.md` for inference-output
  validation before prediction UI state.
- See `docs/plans/2026-06-26-prediction-output-native-contract.md` for the
  no-camera score-to-label selection boundary.
- See `docs/plans/2026-06-14-model-output-dtype-validation.md` for guarded
  TensorFlow prediction tensor access.
- See `docs/plans/2026-06-15-upstream-credential-fixture-provenance.md` for the
  reviewed TensorFlow OAuth test fixture path, digest, fake identity, and
  repository-wide private-key marker policy.
- See `docs/plans/2026-06-17-model-prediction-range-validation.md` for executable
  softmax probability boundary validation before prediction UI state.
- See `docs/plans/2026-06-19-frame-preprocessing-native-contract.md` for the
  host-native RGB, crop, byte-bound, arithmetic, and ownership contract.
- See `docs/plans/2026-06-25-active-screen-camera-lifecycle.md` for the
  active-screen capture gate and preserved Freeze/Continue intent.
- See `docs/plans/2026-06-26-stale-prediction-publication.md` for the
  main-thread stale queued predictions publication guard.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
