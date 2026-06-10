# Capture Teardown Order

## Status: Completed

## Context

The preview layer retained the capture session after setup released its own
reference. Teardown released that layer but left the `session` ivar pointing at
the deallocated object, so the freeze/resume nil guard could later pass on a
stale pointer. The video delegate also remained attached while its serial queue
was released.

## Work Completed

- Stopped an active capture session before dismantling its outputs.
- Detached the video sample-buffer delegate before releasing the output and
  dispatch queue in both teardown and partial setup failure.
- Cleared the borrowed session ivar after releasing the preview layer that
  owned it.
- Added static verification for both cleanup paths and the required teardown
  ordering.

## Verification

- `make check`
- Negative teardown-order and stale-session source mutations
- `git diff --check`

The vendored legacy TensorFlow/iOS toolchain is not available in hosted CI, so
the repository continues to use its SDK-free source and resource contract gate.
