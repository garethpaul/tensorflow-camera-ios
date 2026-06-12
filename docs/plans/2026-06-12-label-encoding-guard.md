# Label Encoding Guard

## Status: Completed

## Context

Prediction labels were converted from `std::string` with a deprecated unchecked
C-string initializer. Invalid UTF-8 can make Objective-C string creation return
`nil`, after which using that value as an `NSMutableDictionary` key raises an
exception on the camera callback path.

## Objectives

- Convert model labels with an explicit UTF-8 contract.
- Skip invalid labels before Objective-C collection insertion.
- Log rejected labels without exposing camera content.
- Preserve prediction thresholds and valid-label rendering.

## Work Completed

- Replaced the legacy C-string initializer with `stringWithUTF8String`.
- Guarded failed conversion before creating prediction dictionary entries.
- Logged a bounded diagnostic and continued with remaining predictions.
- Extended static behavior checks and maintenance documentation.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- `make -f /path/to/tensorflow-camera-ios/Makefile check` from an external cwd
- `git diff --check`
