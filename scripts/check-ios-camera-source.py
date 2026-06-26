#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from workflow_contract import validate as validate_workflow


ROOT = Path(__file__).resolve().parents[1]
DOCS_PLANS = ROOT / "docs" / "plans"
CANONICAL_PLAN = DOCS_PLANS / "2026-06-08-tensorflow-camera-ios-baseline.md"
CAMERA_OUTPUT_PLAN = DOCS_PLANS / "2026-06-09-camera-output-guard.md"
TAKE_PICTURE_SESSION_PLAN = DOCS_PLANS / "2026-06-09-take-picture-session-guard.md"
LABEL_LOAD_PLAN = DOCS_PLANS / "2026-06-09-label-load-guard.md"
CI_PLAN = DOCS_PLANS / "2026-06-10-ci-baseline.md"
RESOURCE_PLAN = DOCS_PLANS / "2026-06-10-model-resource-integrity.md"
CAPTURE_TEARDOWN_PLAN = DOCS_PLANS / "2026-06-10-capture-teardown-order.md"
LABEL_ENCODING_PLAN = DOCS_PLANS / "2026-06-12-label-encoding-guard.md"
CALLBACK_DRAIN_PLAN = DOCS_PLANS / "2026-06-12-capture-callback-drain.md"
FRAME_LAYOUT_PLAN = DOCS_PLANS / "2026-06-13-frame-layout-validation.md"
SAMPLING_ARITHMETIC_PLAN = DOCS_PLANS / "2026-06-13-sampling-coordinate-arithmetic.md"
ROOT_OVERRIDE_PLAN = DOCS_PLANS / "2026-06-14-make-root-override-protection.md"
MAKE_AUTHORITY_PLAN = DOCS_PLANS / "2026-06-21-make-authority-isolation.md"
FINITE_PREDICTIONS_PLAN = DOCS_PLANS / "2026-06-14-finite-model-predictions.md"
OUTPUT_DTYPE_PLAN = DOCS_PLANS / "2026-06-14-model-output-dtype-validation.md"
CREDENTIAL_FIXTURE_PLAN = DOCS_PLANS / "2026-06-15-upstream-credential-fixture-provenance.md"
PREDICTION_RANGE_PLAN = DOCS_PLANS / "2026-06-17-model-prediction-range-validation.md"
FRAME_PREPROCESSING_NATIVE_PLAN = DOCS_PLANS / "2026-06-19-frame-preprocessing-native-contract.md"
ACTIVE_SCREEN_LIFECYCLE_PLAN = DOCS_PLANS / "2026-06-25-active-screen-camera-lifecycle.md"
PREDICTION_OUTPUT_NATIVE_PLAN = DOCS_PLANS / "2026-06-26-prediction-output-native-contract.md"
TOOLCHAIN_MODEL_GUIDE = ROOT / "docs" / "toolchain-and-model-assets.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "check.yml"
RESOURCE_SHA256 = {
    "app/data/tensorflow_inception_graph.pb": "a39b08b826c9d5a5532ff424c03a3a11a202967544e389aca4b06c2bd8aef63f",
    "app/data/imagenet_comp_graph_label_strings.txt": "da2a31ecfe9f212ae8dd07379b11a74cb2d7a110eba12c5fc8c862a65b8e6606",
    "app/data/grace_hopper.jpg": "e1f57e98cf38076c0f9a058d74ffddf90f20453e436033784606b63c8ed2e49a",
    "app/data/LICENSE": "f086f362c12f3a0295ba186c8caa1d2778beb6b9a7651c499791f202c2429c0d",
}
CREDENTIAL_FIXTURE = "app/platform/cloud/testdata/service_account_credentials.json"
CREDENTIAL_FIXTURE_SHA256 = "c7d61aaf782924787e979bb3b64e8ccdce81b838d03c44f5dce746e3365ff2f9"
PRIVATE_KEY_PEM_LABELS = (
    "RSA PRIVATE KEY",
    "PRIVATE KEY",
    "EC PRIVATE KEY",
    "DSA PRIVATE KEY",
    "ENCRYPTED PRIVATE KEY",
    "OPENSSH PRIVATE KEY",
    "PGP PRIVATE KEY BLOCK",
)
PRIVATE_KEY_PEM_MARKERS = tuple(
    ("-----BEGIN " + label + "-----").encode("ascii")
    for label in PRIVATE_KEY_PEM_LABELS
)
PRIVATE_KEY_MARKER_OVERLAP = max(len(marker) for marker in PRIVATE_KEY_PEM_MARKERS) - 1


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require_paths():
    errors = []
    for relative_path in (
        "app/tensorflow_camera.xcodeproj/project.pbxproj",
        "app/Info.plist",
        "app/CameraExampleViewController.mm",
        "app/frame_preprocessing.h",
        "app/prediction_output.h",
        "app/prediction_validation.h",
        "app/CameraExampleAppDelegate.m",
        "tests/frame_preprocessing_test.cc",
        "tests/prediction_output_test.cc",
        "tests/prediction_validation_test.cc",
        "scripts/run-frame-preprocessing-tests.sh",
        "scripts/run-ios-build.sh",
        "scripts/run-prediction-output-tests.sh",
        "scripts/run-prediction-range-tests.sh",
        "scripts/test_frame_preprocessing_mutations.py",
        "scripts/test_prediction_output_mutations.py",
        "app/data/tensorflow_inception_graph.pb",
        "app/data/imagenet_comp_graph_label_strings.txt",
        "app/data/grace_hopper.jpg",
        "app/data/LICENSE",
        "docs/toolchain-and-model-assets.md",
        CREDENTIAL_FIXTURE,
    ):
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required file: {relative_path}")
    return errors


