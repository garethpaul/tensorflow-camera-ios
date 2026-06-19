# Sampling Coordinate Arithmetic

## Status: Completed

## Context

The camera path now rejects impossible Core Video dimensions and row strides
before locking frame memory. The resize loop still calculates source
coordinates as `(x * image_width)` and `(y * image_height)` using signed
`int` arithmetic. Dimensions accepted up to `INT_MAX` can overflow those
intermediate products before division and pointer addressing.

## Priority

Keep sampling coordinates within the validated frame layout without signed
overflow, while preserving the existing nearest-neighbor mapping and padded
row-stride access.

## Requirements

- R1. Calculate source x and y coordinates with unsigned size-aware
  intermediates before division.
- R2. Keep the resulting coordinates inside the validated crop dimensions.
- R3. Preserve center crop, ARGB/BGRA channel handling, row-stride addressing,
  TensorFlow input shape, prediction handling, and lock/unlock behavior.
- R4. Add fail-closed contracts, hostile mutations, completed plan evidence,
  maintenance documentation, and full `make check` verification.

## Implementation Units

### Overflow-safe sampling coordinates

**Files:** `app/CameraExampleViewController.mm`

Promote loop coordinates before multiplication and retain size-aware source
indices through pointer offset calculation.

### Contracts and maintenance record

**Files:** `scripts/check-ios-camera-source.py`, `README.md`, `SECURITY.md`,
`VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-13-sampling-coordinate-arithmetic.md`

Reject signed-coordinate multiplication, narrowing source indices, reordered
layout validation, missing documentation, and regressed plan status.

## Verification Plan

- `python3 -B scripts/check-ios-camera-source.py --mode behavior`
- `python3 -B scripts/check-ios-camera-source.py --mode project`
- `python3 -B scripts/test_workflow_contract.py`
- full `make check` locally and from an external working directory
- focused coordinate-arithmetic mutations
- plist, workflow YAML, SVG/XML, Python syntax, artifact, secret-pattern, and
  `git diff --check` audits

## Scope Boundaries

- Do not touch vendored TensorFlow sources, model assets, camera lifecycle,
  prediction UI, project settings, resource digests, or deployment targets.
- Do not change the resize algorithm or claim Xcode, simulator, device, camera,
  or TensorFlow runtime validation from the Linux host.

## Work Completed

- Promoted output x and y loop coordinates before multiplying by validated
  source dimensions.
- Retained `size_t` source indices through row-stride pointer addressing.
- Preserved crop, channel, tensor, prediction, and lock/unlock behavior.
- Added fail-closed source and documentation contracts.

## Verification

- `python3 -B scripts/check-ios-camera-source.py --mode behavior` passed.
- Full `make check` passed project, behavior, resource-integrity, and all 16
  workflow mutation contracts; the build target truthfully reported that local
  `xcodebuild` is unavailable.
- The same full gate passed from an external working directory.
- Seven focused mutations covering signed x/y products, narrowed x/y indices,
  the legacy expression, documentation drift, and plan-status regression were
  rejected.
- Parsed 1 workflow YAML file, 1 plist, 5 JSON files, and 2 SVG files; Python
  syntax, diff whitespace, generated-artifact, and intended-diff secret audits
  passed.
- Plan-aware arithmetic, frame-bounds, testing, maintainability, and scope
  review found no actionable findings. Browser testing is not applicable to
  this native Objective-C++ camera sample.
