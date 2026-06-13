# Sampling Coordinate Arithmetic

## Status: Planned

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
