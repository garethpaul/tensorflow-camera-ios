# Prediction Output Native Contract

Status: Completed

## Context

The repository already exercised center-crop, row-stride, and RGB channel
preprocessing without a camera. Model prediction validation separately covered
finite unit-range values, but the model-score-to-label mapping remained inside
the Objective-C++ camera controller and could not execute on a host without
UIKit, TensorFlow archives, or camera hardware.

## Decision

- Extract framework-independent score-to-label selection into
  `app/prediction_output.h`.
- Bound selection by the shorter prediction and label count.
- Preserve the strict `> 0.05` display threshold and original model order.
- Reject non-finite thresholds plus non-finite or out-of-range predictions.
- Keep Objective-C UTF-8 conversion, dictionary publication, smoothing,
  ranking, rendering, and speech behavior in the controller.
- Compile and execute the selector with the repository's C++11 host gate.

## Verification

- RED `scripts/run-prediction-output-tests.sh` failed because
  `prediction_output.h` did not exist.
- `Prediction output tests passed` after extraction and controller integration.
- `prediction output mutation tests passed (5 mutations rejected)` for
  inclusive threshold, label bound, prediction range, label association, and
  finite-threshold regressions.
- The first `make check` failed in Make-root isolation because the fixture had
  not stubbed the new shell runner; the harness was updated before proceeding.
- `Makefile root tests passed: 35 executed target/authority cases` after the
  fixture update.
- Final `make check` passed all project, behavior, workflow, credential,
  preprocessing, prediction, mutation, and Make authority gates.
- `xcodebuild not found; static project checks completed`; no simulator,
  device, full TensorFlow link, or camera runtime claim is made.
- `git diff --check` passed.

## Residual Risk

The host selector proves deterministic preprocessing and label selection but
does not execute the legacy TensorFlow graph, UIKit layers, speech output, or
camera callback path. Validate those only with reconstructed archives and the
matching Apple toolchain.
