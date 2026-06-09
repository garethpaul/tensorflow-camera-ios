# Nonfatal Resource Lookup

## Status: Completed

## Context

The camera controller now handles failed TensorFlow model and label loading with
user-visible alerts, but the shared bundle-resource helper still logged missing
resources with `LOG(FATAL)`. That meant a missing bundled model, label file, or
memory-mapped model package could terminate the app before the caller returned
an error status.

## Objectives

- Keep missing bundle resources on the non-fatal load-error path.
- Guard the memory-mapped model loader before dereferencing a missing resource
  path.
- Extend static behavior checks to preserve the shared resource lookup contract.

## Work Completed

- Changed `FilePathForResourceName` from fatal logging to non-fatal error
  logging.
- Added a missing-path guard in `LoadMemoryMappedModel`.
- Extended `scripts/check-ios-camera-source.py` to reject fatal logging in the
  TensorFlow utility resource path and require the memory-mapped guard.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `python3 scripts/check-ios-camera-source.py --mode project`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add a no-camera simulator path that exercises model and label load failures
  when Xcode tooling is available.
- Document checksums and provenance for the bundled TensorFlow graph and label
  file.
