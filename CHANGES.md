# Changes

## 2026-06-26 00:15 PDT - P2 - Add no-camera label output verification

### Summary

Extracted model-score-to-label selection into a host-native C++11 boundary so
preprocessing and label output can be verified without TensorFlow archives,
UIKit, a simulator, or camera hardware.

### Work completed

- Added deterministic labeled-prediction selection bounded by available labels.
- Preserved finite/unit-range validation, the strict display threshold, model
  order, Objective-C UTF-8 conversion, and existing rejection logs.
- Added executable selector tests and five compile-and-run hostile mutations.
- Integrated the new runner into `make test` and the Make-root authority fixture.
- Added completed plan, maintainer guidance, and fail-closed source/test checks.
- Advanced the roadmap to downloaded model asset licensing and provenance.

### Threads

- None; camera controller, existing native seams, tests, plans, and roadmap were
  reviewed directly.

### Files changed

- `app/prediction_output.h` — framework-independent score-to-label selection.
- `app/CameraExampleViewController.mm` — shared selector integration.
- `tests/prediction_output_test.cc` — no-camera behavior coverage.
- `scripts/run-prediction-output-tests.sh` — isolated C++11 runner.
- `scripts/test_prediction_output_mutations.py` — five hostile mutations.
- `Makefile`, `scripts/test-makefile-root.sh`, and
  `scripts/check-ios-camera-source.py` — full gate integration and contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, `AGENTS.md`, and
  `docs/plans/2026-06-26-prediction-output-native-contract.md` — guidance and evidence.
- `CHANGES.md` — this cycle record.

### Validation

- RED native runner — failed because `prediction_output.h` was absent.
- `make test` — passed preprocessing, prediction range, prediction output, and
  eleven combined native hostile mutations.
- Initial `make check` — failed because Make-root isolation did not stub the new
  shell runner; the fixture was corrected.
- Final `make check` — passed project/behavior checks, 35 Make authority cases,
  17 workflow mutations, five credential scenarios, all native C++ tests, and
  eleven native mutations.
- Xcode build — skipped explicitly because `xcodebuild` is unavailable.
- `git diff --check` — passed.

### Bugs / findings

- P2 coverage: label-bound and threshold behavior was executable only inside
  the legacy Objective-C++ camera path.
- P2 test integration: adding a shell runner requires the Make-root fixture to
  stub it or every isolated `check`/`verify` case fails.

### Blockers

- Historical Xcode and generated TensorFlow/protobuf archives remain
  unavailable; no full iOS link or camera runtime claim is made.

### Next action

- Clarify licensing and provenance for downloaded model assets.

## 2026-06-25 23:36 PDT - P2 - Document legacy toolchain reconstruction

### Summary

Documented the evidence-backed TensorFlow/iOS reconstruction baseline and
byte-pinned model recovery path without claiming an unknown original commit.

### Work completed

- Recorded TensorFlow `0.12.head`, Xcode 8.2-era, iOS 9.2, GNU++11, libc++, and
  generated-archive expectations from checked-in metadata.
- Verified the graph, labels, and license against official `inception5h.zip`
  bytes and the sample image against the official v0.12.0 iOS camera example.
- Documented the v0.12.0 `build_all_ios.sh` reconstruction path and required
  local search-path rebinding.
- Corrected the README's Xcode target from the nonexistent `tensorflow_camera`
  target to `CameraExample`.
- Extended resource integrity to the bundled license, added fail-closed
  documentation contracts, and advanced the roadmap.

### Threads

- None; repository history and official TensorFlow v0.12.0 sources were
  reviewed directly.

### Files changed

- `docs/toolchain-and-model-assets.md` — historical toolchain, archive, model,
  checksum, and validation boundaries.
- `README.md`, `VISION.md` — linked the guide and advanced the next priority.
- `scripts/check-ios-camera-source.py` — guide and license integrity contracts.
- `CHANGES.md` — this cycle record.

### Validation

