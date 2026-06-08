# Model Output Bounds

## Status: Completed

## Context

The camera inference path assumed TensorFlow returned at least one output tensor
and then indexed labels with `index % predictions.size()`. If model output was
empty, or if the label file was missing or shorter than the prediction vector,
the sample could read outside the available output/label data.

## Objectives

- Preserve local camera-frame inference behavior.
- Guard empty TensorFlow output vectors before reading the first tensor.
- Guard missing labels before rendering predictions.
- Iterate only across the shared bounds of predictions and labels.

## Work Completed

- Replaced direct `outputs[0]` access with an empty-output guard and
  `outputs.front()`.
- Added an empty-label guard before prediction rendering.
- Bounded the prediction loop by the smaller of prediction and label counts.
- Extended `scripts/check-ios-camera-source.py` to preserve these bounds.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add a no-camera test path for model output handling when Xcode is available.
- Document model and label asset provenance in more detail before changing
  bundled model files.
