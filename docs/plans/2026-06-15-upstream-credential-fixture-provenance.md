# Upstream Credential Fixture Provenance

## Status: Completed

## Summary

Make the repository's private-key-shaped service-account test fixture an
explicit, immutable TensorFlow upstream exception rather than an undocumented
secret-like file. Preserve the fixture required by vendored OAuth tests while
rejecting any drift or any additional tracked private-key PEM marker.

## Problem Frame

`app/platform/cloud/testdata/service_account_credentials.json` contains an RSA
private key used by vendored TensorFlow OAuth tests. The surrounding identifiers
are explicitly fake, GitHub secret scanning reports no alert, and the exact
fixture remains public in TensorFlow upstream at commit
`e444cffb938a99d664631aee2544e25314a9e39d`.

The file is nevertheless indistinguishable from a credential during an
uncontextualized repository scan. Leaving it undocumented makes future reviews
ambiguous, while deleting or replacing it would silently break the vendored
test contract. The portable checker should encode the one allowed path,
upstream digest, and fake identity, then reject all other key-shaped content.

## Priorities

1. Prevent new tracked private-key fixtures or accidental credential commits.
2. Detect any byte-level drift in the one reviewed TensorFlow upstream fixture.
3. Preserve vendored TensorFlow OAuth test compatibility without copying,
   regenerating, or modifying key material.
4. Document provenance and the narrow exception in contributor and security
   guidance.

## Requirements

- **R1:** The existing credential fixture must remain byte-for-byte unchanged at
  SHA-256 `c7d61aaf782924787e979bb3b64e8ccdce81b838d03c44f5dce746e3365ff2f9`.
- **R2:** Repository file scanning must reject RSA, generic, EC, DSA, encrypted,
  OpenSSH, or PGP private-key markers outside the exact reviewed fixture path.
- **R3:** The reviewed JSON must parse and retain `type: service_account`,
  `project_id: fake_project_id`, `private_key_id: fake_key_id`, and the fake
  TensorFlow test service-account email.
- **R4:** Project checks must fail when the fixture is missing, changed,
  relocated, duplicated, or loses its fake identity fields.
- **R5:** Maintained documentation must identify the fixture as public upstream
  testdata, prohibit any broader key exception, and link its authoritative
  TensorFlow source.
- **R6:** Completed verification must include repository/external gates, focused
  hostile mutations, exact protected-path proof, and secret/artifact audits.

## Technical Decisions

- Scan file bytes instead of relying on filename extensions so renamed or
  extensionless key material cannot bypass the guard.
- Exclude `.git` internals from the repository file walk; the policy covers
  working-tree content that can be reviewed and committed.
- Allow exactly one path and one digest. Fake metadata is an additional semantic
  check, not a substitute for byte integrity.
- Do not rewrite, regenerate, print, or copy the key in implementation, tests,
  plans, logs, or documentation.

## Implementation Units

### U1. Enforce the single reviewed fixture

**Files:** `scripts/check-ios-camera-source.py`

Add the fixture path and SHA-256 to project checks, parse its JSON metadata, scan
repository file bytes for common private-key PEM markers, and fail for every
marker path except the exact reviewed fixture.

### U2. Make the policy mutation-sensitive

**Files:** `scripts/check-ios-camera-source.py`,
`docs/plans/2026-06-15-upstream-credential-fixture-provenance.md`

Require completed-plan evidence and exercise mutations for digest drift,
additional key-shaped content, path relocation, missing fake metadata, removed
marker scanning, broadened allowlisting, documentation drift, and incomplete
plan status.

### U3. Synchronize maintained guidance

**Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`, `AGENTS.md`

Document why the fixture remains, where it came from, and why contributors must
not add any other credential or private-key fixture.

## Verification

- Run the focused project checker and complete `make check` gate.
- Run the complete gate from an external working directory.
- Run isolated hostile mutations with expected policy failure messages.
- Confirm the fixture path and digest are unchanged from the stack base.
- Audit generated artifacts, credential signatures outside the reviewed path,
  conflict markers, staged paths, and whitespace.

## Scope Boundaries

- Do not edit, delete, regenerate, decode, print, or duplicate the fixture key.
- Do not modify vendored OAuth code, Bazel targets, public-key testdata, or
  TensorFlow dependencies.
- Do not treat the fixture exception as permission for application credentials,
  signing keys, tokens, environment files, or additional test keys.
- Do not claim native iOS, Bazel, OAuth, or network runtime validation on Linux.
- Do not merge or close stacked pull requests without explicit authorization.

## References

- TensorFlow upstream fixture at the reviewed commit:
  <https://github.com/tensorflow/tensorflow/blob/e444cffb938a99d664631aee2544e25314a9e39d/tensorflow/core/platform/cloud/testdata/service_account_credentials.json>
- Vendored OAuth tests reference this fixture through
  `app/platform/cloud/BUILD`, `app/platform/cloud/oauth_client_test.cc`, and
  `app/platform/cloud/google_auth_provider_test.cc`.

## Completion Evidence

- The focused credential policy suite passed the reviewed fixture and rejected
  digest drift, fake-identity drift, relocation, an additional key marker, and
  a marker split across streaming scan chunks.
- The repository and external-directory `make check` passed project, behavior,
  credential-fixture, resource-integrity, and all 16 workflow mutation checks
  with the documented static-only Linux boundary.
- Ten hostile credential-fixture mutations were rejected across digest,
  metadata, path, marker scan, allowlist, stream overlap, test registration,
  documentation, and completed-plan contracts.
- The protected fixture path and digest remained unchanged from the stack base.
- The generated-artifact and credential-pattern audits passed with no key marker
  outside the reviewed upstream fixture.
- No native iOS build, Bazel OAuth test, network request, real credential, or
  deployment was exercised.
