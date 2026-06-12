# Capture Callback Drain

## Status: Completed

## Context

Camera teardown stops the session and detaches the video sample delegate before
releasing the serial callback queue. Delegate detachment prevents new callbacks,
but work already submitted to the queue can still be running while controller-
owned TensorFlow and Objective-C state is released during deallocation.

## Priority

Drain in-flight camera work before releasing callback resources. This is the
highest-value portable lifecycle improvement because it closes a use-after-free
boundary without requiring the unavailable generated TensorFlow archives or an
Xcode host.

## Requirements

- R1. Assign stable queue-specific identity when the serial video callback queue
  is created.
- R2. After detaching the sample delegate, synchronously drain already-enqueued
  callbacks before releasing the output or queue.
- R3. Skip synchronous draining when teardown is already executing on the video
  queue, preventing self-deadlock.
- R4. Preserve capture stop, delegate detach, output release, queue release,
  preview release, and borrowed session clearing order.
- R5. Add static contracts, hostile mutations, maintenance documentation, and
  full `make check` verification.

## Scope Boundaries

- Do not change model inference, frame preprocessing, prediction thresholds,
  camera switching, visual output, or resource digests.
- Do not claim an iOS build or device run from this Linux environment.
- Do not add dependencies or alter the deployment target.

## Implementation Units

### Deadlock-safe callback drain

**Files:** `app/CameraExampleViewController.mm`

- Mark the serial callback queue with a private queue-specific key.
- Add a helper that drains pending callbacks only when invoked off that queue.
- Invoke it after delegate detachment and before callback resource release.

### Contracts and maintenance record

**Files:** `scripts/check-ios-camera-source.py`, `README.md`, `SECURITY.md`,
`VISION.md`, `CHANGES.md`, `docs/plans/2026-06-12-capture-callback-drain.md`

- Enforce queue identity, deadlock avoidance, and teardown ordering.

## Verification Plan

- `python3 -B scripts/check-ios-camera-source.py --mode project`
- `python3 -B scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- external-directory `make check`
- focused callback-drain mutations
- `git diff --check`

## Verification Record

- Project and behavior modes passed with queue identity, deadlock avoidance,
  callback draining, and teardown-order contracts enabled.
- Five focused mutations were rejected: missing identity registration, inverted
  same-queue comparison, missing synchronization, missing teardown invocation,
  and output release before drain.
- Python syntax compilation and `git diff --check` passed; the generated
  bytecode artifact was removed before staging.
- `make check` passed project, 16 workflow-mutation, camera behavior, and build
  fallback checks; `xcodebuild` was unavailable and no iOS build was claimed.
- External-directory `make -f /absolute/path/Makefile check` passed, confirming
  the new source and plan contracts remain caller-directory independent.

## Remaining Risks

- Static contracts cannot exercise AVFoundation scheduling or prove behavior on
  a physical camera.
- Full application linking still requires generated TensorFlow/protobuf archives
  and Xcode on macOS.
