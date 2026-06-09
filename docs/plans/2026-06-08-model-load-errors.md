# Model Load Errors

## Status: Completed

## Context

The camera sample loaded its TensorFlow graph and label file during
`viewDidLoad`. If either resource failed to load from the app bundle, the
controller logged with `LOG(FATAL)`, turning missing or corrupt model assets
into a launch crash.

## Objectives

- Preserve local camera inference when model and label assets are present.
- Replace fatal model and label load failures with user-visible errors.
- Avoid starting capture setup when required model assets are unavailable.
- Extend static behavior checks to preserve the non-fatal load path.

## Work Completed

- Changed model load failure logging from `LOG(FATAL)` to `LOG(ERROR)`.
- Changed label load failure logging from `LOG(FATAL)` to `LOG(ERROR)`.
- Showed explicit model/label availability alerts before returning.
- Extended `scripts/check-ios-camera-source.py` to reject fatal model/label
  load paths and require the user-visible errors.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `python3 scripts/check-ios-camera-source.py --mode project`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add a no-camera simulator path for exercising load-failure UI when Xcode is
  available.
- Document model asset provenance and checksums before replacing bundled model
  files.