- Red `make check` — rejected the missing guide and stale roadmap priority.
- Official `inception5h.zip` and v0.12.0 camera image byte comparison — passed.
- Eleven hostile documentation/resource mutations — rejected missing toolchain,
  archive, uncertainty, README, target, roadmap, and license contracts.
- `make check` — passed, including project/behavior contracts, 35 Make
  authority cases, workflow and credential mutations, and native C++ tests.
- `make -f /absolute/path/Makefile check` from outside the repository — passed.
- `git diff --check` — passed.

### Bugs / findings

- P2 developer workflow: the repository named no reproducible TensorFlow tag,
  omitted the generated archive commands, and retained machine-local Xcode
  search paths without a rebinding warning.
- P2 documentation: the README named `tensorflow_camera`, but the project and
  verified build script use the `CameraExample` target.

### Blockers

- Historical Xcode and generated TensorFlow/protobuf archives are unavailable
  locally; no full iOS link or camera runtime claim is made.

### Next action

- Add a no-camera test path for image preprocessing and label output.

## 2026-06-25 07:18:07 PDT

- Limited camera capture to the intersection of explicit user intent, visible
  controller state, and active application state. Leaving the screen or
  resigning active now suspends capture without losing the user's Freeze or
  Continue choice.
- Added lifecycle contract checks that reject eager setup starts, app-state or
  visibility bypasses, session-derived user intent, and observer cleanup
  regressions.

## 2026-06-21

- Isolated verification from caller-selected roots, shells, bypassing Make
  modes, preload metadata, and additional Makefiles while preserving trusted
  Python, C++ compiler, and Xcode executable overrides.

## 2026-06-19

- Corrected ARGB/BGRA camera bytes to TensorFlow RGB order, added symmetric
  center cropping, and rejected truncated or overflow-prone frame layouts.
- Made capture-session ownership explicit and made TensorFlow model loading
  transactional so failed graph creation cannot leak or publish a session.
- Added host-native frame preprocessing tests and hostile mutation coverage.
- Isolated Xcode products from the source tree so the default `app/build`
  directory cannot collide with the tracked `app/BUILD` file on macOS.

## 2026-06-17

- Added executable model prediction range validation so malformed finite
  softmax values cannot reach smoothing or percentage presentation.

## 2026-06-15

- Pinned the reviewed upstream credential fixture by path, digest, and fake
  identity while rejecting private-key markers elsewhere in the repository.

## 2026-06-14

- Added model output dtype validation before TensorFlow float prediction access.
- Required finite model predictions before scores enter Objective-C
  collections, smoothing, sorting, or display state.

## 2026-06-13

- Promoted sampling coordinate arithmetic before multiplication to prevent
  signed overflow in camera frame pointer offsets.
- Rejected zero, oversized, and undersized-stride camera frame layouts before
  locking Core Video memory or entering TensorFlow preprocessing.

## 2026-06-12

- Drained already-enqueued camera callbacks after delegate detachment and before
  resource release, with queue identity preventing synchronous self-deadlock.
- Rejected invalid UTF-8 model labels before Objective-C dictionary insertion,
  replacing deprecated unchecked C-string conversion.

## 2026-06-10

- Stopped capture and detached video callbacks before queue teardown, then
  cleared the borrowed session pointer after releasing its preview-layer owner.
- Added SHA-256 integrity checks for the TensorFlow graph, ImageNet labels, and
  bundled sample image.
- Fixed hosted verification to Ubuntu 24.04 with concurrency cancellation and
  made Make targets independent of the caller's working directory.
- Corrected the optional Xcode build target name while documenting its missing
  generated TensorFlow/protobuf archive prerequisites.
- Added a least-privilege GitHub Actions workflow that runs `make check` for
  the static camera baseline with commit-pinned Node 24 actions and a bounded
  runtime. Checkout credentials are not persisted.
- Added dependency-free structural workflow tests that reject duplicate,
  relocated, or contradictory credentials and other policy regressions.
- Extended project checks to require the CI workflow and completed CI plans.

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
