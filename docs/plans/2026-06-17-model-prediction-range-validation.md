# Model Prediction Range Validation

## Status: In Progress

## Context

The `softmax1` inference path rejects non-float tensors and non-finite values,
but it still accepts arbitrarily large finite predictions. Those values enter
Objective-C smoothing state and later reach `roundf(value * 100.0f)` followed
by an `int` conversion in the overlay renderer. A malformed finite output can
therefore overflow presentation arithmetic despite the existing finite-value
guard.

## Priority

1. Reject finite model outputs outside the semantic probability range before
   they cross into Objective-C collections or UI publication.
2. Preserve the existing non-finite diagnostic, `0.05` display threshold,
   valid `[0, 1]` predictions, label bounds, and main-queue update ordering.
3. Add an executable framework-independent C++ boundary test and
   mutation-sensitive source contracts so the rule is not static prose only.

## Requirements

- Accept model prediction values from `0.0f` through `1.0f`, inclusive.
- Reject negative values and values greater than `1.0f` before thresholding,
  `NSNumber` creation, smoothing, sorting, percentage conversion, or speech.
- Keep NaN and infinity on the existing non-finite rejection path so range
  validation does not weaken or obscure that diagnostic.
- Put the unit-range predicate in a small framework-independent header used by
  both the Objective-C++ controller and an executable C++ test.
- Run the executable boundary test through `make test` and therefore through
  the canonical `make check` gate from any working directory.
- Add completed-plan, maintained-documentation, ordering, Makefile, runner,
  and hostile-mutation contracts without changing model resources, labels,
  camera capture, TensorFlow graph execution, or the display threshold.

## Implementation Units

### U1. Define and execute the probability boundary

- **Files:** `app/prediction_validation.h`,
  `tests/prediction_validation_test.cc`,
  `scripts/run-prediction-range-tests.sh`, `Makefile`
- **Outcome:** A dependency-free C++ test accepts both inclusive endpoints and
  representative in-range values while rejecting negative, over-one,
  non-finite, and extreme finite values.

### U2. Guard the inference-to-UI boundary

- **Files:** `app/CameraExampleViewController.mm`,
  `scripts/check-ios-camera-source.py`
- **Outcome:** The controller keeps its finite guard first, then rejects
  out-of-range values before the existing display threshold and collection
  creation.

### U3. Record the maintained contract

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, `AGENTS.md`,
  `docs/plans/2026-06-17-model-prediction-range-validation.md`
- **Outcome:** Documentation distinguishes finite-value safety from semantic
  model prediction range validation and records actual verification evidence.

## Verification

- Focused executable C++ prediction boundary test.
- Focused project and camera behavior source contracts.
- Repository and external-directory `make check`.
- Hostile mutations for the helper predicate, inclusive endpoints, controller
  call, validation ordering, diagnostic, runner, Makefile wiring,
  documentation, and completed plan evidence.
- Exact-diff, generated-artifact, credential-pattern, protected-fixture,
  executable-mode, and staged-path audits.
- Exact-head hosted contract evidence after push; no native iOS build is
  claimed because the clean repository lacks generated TensorFlow archives.

## Scope Boundaries

- This plan supersedes the earlier finite-prediction plan only for finite
  values that violate the model's `[0, 1]` probability contract.
- It does not clamp, renormalize, or reinterpret malformed output.
- It does not change UI layout, ranking, smoothing, camera lifecycle,
  preprocessing, labels, model files, workflow permissions, or credentials.
