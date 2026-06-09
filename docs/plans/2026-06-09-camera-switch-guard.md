# Camera Switch Guard

## Status: Completed

## Context

The camera controller's front/back switch path assumed the preview session was
available, ignored replacement input creation errors, and toggled
`isUsingFrontFacingCamera` even if no replacement input was installed. On
devices or simulators without the requested camera, that could leave the sample
in a misleading state or with a partially reconfigured capture session.

## Objectives

- Preserve successful front/back camera switching.
- Fail closed when the preview session or requested camera input is unavailable.
- Keep the previous capture inputs when a replacement input cannot be added.
- Extend static behavior checks so the guarded switch path does not regress.

## Work Completed

- Added an active capture-session guard before switching cameras.
- Checked replacement `AVCaptureDeviceInput` creation errors.
- Reconfigured the session through a local `captureSession` reference.
- Preserved old inputs and restored them if the replacement input is rejected.
- Moved `isUsingFrontFacingCamera` toggling behind a successful switch.
- Extended `scripts/check-ios-camera-source.py` to reject unguarded camera
  switching paths.
- Documented the camera switch guard in README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `python3 scripts/check-ios-camera-source.py --mode project`
- `make check`
- `make verify`
- `git diff --check`

## Xcode Notes

XcodeBuildMCP tools and `xcodebuild` were not available in this environment, so
simulator build verification was not run here. The repository `make check`
wrapper still runs `xcodebuild` when that tool is available locally.
