# Camera KVO Gate

## Problem

The repository had no local verification command. The camera setup observed the
`capturingStillImage` KVO key path, but teardown attempted to remove
`isCapturingStillImage`, which can crash during observer cleanup.

## TDD Evidence

1. Added `scripts/check-ios-camera-source.py` and Makefile targets.
2. Ran `make test` before implementation changes and confirmed it failed on the
   KVO key-path mismatch.
3. Updated teardown to remove the observed key path, added release guards, and
   reran the full verification gate.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `git diff --check`
