# Active-Screen Camera Lifecycle

## Status: Completed

## Problem

`setupAVCapture` started the capture session during `viewDidLoad`, and the
controller did not stop it when its view disappeared or the application
resigned active. Using the session's current running state as the Freeze button
state also meant that lifecycle-driven suspension could silently change user
intent.

## Decision

Keep user intent separate from runtime availability. The capture session runs
only when all three conditions are true:

- the user requested live capture;
- the camera controller is visible; and
- the application is active.

View and application lifecycle events reconcile the session without changing
the user's Freeze/Continue choice. The controller removes its application
notification observers before capture teardown.

## Work Completed

- Added explicit capture-request, view-visibility, and application-activity
  state to `CameraExampleViewController`.
- Replaced eager setup and direct Freeze/Continue session control with one
  running-state reconciliation method.
- Suspended capture when the controller disappears or the application resigns
  active, and resumed only when user intent still requests capture.
- Added static behavior contracts for state ownership, lifecycle ordering,
  observer cleanup, and setup/freeze regressions.
- Updated the repository maintenance, security, vision, and contributor notes.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `python3 scripts/check-ios-camera-source.py --mode project`
- `make check`
- `git diff --check`
- Hostile lifecycle mutations were rejected for eager setup starts, missing
  state gates, session-derived Freeze intent, and missing observer cleanup.

The SDK-free checks do not claim an iOS build or device camera runtime test. A
camera-capable Apple device remains the final integration environment for
AVCapture lifecycle behavior.
