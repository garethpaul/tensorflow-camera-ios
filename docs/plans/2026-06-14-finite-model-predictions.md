# Finite Model Predictions

## Status: Completed

## Context

Model output values are copied into Objective-C number collections whenever
they exceed the display threshold. Positive infinity passes that comparison,
and non-finite values can then reach smoothing, sorting, and presentation
state.

## Priority

Untrusted or malformed inference output should not enter UI state. Prediction
validation belongs at the C++ to Objective-C collection boundary.

## Requirements

- Reject NaN and positive or negative infinity before `NSNumber` creation.
- Log skipped non-finite output without terminating capture or inference.
- Preserve the existing 0.05 display threshold and every finite prediction.
- Keep label bounds, UTF-8 conversion, frame preprocessing, callback, and
  teardown behavior unchanged.
- Add fail-closed static contracts, focused finite/non-finite fixtures, and
  maintained documentation.

## Verification

- Focused project and camera behavior contracts passed with the finite guard,
  diagnostic, threshold, and validation-before-collection ordering intact.
- The repository and external-directory `make check` passed in an isolated
  Git-backed copy, including all 16 workflow mutations; Linux reported the
  documented static-only boundary because `xcodebuild` is unavailable.
- Seven hostile finite-prediction mutations were rejected: include,
  finite-check, ordering, diagnostic, threshold, documentation, and
  plan-status regressions.
- Generated-artifact, credential-pattern, protected-path, and exact-diff audits
  passed before commit while preserving the pre-existing ignored workflow
  bytecode unchanged.

## Scope Boundary

This change does not clamp or renormalize model output, alter TensorFlow graph
execution, change ranking behavior for finite values, or claim native device
execution in the Linux environment.
