# Camera Frame Safety

## Problem

The camera controller used assertions for missing camera inputs, null pixel
buffers, unsupported pixel formats, and channel-count assumptions. It also
locked pixel buffers without an explicit unlock after inference. Those paths can
turn simulator/no-camera runs or format changes into crash-only failures.

## TDD Evidence

1. Extended `scripts/check-ios-camera-source.py --mode behavior` to reject the
   assert-only camera and frame preprocessing paths.
2. Added setup guards for missing capture devices, failed device inputs, and
   rejected session inputs with user-visible error messages.
3. Added frame guards for null pixel buffers, unsupported formats, pixel-buffer
   lock failures, null base addresses, and explicit unlocks after processing.

## Verification

- `make lint`
- `make test`
- `make verify`
- `git diff --check`

`make build` attempts the iOS simulator target when `xcodebuild` is installed;
otherwise it reports that static project checks completed.
