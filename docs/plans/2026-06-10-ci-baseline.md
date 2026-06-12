# TensorFlow Camera iOS CI Baseline

## Status: Completed

## Context

`tensorflow-camera-ios` already has SDK-free project and behavior checks behind
`make check`. The repository needs a lightweight GitHub Actions gate so future
changes run the same static baseline before review.

## Objectives

- Run the existing static baseline in GitHub Actions.
- Keep the workflow small enough to run without Xcode or camera hardware.
- Make the CI workflow presence part of the checked repository contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up Python 3.12 in CI for the repository checker.
- Extended the project checker to require the CI workflow and this completed
  plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `git diff --check`

## Follow-Up Candidates

- Add a macOS/Xcode build job once the required Xcode and simulator target are
  documented.
