# Frame preprocessing native contract

## Status: Completed

## Problem

The camera requests BGRA frames but copied the first three bytes directly into
the TensorFlow input, publishing BGR instead of RGB. The legacy ARGB fallback
also included alpha. Landscape frames were stretched rather than center-cropped,
and pointer arithmetic did not validate the Core Video backing byte count.

## Invariant

- Only non-planar ARGB and BGRA buffers are accepted.
- Every accepted frame has a non-zero square center crop whose final byte is
  inside `CVPixelBufferGetDataSize`.
- Resize products, row offsets, column offsets, and additions fail closed on
  `size_t` overflow.
- TensorFlow receives RGB channel order for both supported Core Video layouts.
- Capture-session and TensorFlow-session ownership remains explicit and
  transactional on setup failures.
- Native build products use a temporary directory so case-insensitive macOS
  filesystems cannot replace the tracked `app/BUILD` source file.

## Proof

`tests/frame_preprocessing_test.cc` executes crop, stride, channel, truncation,
and overflow cases as C++11 on the host. `scripts/test_frame_preprocessing_mutations.py`
requires hostile channel, crop, byte-bound, and arithmetic changes to fail.
Static project checks require the Objective-C++ controller and model loader to
use the reviewed helpers and ownership order.

The focused native and mutation tests pass. The canonical `make check` gate is
the required combined verification before the branch is pushed. The portable
combined gate passed; Xcode reached Objective-C++ compilation from an isolated
temporary build directory and stopped at the documented missing generated
`tensorflow/core/public/session.h` dependency.

## Residual risk

The host checks do not compile the Objective-C++ target, execute the bundled
TensorFlow graph, or exercise an actual `CVPixelBuffer`. A regenerated legacy
TensorFlow/protobuf archive set and a compatible Xcode/device environment are
still required for native camera and model-runtime validation.
