# Make Root Override Protection

## Status: Planned

## Context

The Makefile derives checker and Xcode project paths from its own location, but
environment and command-line assignments can replace `ROOT`. A caller can
therefore redirect portable contracts or the optional native build away from
the checked-out camera sample.

## Priority

Repository verification paths are a trust boundary. The Makefile must select
its own root while preserving intentional Python and Xcode tool overrides.

## Objectives

- Protect the repository-derived root from caller assignments.
- Preserve `PYTHON` and `XCODEBUILD` overrides and declaration order.
- Preserve all six public aliases, workflow contracts, and Xcode project path.
- Exercise aliases from repository and external working directories under
  hostile environment and command-line root values.
- Add fail-closed source, README, and completed-plan contracts.

## Implementation Units

### U1. Protect repository paths

**Files:** `Makefile`

Make the root assignment authoritative without changing tool overrides,
targets, checker commands, or native build arguments.

### U2. Preserve the contract

**Files:** `scripts/check-ios-camera-source.py`, `README.md`

Require one root assignment total, the exact protected declaration, tool
ordering, alias graph, root-anchored checker/project paths, README indexing,
and this plan's completed evidence.

## Verification

- Project, behavior, workflow, resource-integrity, and full `make check` gates.
- Repository/external working directories and hostile root assignments.
- Declaration, duplicate, placement, alias, path, README, and plan mutations.
- Exact diff, protected source/project/workflow/resource, artifact, secret, and
  whitespace audits.
- Exact-head hosted contract verification.

## Scope Boundary

This change does not alter Objective-C++, camera lifecycle, sampling, project
settings, model resources, workflow policy, or generated TensorFlow archives.
