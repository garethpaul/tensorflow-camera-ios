# Frame Preprocessing Stride Guard

## Status: Completed

## Context

The camera resize loop mapped output `y` into the source `x` coordinate and
output `x` into the source `y` coordinate before feeding pixels to TensorFlow.
It also stepped source rows with `image_width * image_channels` instead of the
`CVPixelBuffer` row byte stride, which can differ when Core Video pads rows.

## Objectives

- Preserve source `x`/`y` mapping during frame resizing.
- Use `CVPixelBufferGetBytesPerRow()` when walking source rows.
- Add static behavior checks that catch swapped coordinates or row-stride
  regressions without requiring Xcode on the verification machine.

## Work Completed

- Updated `runCNNOnFrame:` to derive `in_x` from output `x` and `in_y` from
  output `y`.
- Changed source pixel addressing to use `sourceRowBytes` for row offsets.
- Extended `scripts/check-ios-camera-source.py` with frame preprocessing
  coordinate and row-stride checks.
- Updated README, VISION, and CHANGES with the new guardrail.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make lint`
- `make test`
- `make build`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add a small image-preprocessing fixture when this Objective-C++ sample has a
  modern build target available.
- Document the expected camera pixel formats and orientation assumptions next
  to the model input dimensions.
