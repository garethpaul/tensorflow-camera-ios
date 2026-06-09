# Camera Output Guard

## Status: Completed

## Context

`setupAVCapture` already handled missing devices and failed camera inputs, but
still-image and video-data outputs were added opportunistically. The video-data
connection was then enabled without checking whether the connection existed,
leaving setup able to proceed with a partially configured capture session.

## Objectives

- Fail closed when the still-image output cannot be added.
- Fail closed when the video-data output cannot be added.
- Guard the video-data connection before enabling it.
- Clean up retained setup state on output setup failures.
- Add static checks so the output setup path stays guarded.

## Work Completed

- Added `failCameraSetupWithMessage:` to centralize output setup cleanup.
- Guarded `canAddOutput:` for still-image and video-data outputs.
- Stored and checked the `AVCaptureConnection` before enabling video frames.
- Extended `scripts/check-ios-camera-source.py` to reject unchecked output and
  connection setup.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- `git diff --check`

`xcodebuild` is not installed in this environment, so `make check` reports that
the Xcode build was not run after static verification passes.

## Follow-Up Candidates

- Add a no-camera test path for image preprocessing and label output.
- Document exact build tool versions and model download expectations.
