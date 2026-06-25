# AGENTS.md

## Repository purpose

`garethpaul/tensorflow-camera-ios` is an Apple platform application or Swift sample. A tensorflow camera for iOS.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `app` - application source or app module

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- Lint/static checks: `make lint`
- Workflow contract mutations: `make contract-test`
- Tests: `make test`
- Build: `make build`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: C++ (142), C/C++ headers (107), Objective-C (1), Objective-C++ (1).

## Testing guidance

- Test-related files detected: `app/common_runtime/constant_folding_test.cc`, `app/common_runtime/device_set_test.cc`, `app/common_runtime/direct_session_test.cc`, `app/common_runtime/direct_session_with_tracking_alloc_test.cc`, `app/common_runtime/function_test.cc`, `app/common_runtime/gpu/gpu_allocator_retry_test.cc`, `app/common_runtime/gpu/gpu_bfc_allocator_test.cc`, `app/common_runtime/gpu/gpu_debug_allocator_test.cc`, `app/common_runtime/gpu/gpu_event_mgr_test.cc`, `app/common_runtime/gpu/gpu_stream_util_test.cc`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.
- Preserve model prediction range validation before Objective-C publication;
  `make test` executes its framework-independent C++ boundary test.
- Preserve the three-part camera running-state gate: explicit user capture
  intent, visible controller state, and active application state. Lifecycle
  suspension must not rewrite the user's Freeze/Continue choice.
- Keep hosted verification read-only and credential-free with immutable action
  pins; update the structural workflow mutations with any intentional policy
  change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- Preserve the reviewed upstream credential fixture only at
  `app/platform/cloud/testdata/service_account_credentials.json` with its
  pinned digest and fake identity; do not add or allow any other key-shaped
  fixture, application credential, token, or local secret.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- A clean checkout does not include the generated TensorFlow/protobuf archives
  required for a full Xcode link; do not report the SDK-free gate as an iOS
  build or runtime test.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- See `docs/plans/2026-06-08-tensorflow-camera-ios-baseline.md` for the canonical camera lifecycle baseline.
- See `docs/plans/2026-06-08-model-output-bounds.md` for the model output and label bounds guard.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
