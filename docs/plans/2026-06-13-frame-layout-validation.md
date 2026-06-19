# Frame Layout Validation

## Status: Completed

## Context

The camera preprocessing path now validates supported BGRA/ARGB formats, checks
pixel-buffer locking, maps output coordinates correctly, and uses Core Video's
row stride. It still casts width, height, and row bytes directly to `int` and
enters the sampling path without rejecting zero dimensions or a row stride too
short to contain `width × 4` bytes. A malformed frame layout can therefore make
pixel addressing invalid even when the format identifier is supported.

## Priority

Reject impossible Core Video layouts before locking or reading frame memory so
the static camera safety boundary covers both pixel format and geometry.

## Requirements

- R1. Read width, height, and row bytes using Core Video's native `size_t`
  values before converting dimensions used by the model loop.
- R2. Reject zero width, zero height, and row strides shorter than four bytes
  per source pixel before locking the pixel buffer.
- R3. Log one diagnostic for invalid frame geometry without exposing frame data
  or crashing capture.
- R4. Preserve ARGB/BGRA handling, center crop, x/y mapping, padded-row access,
  lock/unlock behavior, TensorFlow input shape, prediction thresholds, and
  callback teardown order.
- R5. Avoid integer overflow in the minimum-row-byte comparison.
- R6. Add fail-closed static contracts, hostile mutations, maintenance
  documentation, and full `make check` verification.

## Scope Boundaries

- Do not touch vendored TensorFlow sources, model assets, prediction rendering,
  camera switching, queue draining, project settings, or resource digests.
- Do not add dependencies or alter the deployment target.
- Do not claim Xcode, simulator, device, camera, or TensorFlow runtime behavior
  from the Linux verification host.

## Implementation Units

### Pixel-buffer geometry gate

**Files:** `app/CameraExampleViewController.mm`

- Read native width, height, and row-byte values.
- Compare row bytes against a division-based overflow-safe width bound.
- Return with a diagnostic before buffer locking when geometry is invalid.
- Convert validated dimensions for the existing crop and sampling loop.

### Contracts and maintenance record

**Files:** `scripts/check-ios-camera-source.py`, `README.md`, `SECURITY.md`,
`VISION.md`, `CHANGES.md`, `docs/plans/2026-06-13-frame-layout-validation.md`

- Reject missing zero-dimension, stride, overflow-safe comparison, ordering,
  diagnostic, or regression-plan evidence.

## Verification Plan

- `python3 -B scripts/check-ios-camera-source.py --mode project`
- `python3 -B scripts/check-ios-camera-source.py --mode behavior`
- `python3 -B scripts/test_workflow_contract.py`
- `make check`
- focused frame-layout mutations
- external-working-directory `make check`
- project, workflow, SVG/XML, staged-path, generated-artifact, secret-pattern,
  and `git diff --check` audits

## Assumptions

- Supported capture frames remain four-byte ARGB or BGRA buffers as configured
  by `AVCaptureVideoDataOutput`.
- Static source contracts can prove the guard structure and ordering, but only
  Apple tooling and a runtime camera can validate real `CVPixelBuffer` layouts.

## Work Completed

- Read Core Video row bytes, width, and height as native `size_t` values.
- Rejected zero dimensions, dimensions outside the existing integer model-loop
  range, and row strides too short for four-byte pixels before buffer locking.
- Used division for the minimum-stride comparison so the guard does not
  multiply an untrusted width.
- Preserved supported formats, crop and sampling behavior, lock/unlock paths,
  TensorFlow input and prediction behavior, callback draining, project files,
  assets, and vendored code.
- Extended fail-closed source contracts and maintenance documentation.

## Verification

- Focused behavior contracts and all 16 workflow mutations passed.
- Python source compilation and `git diff --check` passed before the full gate.
- Local `xcodebuild` was unavailable on Linux; no native compile, simulator,
  device, camera, or TensorFlow runtime behavior is claimed.
- `make check` passed project and behavior contracts, all 16 workflow
  mutations, resource-integrity checks, and the truthful no-Xcode build
  fallback.
- The same full gate passed from an external working directory.
- Seven focused hostile mutation categories were rejected: row-stride
  truncation, removed zero-width or zero-height guards, removed integer bounds,
  overflow-prone stride multiplication, validation after locking, and a missing
  diagnostic.
- Plan-aware frame-safety, arithmetic, lifecycle, testing, maintainability, and
  scope review found no remaining actionable issue.
