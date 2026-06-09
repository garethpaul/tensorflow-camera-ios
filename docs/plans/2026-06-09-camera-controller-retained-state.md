# Camera Controller Retained State

## Status: Completed

## Context

`CameraExampleViewController` uses manual Objective-C memory management. It
retained the speech synthesizer, label-layer collection, and prediction-value
dictionary during `viewDidLoad`, but `dealloc` only released `square`.
`viewDidUnload` also released `oldPredictionValues` without clearing the ivar,
leaving a stale pointer path for later teardown.

## Objectives

- Release retained controller-owned Objective-C objects during `dealloc`.
- Clear `oldPredictionValues` after `viewDidUnload` releases it.
- Preserve existing capture, TensorFlow, and prediction rendering behavior.
- Extend static verification so retained-state cleanup does not regress.

## Work Completed

- Released `synth`, `labelLayers`, and `oldPredictionValues` in `dealloc`.
- Set `oldPredictionValues = nil` after the `viewDidUnload` release.
- Extended `scripts/check-ios-camera-source.py --mode behavior` to require the
  cleanup path.
- Updated README, VISION, and CHANGES.

## Verification

- Negative: `python3 scripts/check-ios-camera-source.py --mode behavior`
  failed before the Objective-C++ fix because retained controller state was not
  fully released and `viewDidUnload` did not clear `oldPredictionValues`.
- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Xcode Notes

`xcodebuild` was not available in this environment, so simulator build
verification was not run here. The repository `make check` wrapper still runs
`xcodebuild` when that tool is available locally.
