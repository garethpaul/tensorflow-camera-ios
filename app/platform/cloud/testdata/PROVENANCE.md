# Service Account Test Fixture Provenance

`service_account_credentials.json` is public TensorFlow testdata used by the
vendored cloud OAuth tests. It is not application configuration and must never
be replaced with a real credential.

## Immutable fixture identity

- Repository path: `app/platform/cloud/testdata/service_account_credentials.json`
- SHA-256: `c7d61aaf782924787e979bb3b64e8ccdce81b838d03c44f5dce746e3365ff2f9`
- Required metadata: fake service-account identifiers enforced by
  `scripts/check-ios-camera-source.py`
- Allowed key-shaped files: this exact path only

Do not copy, regenerate, decode, print, or duplicate the fixture key. Any byte,
path, or fake-metadata change requires a new upstream provenance review.

## Upstream lineage

The fixture was introduced in TensorFlow commit
`bb465cdc0ed9c3b9b4f031505ea2294375677807` and has the same reviewed bytes in:

- TensorFlow v0.12.0 at
  `tensorflow/core/platform/cloud/testdata/service_account_credentials.json`
- Reviewed snapshot `e444cffb938a99d664631aee2544e25314a9e39d`
- TensorFlow `master` commit `fba94bc288cbbee7b1a09dec1d61b1c307ca3b79`
  at the legacy core path above
- The same current commit's mirror at
  `third_party/xla/xla/tsl/platform/cloud/testdata/service_account_credentials.json`

No byte or fake-metadata drift was found across those references during the
June 26, 2026 review. The current-head commit records evidence at that date; the
immutable introduction, v0.12.0, snapshot, and digest remain the durable pins.

## Related tests

The vendored fixture is referenced by `app/platform/cloud/BUILD`,
`app/platform/cloud/oauth_client_test.cc`, and
`app/platform/cloud/google_auth_provider_test.cc`.