def docs_plan_checks():
    errors = []
    if not CANONICAL_PLAN.exists():
        errors.append("docs/plans/2026-06-08-tensorflow-camera-ios-baseline.md is missing")
    if not CAMERA_OUTPUT_PLAN.exists():
        errors.append("docs/plans/2026-06-09-camera-output-guard.md is missing")
    if not TAKE_PICTURE_SESSION_PLAN.exists():
        errors.append("docs/plans/2026-06-09-take-picture-session-guard.md is missing")
    if not LABEL_LOAD_PLAN.exists():
        errors.append("docs/plans/2026-06-09-label-load-guard.md is missing")
    if not CI_PLAN.exists():
        errors.append("docs/plans/2026-06-10-ci-baseline.md is missing")
    if not RESOURCE_PLAN.exists():
        errors.append("docs/plans/2026-06-10-model-resource-integrity.md is missing")
    if not CAPTURE_TEARDOWN_PLAN.exists():
        errors.append("docs/plans/2026-06-10-capture-teardown-order.md is missing")
    if not LABEL_ENCODING_PLAN.exists():
        errors.append("docs/plans/2026-06-12-label-encoding-guard.md is missing")
    if not CALLBACK_DRAIN_PLAN.exists():
        errors.append("docs/plans/2026-06-12-capture-callback-drain.md is missing")
    if not FRAME_LAYOUT_PLAN.exists():
        errors.append("docs/plans/2026-06-13-frame-layout-validation.md is missing")
    if not SAMPLING_ARITHMETIC_PLAN.exists():
        errors.append("docs/plans/2026-06-13-sampling-coordinate-arithmetic.md is missing")
    if not ROOT_OVERRIDE_PLAN.exists():
        errors.append("docs/plans/2026-06-14-make-root-override-protection.md is missing")
    if not MAKE_AUTHORITY_PLAN.exists():
        errors.append("docs/plans/2026-06-21-make-authority-isolation.md is missing")
    if not FINITE_PREDICTIONS_PLAN.exists():
        errors.append("docs/plans/2026-06-14-finite-model-predictions.md is missing")
    if not OUTPUT_DTYPE_PLAN.exists():
        errors.append("docs/plans/2026-06-14-model-output-dtype-validation.md is missing")
    if not CREDENTIAL_FIXTURE_PLAN.exists():
        errors.append("docs/plans/2026-06-15-upstream-credential-fixture-provenance.md is missing")
    if not PREDICTION_RANGE_PLAN.exists():
        errors.append("docs/plans/2026-06-17-model-prediction-range-validation.md is missing")
    if not FRAME_PREPROCESSING_NATIVE_PLAN.exists():
        errors.append("docs/plans/2026-06-19-frame-preprocessing-native-contract.md is missing")
    if not ACTIVE_SCREEN_LIFECYCLE_PLAN.exists():
        errors.append("docs/plans/2026-06-25-active-screen-camera-lifecycle.md is missing")
    if not PREDICTION_OUTPUT_NATIVE_PLAN.exists():
        errors.append("docs/plans/2026-06-26-prediction-output-native-contract.md is missing")

    plans = sorted(DOCS_PLANS.glob("*.md")) if DOCS_PLANS.exists() else []
    if not plans:
        errors.append("docs/plans must contain at least one completed plan")

    for plan_path in plans:
        plan = plan_path.read_text(encoding="utf-8")
        if "Status: Completed" not in plan or "make check" not in plan:
            errors.append(f"{plan_path.relative_to(ROOT)} must record completed status and make check verification")

    if FINITE_PREDICTIONS_PLAN.exists():
        finite_plan = FINITE_PREDICTIONS_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "repository and external-directory `make check` passed",
            "hostile finite-prediction mutations were rejected",
        ):
            if evidence not in finite_plan:
                errors.append(f"{FINITE_PREDICTIONS_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}")

    if OUTPUT_DTYPE_PLAN.exists():
        dtype_plan = OUTPUT_DTYPE_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory `make check` passed",
            "hostile model-output dtype mutations were rejected",
        ):
            if evidence not in dtype_plan:
                errors.append(f"{OUTPUT_DTYPE_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}")

    if CREDENTIAL_FIXTURE_PLAN.exists():
        fixture_plan = CREDENTIAL_FIXTURE_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory `make check` passed",
            "hostile credential-fixture mutations were rejected",
            "protected fixture path and digest remained unchanged",
            "generated-artifact and credential-pattern audits passed",
        ):
            if evidence not in fixture_plan:
                errors.append(
                    f"{CREDENTIAL_FIXTURE_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )

    if PREDICTION_OUTPUT_NATIVE_PLAN.exists():
        output_plan = PREDICTION_OUTPUT_NATIVE_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "Prediction output tests passed",
            "prediction output mutation tests passed (5 mutations rejected)",
            "Makefile root tests passed: 35 executed target/authority cases",
            "xcodebuild not found; static project checks completed",
            "make check",
        ):
            if evidence not in output_plan:
                errors.append(
                    f"{PREDICTION_OUTPUT_NATIVE_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )

    if PREDICTION_RANGE_PLAN.exists():
        range_plan = PREDICTION_RANGE_PLAN.read_text(encoding="utf-8")
        for evidence in (
            "Status: Completed",
            "repository and external-directory `make check` passed",
            "hostile model-prediction range mutations were rejected",
            "generated-artifact and credential-pattern audits passed",
        ):
            if evidence not in range_plan:
                errors.append(
                    f"{PREDICTION_RANGE_PLAN.relative_to(ROOT)} must record verification evidence: {evidence}"
                )

    for relative_path in ("README.md", "SECURITY.md", "VISION.md", "CHANGES.md"):
        document = re.sub(r"\s+", " ", read_text(relative_path)).lower()
        if "sampling coordinate arithmetic" not in document:
            errors.append(f"{relative_path} must document sampling coordinate arithmetic")
        if "finite model predictions" not in document:
            errors.append(f"{relative_path} must document finite model predictions")
        if "model output dtype validation" not in document:
            errors.append(f"{relative_path} must document model output dtype validation")
        if "reviewed upstream credential fixture" not in document:
            errors.append(f"{relative_path} must document the reviewed upstream credential fixture")
        if "model prediction range validation" not in document:
            errors.append(f"{relative_path} must document model prediction range validation")

    if TOOLCHAIN_MODEL_GUIDE.exists():
        guide = TOOLCHAIN_MODEL_GUIDE.read_text(encoding="utf-8")
        for contract in (
            "TensorFlow v0.12.0",
            "TensorFlow 0.12.head",
            "Xcode 7.3 or later",
            "Xcode 8.2-era project metadata",
            "iOS 9.2",
            "build_all_ios.sh",
            "libtensorflow-core.a",
            "libprotobuf.a",
            "libprotobuf-lite.a",
            "inception5h.zip",
            "d13569f6a98159de37e92e9c8ec4dae8f674fbf475f69fe6199b514f756d4364",
            "The exact original TensorFlow commit is not recorded",
        ):
            if contract not in guide:
                errors.append(f"toolchain and model guide must preserve: {contract}")

    readme = read_text("README.md")
    if "docs/toolchain-and-model-assets.md" not in readme:
        errors.append("README must link the toolchain and model asset guide")
    if "`CameraExample` target" not in readme:
        errors.append("README must name the CameraExample Xcode target")
    if "Document exact build tool versions and model download expectations" in read_text("VISION.md"):
        errors.append("VISION must not retain the completed toolchain documentation priority")

    return errors


def ci_checks():
    errors = []
    if not CI_WORKFLOW.exists():
        return [".github/workflows/check.yml is missing"]

    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    errors.extend(f"CI workflow must {requirement}" for requirement in validate_workflow(workflow))

    readme = read_text("README.md")
    if "GitHub Actions" not in readme:
        errors.append("README must document the GitHub Actions check")

    return errors


def resource_checks():
    errors = []
    for relative_path, expected_hash in RESOURCE_SHA256.items():
        resource_path = ROOT / relative_path
        if not resource_path.is_file():
            errors.append(f"resource is missing: {relative_path}")
            continue
        digest = hashlib.sha256()
        with resource_path.open("rb") as resource:
            for chunk in iter(lambda: resource.read(1024 * 1024), b""):
                digest.update(chunk)
        actual_hash = digest.hexdigest()
        if actual_hash != expected_hash:
            errors.append(
                f"resource hash mismatch for {relative_path}: expected {expected_hash}, got {actual_hash}"
            )
    return errors


def file_contains_private_key_marker(path):
    overlap = b""
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            candidate = overlap + chunk
            if any(marker in candidate for marker in PRIVATE_KEY_PEM_MARKERS):
                return True
            overlap = candidate[-PRIVATE_KEY_MARKER_OVERLAP:]
    return False


def credential_fixture_checks():
    errors = []
    fixture_path = ROOT / CREDENTIAL_FIXTURE
    if not fixture_path.is_file():
        return [f"reviewed upstream credential fixture is missing: {CREDENTIAL_FIXTURE}"]

    actual_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
    if actual_hash != CREDENTIAL_FIXTURE_SHA256:
        errors.append(
            f"reviewed upstream credential fixture hash mismatch: expected "
            f"{CREDENTIAL_FIXTURE_SHA256}, got {actual_hash}"
        )

    try:
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        errors.append(f"reviewed upstream credential fixture must be valid UTF-8 JSON: {error}")
        fixture = {}
    if not isinstance(fixture, dict):
        errors.append("reviewed upstream credential fixture must be a JSON object")
        fixture = {}

    expected_metadata = {
        "type": "service_account",
        "project_id": "fake_project_id",
        "private_key_id": "fake_key_id",
        "client_email": "fake-test-project.iam.gserviceaccount.com",
    }
    for key, expected_value in expected_metadata.items():
        if fixture.get(key) != expected_value:
            errors.append(
                f"reviewed upstream credential fixture must retain fake {key}: {expected_value}"
            )

    marker_paths = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative_path = path.relative_to(ROOT)
        if ".git" in relative_path.parts:
            continue
        try:
            contains_marker = file_contains_private_key_marker(path)
        except OSError as error:
            errors.append(f"unable to inspect repository file for private-key markers: {relative_path}: {error}")
            continue
        if contains_marker:
            marker_paths.append(relative_path.as_posix())

    unexpected_paths = sorted(set(marker_paths) - {CREDENTIAL_FIXTURE})
    for relative_path in unexpected_paths:
        errors.append(f"unreviewed private-key marker found in repository file: {relative_path}")
    if CREDENTIAL_FIXTURE not in marker_paths:
        errors.append("reviewed upstream credential fixture must remain the sole key-shaped test asset")

    return errors


def project_checks():
    errors = (
        docs_plan_checks()
        + require_paths()
        + ci_checks()
        + resource_checks()
        + credential_fixture_checks()
    )
    if errors:
        return errors

    info = read_text("app/Info.plist")
    if "NSCameraUsageDescription" not in info:
        errors.append("Info.plist must include NSCameraUsageDescription")

    project = read_text("app/tensorflow_camera.xcodeproj/project.pbxproj")
    for fragment in (
        "tensorflow_camera",
        "IPHONEOS_DEPLOYMENT_TARGET = 9.2;",
        "PRODUCT_BUNDLE_IDENTIFIER = com.gpj.Camera;",
    ):
        if fragment not in project:
            errors.append(f"project is missing expected setting: {fragment}")

    makefile = read_text("Makefile")
    root_declaration = "override ROOT := $(shell path='$(subst ','\"'\"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' \"$$path\" | /usr/bin/sed 's/^ //'); [ -f \"$$path\" ] || exit 1; directory=$$(/usr/bin/dirname -- \"$$path\"); CDPATH= cd -- \"$$directory\" && /bin/pwd -P)"
    root_assignments = re.findall(r"^(?:override\s+)?ROOT\s*[:+?]?=", makefile, re.MULTILINE)
    if len(root_assignments) != 1 or makefile.count(root_declaration) != 1:
        errors.append("Makefile must contain exactly one protected repository-root declaration")
    tool_contracts = (
        "PYTHON ?= python3",
        "CXX ?= c++",
        "XCODEBUILD ?= xcodebuild",
        "override PYTHON := $(value PYTHON)",
        "override CXX := $(value CXX)",
        "override XCODEBUILD := $(value XCODEBUILD)",
        "export PYTHON CXX XCODEBUILD",
        "override SHELL := /bin/sh",
        "override .SHELLFLAGS := -c",
    )
    if any(makefile.count(contract) != 1 for contract in tool_contracts) or max(makefile.index(contract) for contract in tool_contracts) > makefile.index(root_declaration):
        errors.append("Makefile must keep tool overrides before the protected repository root")
    if '"$$PYTHON" "$$ROOT/scripts/test_credential_fixture_policy.py"' not in makefile:
        errors.append("Makefile contract-test must run the credential fixture policy tests")
    if 'CXX="$$CXX" "$$ROOT/scripts/run-prediction-range-tests.sh"' not in makefile:
        errors.append("Makefile test must execute the model prediction range tests")
    if 'CXX="$$CXX" "$$ROOT/scripts/run-prediction-output-tests.sh"' not in makefile:
        errors.append("Makefile test must execute the model prediction output tests")
    if 'CXX="$$CXX" "$$PYTHON" "$$ROOT/scripts/test_prediction_output_mutations.py"' not in makefile:
        errors.append("Makefile test must execute model prediction output mutations")
    if 'CXX="$$CXX" "$$ROOT/scripts/run-frame-preprocessing-tests.sh"' not in makefile:
        errors.append("Makefile test must execute frame preprocessing tests")
    if 'CXX="$$CXX" "$$PYTHON" "$$ROOT/scripts/test_frame_preprocessing_mutations.py"' not in makefile:
        errors.append("Makefile test must execute frame preprocessing mutations")
    for fragment in (
        ".DEFAULT_GOAL := check",
        ".PHONY: __repository-make-authority build check contract-test lint root-test test verify",
        ".SECONDEXPANSION:",
        "$(error MAKEFLAGS must not be overridden for repository verification)",
        "$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)",
        "$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)",
        "$(error MAKEFILE_LIST must not be overridden)",
        "build: lint",
        "verify: root-test lint contract-test test build",
        "check: verify",
        '"$$ROOT/scripts/check-ios-camera-source.py"',
        '"$$ROOT/scripts/test_workflow_contract.py"',
        '"$$ROOT/scripts/run-prediction-range-tests.sh"',
        '"$$ROOT/scripts/run-prediction-output-tests.sh"',
        '"$$ROOT/scripts/test_prediction_output_mutations.py"',
        '"$$ROOT/scripts/run-frame-preprocessing-tests.sh"',
        '"$$ROOT/scripts/test_frame_preprocessing_mutations.py"',
        '"$$ROOT/scripts/run-ios-build.sh"',
        '"$$ROOT/scripts/test-makefile-root.sh"',
    ):
        if fragment not in makefile:
            errors.append(f"Makefile is missing root-independent fragment: {fragment}")

    if "docs/plans/2026-06-14-make-root-override-protection.md" not in read_text("README.md"):
        errors.append("README must index Make root override protection evidence")
    if "docs/plans/2026-06-21-make-authority-isolation.md" not in read_text("README.md"):
        errors.append("README must index Make authority isolation evidence")
    if "docs/plans/2026-06-14-finite-model-predictions.md" not in read_text("README.md"):
        errors.append("README must index finite model prediction evidence")
    if "docs/plans/2026-06-14-model-output-dtype-validation.md" not in read_text("README.md"):
        errors.append("README must index model output dtype validation evidence")
    if "docs/plans/2026-06-15-upstream-credential-fixture-provenance.md" not in read_text("README.md"):
        errors.append("README must index upstream credential fixture provenance evidence")
    if "docs/plans/2026-06-17-model-prediction-range-validation.md" not in read_text("README.md"):
        errors.append("README must index model prediction range validation evidence")
    if "docs/plans/2026-06-19-frame-preprocessing-native-contract.md" not in read_text("README.md"):
        errors.append("README must index frame preprocessing native evidence")
    if "docs/plans/2026-06-26-prediction-output-native-contract.md" not in read_text("README.md"):
        errors.append("README must index prediction output native evidence")

    runner = ROOT / "scripts" / "run-prediction-range-tests.sh"
    if runner.exists() and not runner.stat().st_mode & 0o111:
        errors.append("model prediction range test runner must be executable")
    output_runner = ROOT / "scripts" / "run-prediction-output-tests.sh"
    if output_runner.exists() and not output_runner.stat().st_mode & 0o111:
        errors.append("model prediction output test runner must be executable")
    root_test_source = read_text("scripts/test-makefile-root.sh")
    if "run-prediction-output-tests.sh" not in root_test_source:
        errors.append("Make-root isolation must stub the prediction output runner")
    frame_runner = ROOT / "scripts" / "run-frame-preprocessing-tests.sh"
    if frame_runner.exists() and not frame_runner.stat().st_mode & 0o111:
        errors.append("frame preprocessing test runner must be executable")
    ios_build_runner = ROOT / "scripts" / "run-ios-build.sh"
    if ios_build_runner.exists() and not ios_build_runner.stat().st_mode & 0o111:
        errors.append("iOS build runner must be executable")
    if ios_build_runner.exists():
        ios_build = ios_build_runner.read_text(encoding="utf-8")
        for fragment in (
            'mktemp -d "${TMPDIR:-/tmp}/tensorflow-camera-xcodebuild.XXXXXX"',
            "trap 'rm -rf \"$TEMP_DIR\"' EXIT HUP INT TERM",
            '"$ROOT/app/tensorflow_camera.xcodeproj"',
            "-target CameraExample",
            'OBJROOT="$TEMP_DIR/obj"',
            'SYMROOT="$TEMP_DIR/products"',
            'SHARED_PRECOMPS_DIR="$TEMP_DIR/precompiled"',
        ):
            if fragment not in ios_build:
                errors.append(f"iOS build runner isolation is missing: {fragment}")

    return errors


def behavior_checks():
    errors = require_paths()
    if errors:
        return errors

    source = read_text("app/CameraExampleViewController.mm")
    header_source = read_text("app/CameraExampleViewController.h")
    utils_source = read_text("app/tensorflow_utils.mm")
    validation_source = read_text("app/prediction_validation.h")
    validation_test = read_text("tests/prediction_validation_test.cc")
    validation_runner = read_text("scripts/run-prediction-range-tests.sh")
    output_source = read_text("app/prediction_output.h")
    output_test = read_text("tests/prediction_output_test.cc")
    output_runner = read_text("scripts/run-prediction-output-tests.sh")
    output_mutations = read_text("scripts/test_prediction_output_mutations.py")
    frame_source = read_text("app/frame_preprocessing.h")
    frame_test = read_text("tests/frame_preprocessing_test.cc")
    frame_runner = read_text("scripts/run-frame-preprocessing-tests.sh")
    frame_mutations = read_text("scripts/test_frame_preprocessing_mutations.py")
    lifecycle_contracts = [
        "captureRequested = YES;",
        "viewIsVisible = YES;",
        "viewIsVisible = NO;",
        "UIApplicationWillResignActiveNotification",
        "UIApplicationDidBecomeActiveNotification",
        "- (void)updateCaptureRunningState",
        "captureRequested && viewIsVisible",
        "applicationIsActive",
        "[[NSNotificationCenter defaultCenter] removeObserver:self];",
    ]
    for contract in lifecycle_contracts:
        if contract not in source:
            errors.append("camera active-screen lifecycle contract is missing: " + contract)
    for declaration in (
        "BOOL captureRequested;",
        "BOOL viewIsVisible;",
        "BOOL applicationIsActive;",
    ):
        if declaration not in header_source:
            errors.append("camera lifecycle state is missing from the controller: " + declaration)
    setup_start = source.find("- (void)setupAVCapture {", source.find("@implementation"))
    setup_end = source.find("- (void)updateCaptureRunningState", setup_start)
    if min(setup_start, setup_end) < 0:
        errors.append("camera setup lifecycle boundary is missing")
    if "[session startRunning];" in source[setup_start:setup_end]:
        errors.append("camera setup must not start capture before the view is active")
    update_start = source.find("- (void)updateCaptureRunningState {", setup_start)
    update_end = source.find("- (void)applicationDidBecomeActive:", update_start)
    update_source = source[update_start:update_end]
    for contract in (
        "captureRequested && viewIsVisible && applicationIsActive",
        "[session startRunning];",
        "[session stopRunning];",
    ):
        if contract not in update_source:
            errors.append("camera running-state gate is incomplete: " + contract)
    lifecycle_methods = (
        ("- (void)applicationDidBecomeActive:", "applicationIsActive = YES;"),
        ("- (void)applicationWillResignActive:", "applicationIsActive = NO;"),
        ("- (void)viewWillAppear:", "viewIsVisible = YES;"),
        ("- (void)viewWillDisappear:", "viewIsVisible = NO;"),
    )
    for method, assignment in lifecycle_methods:
        method_start = source.find(method, source.find("@implementation"))
        update_call = source.find("[self updateCaptureRunningState];", method_start)
        assignment_position = source.find(assignment, method_start)
        next_method = source.find("\n- (", method_start + 1)
        if min(method_start, assignment_position, update_call, next_method) < 0 or not (
            method_start < assignment_position < update_call < next_method
        ):
            errors.append("camera lifecycle state must update before capture reconciliation: " + method)
    freeze_start = source.find("- (IBAction)takePicture")
    freeze_end = source.find("+ (CGRect)videoPreviewBoxForGravity")
    if "if ([session isRunning])" in source[freeze_start:freeze_end]:
        errors.append("freeze intent must not depend on app-driven capture suspension")
    freeze_source = source[freeze_start:freeze_end]
    for assignment in ("captureRequested = NO;", "captureRequested = YES;"):
        assignment_position = freeze_source.find(assignment)
        update_call = freeze_source.find("[self updateCaptureRunningState];", assignment_position)
        if assignment_position < 0 or update_call < assignment_position:
            errors.append("freeze intent must be recorded before capture reconciliation: " + assignment)
    dealloc_start = source.find("- (void)dealloc")
    teardown_call = source.find("[self teardownAVCapture];", dealloc_start)
    observer_removal = source.find(
        "[[NSNotificationCenter defaultCenter] removeObserver:self];",
        dealloc_start,
    )
    if min(dealloc_start, observer_removal, teardown_call) < 0 or not (
        dealloc_start < observer_removal < teardown_call
    ):
        errors.append("camera controller must remove app lifecycle observers before teardown")
    teardown_match = re.search(r"- \(void\)teardownAVCapture \{(.*?)\n\}", source, re.DOTALL)
    if not teardown_match:
        errors.append("camera controller teardown method is missing")
    else:
        teardown = teardown_match.group(1)
        teardown_contract = (
            "[session stopRunning];",
            "[videoDataOutput setSampleBufferDelegate:nil queue:NULL];",
            "[self drainVideoDataOutputQueue];",
            "[videoDataOutput release];",
            "dispatch_release(videoDataOutputQueue);",
            "[previewLayer release];",
            "[session release];",
            "session = nil;",
        )
        positions = [teardown.find(fragment) for fragment in teardown_contract]
        if any(position < 0 for position in positions):
            errors.append("camera teardown must stop capture, detach callbacks, release resources, and clear session")
        elif positions != sorted(positions):
            errors.append("camera teardown must detach, drain, and release capture resources in lifecycle order")
    if "static char VideoDataOutputQueueKey;" not in source:
        errors.append("video callback queue must have private queue-specific identity")
    queue_create = 'dispatch_queue_create("VideoDataOutputQueue", DISPATCH_QUEUE_SERIAL);'
    queue_identity = "dispatch_queue_set_specific(videoDataOutputQueue, &VideoDataOutputQueueKey,"
    queue_delegate = "[videoDataOutput setSampleBufferDelegate:self queue:videoDataOutputQueue];"
    queue_setup_positions = [source.find(fragment) for fragment in (queue_create, queue_identity, queue_delegate)]
    if any(position < 0 for position in queue_setup_positions):
        errors.append("video callback queue must create, identify, and then install its delegate")
    elif queue_setup_positions != sorted(queue_setup_positions):
        errors.append("video callback queue must register identity before delegate installation")
    drain_match = re.search(r"- \(void\)drainVideoDataOutputQueue \{(.*?)\n\}", source, re.DOTALL)
    if not drain_match:
        errors.append("camera controller callback-drain helper is missing")
    else:
        drain = drain_match.group(1)
        if "!videoDataOutputQueue" not in drain:
            errors.append("callback drain must tolerate a missing video queue")
        if "dispatch_get_specific(&VideoDataOutputQueueKey)" not in drain:
            errors.append("callback drain must identify execution on the video queue")
        if "dispatch_get_specific(&VideoDataOutputQueueKey) ==" not in drain:
            errors.append("callback drain must skip synchronization on the video queue itself")
        if "dispatch_sync(videoDataOutputQueue, ^{});" not in drain:
            errors.append("callback drain must wait for already-enqueued video work")
    if source.count("[videoDataOutput setSampleBufferDelegate:nil queue:NULL];") < 2:
        errors.append("camera setup failure and teardown must both detach the video sample delegate")
    if "AVCaptureStillImageIsCapturingStillImageContext" not in source:
        errors.append("still-image KVO context is missing")
    if 'forKeyPath:@"capturingStillImage"' not in source:
        errors.append("still-image output must observe capturingStillImage")
    if 'removeObserver:self forKeyPath:@"capturingStillImage"' not in source:
        errors.append("still-image output must remove the same KVO key path it observes")
    if re.search(r'removeObserver:self\s+forKeyPath:@"isCapturingStillImage"', source):
        errors.append("teardown must not remove the stale isCapturingStillImage key path")
    for fragment in (
        "assert(error == nil)",
        "assert(pixelBuffer != NULL)",
        "assert(false)",
        "assert(image_channels >= wanted_input_channels)",
    ):
        if fragment in source:
            errors.append(f"camera controller must not crash with {fragment}")
    if "showCaptureErrorWithTitle" not in source:
        errors.append("camera setup must surface setup failures without assertions")
    if "if (!device)" not in source:
        errors.append("camera setup must handle missing capture devices")
    if "if (error || !deviceInput)" not in source:
        errors.append("camera setup must handle failed capture input creation")
    if "- (void)failCameraSetupWithMessage:(NSString *)message" not in source:
        errors.append("camera setup must centralize output failure cleanup")
    if 'Could not add the still image output.' not in source:
        errors.append("camera setup must fail closed when still image output cannot be added")
    if 'Could not add the video data output.' not in source:
        errors.append("camera setup must fail closed when video data output cannot be added")
    if 'AVCaptureConnection *videoConnection =\n      [videoDataOutput connectionWithMediaType:AVMediaTypeVideo];' not in source:
        errors.append("camera setup must store the video data connection before enabling it")
    if 'if (!videoConnection)' not in source:
        errors.append("camera setup must handle missing video data connections")
    if 'Could not create a video data connection.' not in source:
        errors.append("camera setup must show an error for missing video data connections")
    if '[[videoDataOutput connectionWithMediaType:AVMediaTypeVideo] setEnabled:YES]' in source:
        errors.append("camera setup must not enable an unchecked video data connection")
    if "AVCaptureSession *captureSession = [previewLayer session];" not in source:
        errors.append("camera switching must guard the active preview capture session")
    if "if (!captureSession)" not in source:
        errors.append("camera switching must handle missing capture sessions")
    if "if (!session)" not in source:
        errors.append("camera freeze/resume action must handle missing capture sessions")
    if 'message:@"Camera capture is not available."' not in source:
        errors.append("camera freeze/resume action must surface missing capture sessions")
    if "deviceInputWithDevice:d error:nil" in source:
        errors.append("camera switching must not ignore capture input creation errors")
    if "if (error || !input)" not in source:
        errors.append("camera switching must handle failed replacement input creation")
    if "BOOL didSwitchCamera = NO;" not in source or "if (!didSwitchCamera)" not in source:
        errors.append("camera switching must only toggle state after a successful switch")
    if "NSArray *oldInputs = [NSArray arrayWithArray:[captureSession inputs]];" not in source:
        errors.append("camera switching must preserve old inputs while reconfiguring")
    if "[captureSession canAddInput:input]" not in source:
        errors.append("camera switching must verify the replacement input can be added")
    if "[[previewLayer session] addInput:input]" in source:
        errors.append("camera switching must not add replacement inputs without guard checks")
    if "Unsupported pixel format:" not in source:
        errors.append("frame preprocessing must log unsupported pixel formats")
    if "CVPixelBufferLockBaseAddress(pixelBuffer, 0) != kCVReturnSuccess" not in source:
        errors.append("frame preprocessing must handle pixel buffer lock failures")
    if "CVPixelBufferUnlockBaseAddress(pixelBuffer, 0);" not in source:
        errors.append("frame preprocessing must unlock locked pixel buffers")
    if "#include <limits.h>" not in source:
        errors.append("frame preprocessing must retain the native dimension bound")
    for fragment in (
        "const size_t sourceRowBytes = CVPixelBufferGetBytesPerRow(pixelBuffer);",
        "const size_t sourceWidth = CVPixelBufferGetWidth(pixelBuffer);",
        "const size_t sourceFullHeight = CVPixelBufferGetHeight(pixelBuffer);",
        "const size_t sourceDataSize = CVPixelBufferGetDataSize(pixelBuffer);",
        "CVPixelBufferIsPlanar(pixelBuffer)",
        "sourceFullHeight > INT_MAX",
        "tensorflow_camera::BuildFrameLayout(",
        "tensorflow_camera::SourcePixelOffset(",
        "tensorflow_camera::SourceChannelOffset(",
        'LOG(ERROR) << "Invalid pixel buffer geometry";',
        'LOG(ERROR) << "Invalid pixel buffer sampling arithmetic";',
    ):
        if fragment not in source:
            errors.append(f"frame preprocessing geometry contract is missing: {fragment}")
    if "const int sourceRowBytes =" in source:
        errors.append("frame preprocessing must not truncate the Core Video row stride")
    geometry_guard = source.find("tensorflow_camera::BuildFrameLayout(")
    pixel_lock = source.find("CVPixelBufferLockBaseAddress(pixelBuffer, 0)")
    if geometry_guard < 0 or pixel_lock < 0 or geometry_guard > pixel_lock:
        errors.append("frame preprocessing must validate geometry before locking frame memory")
    if "const int in_x" in source or "const int in_y" in source:
        errors.append("frame preprocessing must not narrow source sampling coordinates to int")
    if "(x * image_width)" in source or "(y * image_height)" in source:
        errors.append("frame preprocessing must not multiply sampling coordinates as signed int")
    for fragment in (
        "inline bool CheckedMultiply",
        "inline bool CheckedAdd",
        "final_offset >= data_size",
        "source_offset > layout.data_size - 4",
        "output_channel >= 3",
        "*source_channel = output_channel + 1;",
        "*source_channel = 2 - output_channel;",
    ):
        if fragment not in frame_source:
            errors.append(f"frame preprocessing helper contract is missing: {fragment}")
    for fragment in (
        "landscape frames use a centered square crop",
        "portrait frames use a centered square crop",
        "BGRA input is published to TensorFlow as RGB",
        "ARGB input skips alpha and publishes RGB",
        "truncated backing storage is rejected",
        "overflowing resize products are rejected",
        "unsupported output channels are rejected",
    ):
        if fragment not in frame_test:
            errors.append(f"frame preprocessing native test is missing: {fragment}")
    for fragment in (
        '"${CXX:-c++}" -std=c++11 -Wall -Wextra -Werror',
        '"$ROOT/tests/frame_preprocessing_test.cc"',
        '"$TEMP_DIR/frame_preprocessing_test"',
        "trap 'rm -rf \"$TEMP_DIR\"' EXIT HUP INT TERM",
    ):
        if fragment not in frame_runner:
            errors.append(f"frame preprocessing test runner is missing: {fragment}")
    for fragment in (
        "BGRA red/blue swap",
        "ARGB alpha exposure",
        "landscape crop removal",
        "portrait crop removal",
        "backing-size check removal",
        "resize overflow check removal",
    ):
        if fragment not in frame_mutations:
            errors.append(f"frame preprocessing mutation is missing: {fragment}")
    if "&outputs[0]" in source:
        errors.append("model output handling must not assume outputs[0] exists")
    if "outputs.empty()" not in source:
        errors.append("model output handling must guard empty output tensors")
    if "labels.empty()" not in source:
        errors.append("model output handling must guard empty label lists")
    if "labels[index % predictions.size()]" in source:
        errors.append("model output handling must not index labels by prediction count modulo")
    if "const size_t result_count" not in source:
        errors.append("model output handling must bound iteration by labels and predictions")
    if "stringWithCString:label.c_str()" in source:
        errors.append("model labels must not use unchecked legacy C-string conversion")
    if "stringWithUTF8String:prediction.label.c_str()" not in source:
        errors.append("model labels must use explicit UTF-8 conversion")
    if "if (!labelObject)" not in source:
        errors.append("model label rendering must reject failed string conversion")
    if "Skipping invalid UTF-8 model label" not in source:
        errors.append("model label rendering must log skipped invalid labels")
    if "if (output->dtype() != tensorflow::DT_FLOAT)" not in source:
        errors.append("model output handling must reject non-float prediction tensors")
    if "Skipping model output with unexpected dtype" not in source:
        errors.append("model output handling must log skipped non-float tensors")
    dtype_guard = source.find("if (output->dtype() != tensorflow::DT_FLOAT)")
    typed_flatten = source.find("output->flat<float>()")
    if dtype_guard < 0 or typed_flatten < 0 or dtype_guard > typed_flatten:
        errors.append("model output handling must validate dtype before typed tensor access")
    if "#include <cmath>" not in source:
        errors.append("model output handling must include the finite-value predicate")
    if "if (!std::isfinite(predictionValue))" not in source:
        errors.append("model output handling must reject non-finite prediction values")
    if "Skipping non-finite model prediction" not in source:
        errors.append("model output handling must log skipped non-finite predictions")
    finite_guard = source.find("if (!std::isfinite(predictionValue))")
    selector_call = source.find("tensorflow_camera::SelectLabeledPredictions(")
    number_creation = source.find("[NSNumber numberWithFloat:prediction.value]")
    if finite_guard < 0 or number_creation < 0 or finite_guard > number_creation:
        errors.append("model output handling must reject non-finite predictions before NSNumber creation")
    for fragment in (
        "inline bool IsValidModelPrediction(float value)",
        "return value >= 0.0f && value <= 1.0f;",
    ):
        if fragment not in validation_source:
            errors.append(f"model prediction range helper is missing: {fragment}")
    for fragment in (
        'ExpectValidation(0.0f, true, "zero is a valid inclusive endpoint")',
        'ExpectValidation(1.0f, true, "one is a valid inclusive endpoint")',
        'ExpectValidation(-0.01f, false, "negative predictions are rejected")',
        'ExpectValidation(1.01f, false, "predictions above one are rejected")',
        "std::numeric_limits<float>::max()",
        "std::numeric_limits<float>::quiet_NaN()",
        'Prediction range tests passed',
    ):
        if fragment not in validation_test:
            errors.append(f"model prediction range executable test is missing: {fragment}")
    for fragment in (
        '"${CXX:-c++}" -std=c++11 -Wall -Wextra -Werror',
        '"$ROOT/tests/prediction_validation_test.cc"',
        '"$TEMP_DIR/prediction_validation_test"',
        "trap 'rm -rf \"$TEMP_DIR\"' EXIT HUP INT TERM",
    ):
        if fragment not in validation_runner:
            errors.append(f"model prediction range test runner is missing: {fragment}")
    for fragment in (
        "struct LabeledPrediction",
        "inline std::vector<LabeledPrediction> SelectLabeledPredictions(",
        "const size_t result_count",
        "!std::isfinite(value)",
        "!IsValidModelPrediction(value)",
        "value <= threshold",
        "labels[index]",
    ):
        if fragment not in output_source:
            errors.append(f"model prediction output helper is missing: {fragment}")
    for fragment in (
        'const std::vector<std::string> labels = {"cat", "dog", "bird"};',
        "only scores above the threshold are selected",
        "selection respects the shorter label vector",
        "non-finite and out-of-range scores are excluded",
        "non-finite thresholds fail closed",
        "Prediction output tests passed",
    ):
        if fragment not in output_test:
            errors.append(f"model prediction output executable test is missing: {fragment}")
    for fragment in (
        '"${CXX:-c++}" -std=c++11 -Wall -Wextra -Werror',
        '"$ROOT/tests/prediction_output_test.cc"',
        '"$TEMP_DIR/prediction_output_test"',
        "trap 'rm -rf \"$TEMP_DIR\"' EXIT HUP INT TERM",
    ):
        if fragment not in output_runner:
            errors.append(f"model prediction output test runner is missing: {fragment}")
    for fragment in (
        "inclusive threshold",
        "label bound",
        "prediction range",
        "label association",
        "finite threshold",
    ):
        if fragment not in output_mutations:
            errors.append(f"model prediction output mutation is missing: {fragment}")
    range_call = "if (!tensorflow_camera::IsValidModelPrediction(predictionValue))"
    if '#include "prediction_validation.h"' not in source:
        errors.append("camera controller must include shared model prediction range validation")
    if range_call not in source:
        errors.append("camera controller must reject out-of-range model predictions")
    if "Skipping out-of-range model prediction" not in source:
        errors.append("camera controller must log skipped out-of-range model predictions")
    if '#include "prediction_output.h"' not in source:
        errors.append("camera controller must include shared model prediction output selection")
    if selector_call < 0:
        errors.append("camera controller must use shared model prediction output selection")
    range_guard = source.find(range_call)
    if min(finite_guard, range_guard, selector_call, number_creation) < 0 or not (
        finite_guard < range_guard < selector_call < number_creation
    ):
        errors.append(
            "model prediction validation must precede shared selection and Objective-C publication"
        )
    if 'LOG(FATAL) << "Couldn\'t load model' in source:
        errors.append("model load failures must not crash with LOG(FATAL)")
    if 'LOG(FATAL) << "Couldn\'t load labels' in source:
        errors.append("label load failures must not crash with LOG(FATAL)")
    if 'showCaptureErrorWithTitle:@"Model Unavailable"' not in source:
        errors.append("model load failures must show a user-visible error")
    if 'showCaptureErrorWithTitle:@"Labels Unavailable"' not in source:
        errors.append("label load failures must show a user-visible error")
    if "[synth release];" not in source:
        errors.append("camera controller must release the retained speech synthesizer")
    if "[labelLayers release];" not in source:
        errors.append("camera controller must release retained prediction label layers")
    if "[square release];\n  [synth release];\n  [labelLayers release];\n  [oldPredictionValues release];" not in source:
        errors.append("camera controller dealloc must release retained prediction values")
    if "oldPredictionValues = nil;" not in source:
        errors.append("viewDidUnload must nil out released prediction values")
    if "LOG(FATAL)" in utils_source:
        errors.append("TensorFlow utility resource lookups must not use LOG(FATAL)")
    if "LOG(ERROR) << \"Couldn't find '\"" not in utils_source:
        errors.append("missing bundle resources must be logged as non-fatal errors")
    if "if (!network_path)" not in utils_source:
        errors.append("memory-mapped model loading must guard missing bundle resources")
    if utils_source.count("std::unique_ptr<tensorflow::Session> new_session(session_pointer);") != 2:
        errors.append("TensorFlow model loading must own new sessions transactionally")
    if utils_source.count("session->reset(new_session.release());") != 2:
        errors.append("TensorFlow model loading must publish sessions only after graph creation")
    if "std::unique_ptr<tensorflow::MemmappedEnv> new_memmapped_env(" not in utils_source:
        errors.append("memory-mapped model loading must own its environment transactionally")
    if "memmapped_env->reset(new_memmapped_env.release());" not in utils_source:
        errors.append("memory-mapped model loading must publish its environment only after graph creation")
    if "if (!t.is_open())" not in utils_source:
        errors.append("label loading must fail when the labels file cannot be opened")
    if "Failed to open labels file" not in utils_source:
        errors.append("label loading must log failed labels file opens")
    if "while (std::getline(t, line))" not in utils_source:
        errors.append("label loading must iterate over successfully read lines")
    if "if (!line.empty())" not in utils_source:
        errors.append("label loading must skip empty labels")

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("project", "behavior"), required=True)
    args = parser.parse_args()

    errors = project_checks() if args.mode == "project" else behavior_checks()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"{args.mode} checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
