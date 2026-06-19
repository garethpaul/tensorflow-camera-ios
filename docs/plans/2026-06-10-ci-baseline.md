# CI Contract Gate

## Status: Completed

## Context

The repository had a deterministic `make check` baseline but no hosted check
to prevent camera safety contracts or completed maintenance plans from
regressing. The full Objective-C++ application requires Xcode and legacy
TensorFlow dependencies, which are unavailable on a standard Linux runner.

## Objectives

- Run the portable source and project contracts on pushes and pull requests.
- Keep the workflow least-privilege, credential-free, and bounded.
- Pin third-party actions to immutable commits backed by Node 24 runtimes.
- Test workflow policy structurally without adding parser dependencies.
- Make the Linux gate's limits explicit rather than implying an iOS build.

## Work Completed

- Added `.github/workflows/check.yml` for pushes to `master`, pull requests,
  and manual runs.
- Granted only read access to repository contents, disabled checkout credential
  persistence, enabled concurrency cancellation, and set a five-minute timeout.
- Pinned checkout and Python setup actions to immutable Node 24 commits.
- Ran the existing `make check` entry point with Python 3.12 on Ubuntu 24.04.
- Added dependency-free structural validation and 16 hostile mutations covering
  credentials, permissions, triggers, actions, runtime bounds, Python, and the
  required gate command.
- Added SHA-256 resource checks, root-independent Make targets, and the correct
  optional Xcode target while documenting its absent generated archives.
- Documented the hosted baseline in README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 -B scripts/test_workflow_contract.py`
- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make lint`
- `make contract-test`
- `make test`
- `make build`
- `make check`
- `make -f /path/to/tensorflow-camera-ios/Makefile check` outside the repository
- negative resource, teardown-order, and workflow-policy mutations
- `git diff --check`

The Linux job validates portable source, asset, documentation, and workflow
contracts. It does not compile the iOS target, run a simulator, exercise a
camera, or validate the legacy TensorFlow binary integration. A future macOS
job should add that coverage once the exact Xcode and dependency versions are
documented and reproducible.
