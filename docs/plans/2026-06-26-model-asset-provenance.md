# Model Asset Provenance Contract

Status: Completed

## Context

The repository pinned model resource bytes and documented their recovery URLs,
but the bundled Apache license sat beside a sample image that was not part of
the model archive. Readers could incorrectly assume one notice covered every
file in `app/data`.

## Decision

- Record provenance and copyright status per upstream asset group.
- Identify the graph, labels, and license as the exact contents of TensorFlow's
  official `inception5h.zip` archive under its included Apache-2.0 notice.
- Identify `grace_hopper.jpg` by exact byte match to TensorFlow v0.12.0 and the
  Wikimedia Commons copy of the 1984 U.S. Navy official portrait.
- Preserve the public-domain basis, photographer, and naval identifier without
  claiming that TensorFlow's Apache license applies to the photograph.
- Fail the portable project gate if the provenance boundary disappears.

## Verification

- The checked-in image and Commons original both produced SHA-256
  `e1f57e98cf38076c0f9a058d74ffddf90f20453e436033784606b63c8ed2e49a`.
- TensorFlow v0.12.0's camera data directory records the same image blob.
- `inception5h.zip` contains only the graph, labels, and Apache `LICENSE`.
- `make check` passed the project, workflow, credential, native C++, mutation,
  and Make authority gates.
- `xcodebuild not found; static project checks completed`; no iOS runtime claim
  is made for this documentation and supply-chain change.
- `git diff --check` passed.

## Residual Risk

The upstream GCS archive has no versioned landing page containing a richer
model card. The repository therefore preserves the reviewed URL, exact archive
digest, included notice, and installed-file digests rather than relying on the
current contents of a mutable download endpoint.
