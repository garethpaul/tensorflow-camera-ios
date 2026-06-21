# Make Authority Isolation

Status: Completed

## Context

The verification Makefile protected direct `ROOT` assignment but used a
whitespace-sensitive checkout expression. Caller-selected shells, bypassing
Make modes, preload files, and additional `-f` programs could replace checks.

## Work Completed

- Added space-safe root derivation, fixed shell authority, and fail-closed Make
  metadata and mode validation.
- Preserved trusted Python, C++ compiler, and Xcode executable overrides.
- Added a bounded authority harness across all seven public targets and pinned
  hosted dispatch to `/usr/bin/make`.

## Verification

- `make root-test` passed 35 target/authority cases, one literal-dollar tool
  case, one raw tool Make-syntax rejection, two `MAKEFILE_LIST` rejections, two
  contained startup-boundary cases, and ten mode-flag rejections.
- Repository and external-directory `make check` passed with the SDK-free gate.
- Exact PR-head contract run `27899101898` and CodeQL run `27899101427`
  passed before merge.
- Merged-head contract run `27899143177` and CodeQL run `27899142950`
  passed at `5900fae9e9c0aa6df281959b3f8677a71f927df3`.

## Trust Boundary

GNU Make preload and earlier additional-file parse expressions can execute
before the repository Makefile rejects them. Trusted automation must invoke
only this Makefile. Tool overrides remain trusted inputs and are shell-quoted.

## Scope Boundary

This change does not alter Objective-C++, camera behavior, model resources,
project settings, dependencies, or generated TensorFlow archives.
