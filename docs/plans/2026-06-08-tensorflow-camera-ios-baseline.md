# TensorFlow Camera iOS Baseline

## Status: Completed

## Context

`tensorflow-camera-ios` is a historical Objective-C++ camera sample that runs a
TensorFlow model on live camera frames. The maintenance baseline should preserve
the camera inference path while keeping permission metadata, KVO teardown, and
frame preprocessing crash paths checked statically.

## Objectives

- Preserve the camera-frame inference flow and bundled model/label assets.
- Keep camera permission metadata visible in the iOS project.
- Validate KVO setup/teardown for the still-image output.
- Guard capture setup and pixel-buffer preprocessing against crash-only paths.
- Maintain completed maintenance plans under `docs/plans`.

## Work Completed

- Confirmed `make check` runs project checks, behavior checks, and optional
  Xcode build execution.
- Added canonical `docs/plans` coverage for the current camera lifecycle
  baseline.
- Extended project checks to require completed `docs/plans` entries with
  `make check` verification.
- Updated README, VISION, and CHANGES to make the baseline discoverable.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Run the iOS target on macOS with Xcode and camera-capable hardware.
- Document exact TensorFlow/Bazel/toolchain versions and model provenance.
