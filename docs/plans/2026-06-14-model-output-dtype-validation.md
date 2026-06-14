# Model Output Dtype Validation

## Status: Planned

## Context

The camera validates empty output collections, empty labels, invalid UTF-8
labels, and non-finite prediction values. It still calls TensorFlow's typed
`flat<float>()` accessor without first confirming that the model output tensor
is `DT_FLOAT`.

## Priority

High runtime resilience. A mismatched or corrupted model output must be rejected
before a typed tensor accessor can assert or interpret incompatible storage.

## Requirements

- Validate the first output tensor's dtype before calling `flat<float>()`.
- Accept only `tensorflow::DT_FLOAT`, matching the existing prediction path.
- Log and skip incompatible output without publishing new prediction values.
- Preserve empty-output, empty-label, finite-value, threshold, UTF-8 label, and
  main-queue publication behavior.
- Add fail-closed source contracts, maintained documentation, mutation coverage,
  and completed verification evidence.

## Scope Boundaries

- Do not convert other tensor dtypes or change model resources, TensorFlow
  dependencies, prediction thresholds, labels, camera sampling, or UI behavior.
- Do not claim native compilation or camera runtime coverage from Linux.

## Implementation Units

1. Guard output dtype before typed flattening in
   `app/CameraExampleViewController.mm`.
2. Extend `scripts/check-ios-camera-source.py` and maintained documentation.
3. Verify focused contracts, full static gates, hostile mutations, and final
   artifact and secret audits.

## Verification

- focused camera source contract
- repository and external-directory `make check`
- hostile dtype predicate, ordering, diagnostic, typed-access, documentation,
  and plan-status mutations
- generated-artifact, credential-pattern, protected-path, exact-diff, and
  staged-path audits

## Risks

- Linux and hosted Ubuntu validate source contracts but do not compile the
  Objective-C++ iOS target.
- Model outputs with supported numeric but non-float dtypes remain intentionally
  unsupported rather than implicitly converted.
