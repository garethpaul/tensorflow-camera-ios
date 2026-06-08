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
- Model asset drops without provenance
- Broad framework rewrites without preserving the sample path

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
