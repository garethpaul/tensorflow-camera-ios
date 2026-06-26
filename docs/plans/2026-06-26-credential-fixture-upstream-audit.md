# Credential Fixture Upstream Audit

Status: Completed

## Context

The repository already allowed one byte-pinned, private-key-shaped TensorFlow
test fixture. The roadmap required checking that its provenance stayed aligned
with upstream rather than assuming the historical snapshot remained sufficient.

## Evidence

- TensorFlow file history shows the fixture was introduced by commit
  `bb465cdc0ed9c3b9b4f031505ea2294375677807`.
- The introduction commit, TensorFlow v0.12.0, reviewed snapshot
  `e444cffb938a99d664631aee2544e25314a9e39d`, and current reviewed commit
  `fba94bc288cbbee7b1a09dec1d61b1c307ca3b79` all produce SHA-256
  `c7d61aaf782924787e979bb3b64e8ccdce81b838d03c44f5dce746e3365ff2f9`.
- Current TensorFlow also carries the same blob at the legacy core path and the
  XLA mirror path.
- No byte or fake-metadata drift was found.

## Decision

- Keep the vendored fixture unchanged.
- Add adjacent provenance without reproducing or printing key material.
- Make the offline project gate require the reviewed lineage, dual current
  paths, digest, and no-drift conclusion.
- Reject network access in `make check`; mutable upstream availability must not
  make local verification flaky or silently redefine the accepted bytes.

## Verification

- RED project gate failed because `app/platform/cloud/testdata/PROVENANCE.md`
  was missing.
- RED isolated policy suite failed because the provenance fixture was missing.
- `credential fixture policy tests passed (7 hostile scenarios rejected)` after
  adding missing-provenance and lineage-drift cases.
- `make check` passed all project, workflow, credential, native C++, mutation,
  Make authority, and static build gates.
- `xcodebuild not found; static project checks completed`; no OAuth, network,
  Bazel, or iOS runtime claim is made.
- `git diff --check` passed.

## Follow-up

Re-run this audit only when the vendored cloud OAuth code, fixture bytes,
fixture paths, or authoritative TensorFlow lineage changes.
