#!/usr/bin/env python3
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

spec = importlib.util.spec_from_file_location(
    "camera_source_policy",
    SCRIPT_DIR / "check-ios-camera-source.py",
)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

ORIGINAL_FIXTURE = (REPOSITORY_ROOT / policy.CREDENTIAL_FIXTURE).read_bytes()


def require_error(errors, expected):
    if not any(expected in error for error in errors):
        raise AssertionError("expected policy error %r, got %r" % (expected, errors))


def write_fixture(root, content=ORIGINAL_FIXTURE):
    fixture = root / policy.CREDENTIAL_FIXTURE
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_bytes(content)
    return fixture


with tempfile.TemporaryDirectory(prefix="tensorflow-camera-credential-policy-") as directory:
    root = Path(directory)
    policy.ROOT = root

    fixture = write_fixture(root)
    if policy.credential_fixture_checks():
        raise AssertionError("reviewed upstream fixture must pass the isolated policy")

    fixture.write_bytes(ORIGINAL_FIXTURE + b"\n")
    require_error(policy.credential_fixture_checks(), "fixture hash mismatch")

    metadata = json.loads(ORIGINAL_FIXTURE.decode("utf-8"))
    metadata["project_id"] = "unexpected_project"
    fixture.write_text(json.dumps(metadata), encoding="utf-8")
    require_error(policy.credential_fixture_checks(), "must retain fake project_id")

    fixture.unlink()
    require_error(policy.credential_fixture_checks(), "fixture is missing")

    write_fixture(root)
    marker = ("-----BEGIN " + "PRIVATE KEY" + "-----").encode("ascii")
    extra_fixture = root / "testdata" / "unexpected-credential.txt"
    extra_fixture.parent.mkdir(parents=True, exist_ok=True)
    extra_fixture.write_bytes(marker + b"\nnot-a-real-key")
    require_error(policy.credential_fixture_checks(), str(extra_fixture.relative_to(root)))

    extra_fixture.write_bytes(b"x" * (64 * 1024 - 5) + marker + b"\n")
    require_error(policy.credential_fixture_checks(), str(extra_fixture.relative_to(root)))

print("credential fixture policy tests passed (5 hostile scenarios rejected)")
