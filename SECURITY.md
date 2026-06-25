# Security Policy

## Supported Versions

The supported security scope for `tensorflow-camera-ios` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: A tensorflow camera for iOS.

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/tensorflow-camera-ios` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Apple platform application or Swift sample. The active security scope is the code and documentation on the default branch.
- Review found authentication, token, or session-related code paths; changes in those areas should receive security-focused review before merge.
- Review found external API integrations or credential-adjacent configuration; changes in those areas should receive security-focused review before merge.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found mobile permission or privacy-sensitive data handling; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found shell execution, subprocess, or dynamic evaluation surfaces; changes in those areas should receive security-focused review before merge.
- Review found database, model, query, or persistence-related code; changes in those areas should receive security-focused review before merge.
- Review found secret-like configuration names that require careful review before use; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.
- GitHub Actions runs the SDK-free `make check` baseline with read-only
  repository permissions and credential-free checkout on Ubuntu 24.04, a
  five-minute timeout, concurrency cancellation, and commit-pinned Node 24
  actions. Structural mutation tests reject contradictory credential settings,
  write permissions, and unreviewed actions. The gate verifies exact SHA-256
  digests for the graph, label set, and sample image.
- Model labels that fail explicit UTF-8 conversion are skipped before they can
  become invalid Objective-C collection keys.
- Camera teardown stops local capture, detaches frame callbacks, and drains
  already-enqueued work before releasing its serial queue. Queue-specific
  identity prevents that drain from synchronously waiting on itself.
- Camera capture is suspended whenever the controller is hidden or the
  application resigns active, without silently changing the user's explicit
  Freeze/Continue choice.
- Camera preprocessing rejects impossible dimensions and undersized Core Video
  row strides before locking or reading frame memory.
- Camera sampling coordinate arithmetic promotes resize-loop intermediates
  before multiplication and pointer offset calculation.
- Finite model predictions are required before scores cross into Objective-C
  collections; malformed non-finite outputs are logged and skipped.
- Model prediction range validation rejects finite softmax values outside the
  inclusive `[0, 1]` probability range before smoothing or presentation.
- Model output dtype validation rejects incompatible prediction tensors before
  TensorFlow typed access or Objective-C publication.
- The reviewed upstream credential fixture is the sole allowed key-shaped file.
  Project checks pin its TensorFlow testdata SHA-256 and fake service-account
  identity, and reject private-key PEM markers at every other repository path.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

The reviewed TensorFlow OAuth fixture is a narrow upstream-test compatibility
exception, not permission to commit application credentials or additional test
keys. Any change to its path, digest, or fake identity requires explicit
upstream provenance review.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
