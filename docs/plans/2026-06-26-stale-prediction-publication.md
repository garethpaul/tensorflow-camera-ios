# Stale Prediction Publication Guard

Status: Completed

## Context

Camera capture already stops when explicit capture intent, controller
visibility, or application activity closes. An inference callback that was
already executing can still finish afterward and enqueue a main-thread update,
allowing stale queued predictions to change a frozen, hidden, or inactive UI.

## Decision

- Define one framework-independent publication decision using the same three
  lifecycle gates as camera running-state ownership.
- Evaluate the decision on the main thread immediately before mutating
  Objective-C prediction state.
- Reject publication when capture is frozen, the controller is hidden, or the
  application is inactive.
- Preserve model inference, score validation, label selection, smoothing,
  speech, camera session ownership, and the user's Freeze/Continue intent.

## Verification

- RED `make test` rejected the missing helper and controller publication guard.
- `Prediction output tests passed` for the fully open gate and all three
  independently closed gates.
- `prediction output mutation tests passed (8 mutations rejected)` including
  capture-intent, visible-view, and active-application gate removal.
- Repository and external-directory `make check` passed all portable gates.
- An isolated mutation removing the Objective-C++ controller publication guard
  was rejected by the behavior checker.
- Gitleaks reported seven reviewed findings confined to the allowed upstream
  credential fixture plus three known generic-key false positives; the
  digest-pinned credential policy passed all seven hostile scenarios.
- `xcodebuild not found; static project checks completed`; no full iOS link,
  simulator, device, camera, or TensorFlow graph runtime claim is made.
- `git diff --check` passed.

## Residual Risk

The host-native decision and source contract prove fail-closed publication at
the main-thread handoff. They do not execute UIKit, AVFoundation, the legacy
TensorFlow graph, or rapid freeze/resume timing on camera hardware.
