## TensorFlow Camera iOS Vision

TensorFlow Camera iOS is an Objective-C++ iOS camera sample that runs an
Inception-style TensorFlow model on live camera frames and displays labels near
recognized objects.

The repository is useful as a historical mobile ML example combining AVCapture,
TensorFlow model loading, image preprocessing, and label rendering.

The goal is to preserve the camera inference sample while making model assets,
camera permissions, and legacy TensorFlow/iOS build assumptions explicit.

The current focus is:

Priority:

- Preserve the camera-frame inference flow
- Keep model and label filenames documented
- Make camera permission and local inference behavior clear
- Keep no-camera and unsupported-frame cases from becoming crash-only paths
- Keep still-image and video-data output setup fail-closed
- Keep freeze/resume controls fail-closed when capture setup is unavailable
- Keep front/back camera switching fail-closed when replacement inputs fail
- Keep camera frame preprocessing faithful to source coordinates and row stride
- Keep model outputs and labels bounded before rendering predictions
- Keep missing model or label assets user-visible instead of fatal
- Keep shared bundle-resource lookup non-fatal for model paths
- Keep label file loading fail-closed before prediction rendering
- Keep invalid label encodings from reaching prediction UI collections
- Keep manually retained camera-controller state released during teardown
- Stop capture callbacks and clear borrowed session state during teardown
- Keep completed maintenance plans under `docs/plans`
- Keep the SDK-free `make check` baseline running in GitHub Actions
- Keep hosted verification read-only, credential-free, pinned, and structurally
  protected against workflow policy regressions
- Keep graph, label, and sample-image integrity deterministic
- Treat Bazel, TensorFlow, and Objective-C++ setup as legacy context

Next priorities:

- Document exact build tool versions and model download expectations
- Add a no-camera test path for image preprocessing and label output
- Clarify licensing/provenance for downloaded model assets
- Modernize ML dependencies only in a dedicated compatibility pass

Contribution rules:

- One PR = one focused camera, model, preprocessing, build, or documentation change.
- Do not commit private images or user camera captures.
- Keep model downloads reproducible and attributed.
- Include device or simulator notes for runtime changes.

## Security And Responsible Use

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Camera ML samples can process sensitive scenes. Inference should remain local by
default, captures should not be stored or uploaded silently, and camera
permissions should be obvious to users.

## What We Will Not Merge (For Now)

- Silent image upload or storage
- Private camera captures in fixtures
- Unguarded camera input replacement during front/back switching
- Freeze/resume UI changes against a missing capture session
- Model asset drops without provenance
- Fatal bundle-resource lookups for optional model paths
- Broad framework rewrites without preserving the sample path

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
