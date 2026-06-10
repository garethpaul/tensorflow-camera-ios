# CI Contract Gate

## Status: Completed

## Context

The repository had a deterministic `make check` baseline but no hosted check
to prevent camera safety contracts or completed maintenance plans from
regressing. The full Objective-C++ application requires Xcode and legacy
TensorFlow dependencies, which are unavailable on a standard Linux runner.

## Objectives

- Run the portable source and project contracts on pushes and pull requests.
- Keep the workflow least-privilege and bounded.
- Pin third-party actions to immutable commits backed by Node 24 runtimes.
- Make the Linux gate's limits explicit rather than implying an iOS build.

## Work Completed

- Added `.github/workflows/check.yml` for pushes to `master`, pull requests,
  and manual runs.
- Granted only read access to repository contents and set a five-minute job
  timeout.
- Pinned checkout and Python setup actions to immutable Node 24 commits.
- Ran the existing `make check` entry point with Python 3.12.
- Extended the project checker to enforce the workflow's security and runtime
  contract.
- Documented the hosted baseline in README, SECURITY, VISION, and CHANGES.

## Verification

- `python3 -m py_compile scripts/check-ios-camera-source.py`
- `python3 scripts/check-ios-camera-source.py --mode project`
- `python3 scripts/check-ios-camera-source.py --mode behavior`
- `make check`
- `git diff --check`

The Linux job validates portable source, asset, documentation, and workflow
contracts. It does not compile the iOS target, run a simulator, exercise a
camera, or validate the legacy TensorFlow binary integration. A future macOS
job should add that coverage once the exact Xcode and dependency versions are
documented and reproducible.
