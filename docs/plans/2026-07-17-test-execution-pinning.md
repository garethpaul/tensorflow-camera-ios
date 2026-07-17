# Test Execution Pinning

Status: Completed

## Context

The gate pinned the *content* of every test runner and mutation tester but not
their *execution*. Each pin was a substring search, so a runner could be
reduced to work it never performed while every pin stayed satisfied:

- The three C++ runners were pinned on `"$TEMP_DIR/<name>_test"`. That string
  also appears on the compile line as `-o "$TEMP_DIR/<name>_test"`, so deleting
  the final exec line left the pin substring-satisfied by the compile
  argument. The runners then compiled each test and never ran it.
- `run-ios-build.sh` was pinned on individual `xcodebuild` argument lines.
  Prefixing the invocation with `:` turned it into a no-op while every
  argument pin stayed satisfied.
- `test-makefile-root.sh` (5506 bytes, 35 authority cases) was pinned by a
  single string, `run-prediction-output-tests.sh`, which a comment satisfies.
- The two mutation testers were pinned only by their mutation description
  strings, which a list literal or a comment satisfies.
- The two contract testers had no content pins at all, so each collapsed to a
  `print` of its own success message.

Nothing asserted any runner's success message, so all of the above were silent.

Because the description strings were substring pins, pinning only the
mutate/compile/run chain would still have left an empty-table bypass: the
descriptions could sit in a comment while `mutations = {}` ran nothing and the
tester printed "0 mutations rejected". The mutation and contract tables are
therefore pinned as anchored table entries, which prose cannot satisfy.

## Work Completed

- Pinned each C++ runner's exec line as a whole line exactly once, anchored
  with `re.findall(r"^...$", ..., re.MULTILINE)` so the `-o` compile argument
  cannot satisfy it.
- Pinned the `"$XCODEBUILD"` invocation in `run-ios-build.sh` as a whole line.
- Pinned `test-makefile-root.sh`'s `run_case` definition and its 35-case
  execution/count assertion as whole lines.
- Pinned the mutate/compile/run/assert chain of both mutation testers as whole
  lines, so each pinned mutation description must flow through a real compile
  and run, and pinned each mutation description as an anchored table entry.
- Pinned the workflow contract tester's mutate/validate/assert chain and its 17
  mutation table entries, and the credential fixture policy tester's
  `require_error` definition and its eight isolated-policy assertions.

## Verification

- `make check` passed unchanged at each step.
- Each new assertion was verified live: re-applying the corresponding probe is
  rejected with the new message and `make check` exits 2.
- Each new assertion was verified load-bearing: with the assertion deleted the
  same probe makes `make check` exit 0, confirming nothing else caught it.
- Deleting the exec line from all three C++ runners passed the pre-change gate
  with exit 0; it is now rejected.
- Stubbing `test-makefile-root.sh` to 277 bytes that print its own success
  message passed the pre-change gate with exit 0; it is now rejected.
- Stubbing both mutation testers to a `print` passed the pre-change gate with
  exit 0; they are now rejected.
- Stubbing both contract testers to a `print` passed the pre-change gate with
  exit 0; they are now rejected.
- The empty-table bypass described above passed an intermediate form of this
  change with exit 0 and is rejected by the anchored table-entry pins.

## Trust Boundary

These are static content pins, so they bound what the checker will accept in
the repository; they are not a runtime guarantee. `run-ios-build.sh` still
takes the `command -v` early-exit branch without Xcode, so its pin was verified
statically only and no iOS build or runtime behavior was executed.

## Scope Boundary

This change only strengthens verification. No Objective-C++, camera behavior,
C++ headers, tests, runners, mutation testers, model resources, project
settings, dependencies, or workflow files changed. No test outcome changed:
every runner and mutation tester passed before and after, so this closes a
verification gap rather than fixing an observed regression.
