# Label Load Guard

## Status: Completed

## Context

`LoadLabels()` already used the shared non-fatal bundle-resource lookup for the
labels file path. Once a path was returned, it opened the file and reported
success even if the stream did not open or only yielded empty lines. That left
the camera controller to discover missing labels later during prediction
rendering.

## Objectives

- Preserve successful label loading for valid bundled label files.
- Fail early when the labels file path cannot be opened.
- Skip empty label lines before storing labels for prediction rendering.
- Add deterministic static coverage for the label loading boundary.

## Work Completed

- Added an `is_open()` guard after opening the labels file.
- Logged failed label file opens and returned a non-OK TensorFlow status.
- Switched label iteration to `std::getline` success checks.
- Skipped empty label lines before appending to the labels vector.
- Extended `scripts/check-ios-camera-source.py --mode behavior` to require the
  label file open and empty-label guards.
- Updated README, VISION, and CHANGES notes for label loading.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make lint`
- `make check`
- `make verify`
- `git diff --check`

`xcodebuild` is not installed in this environment, so `make check` reports that
the Xcode build was not run after static verification passes.
