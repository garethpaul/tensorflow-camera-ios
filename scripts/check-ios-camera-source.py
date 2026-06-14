#!/usr/bin/env python3
import argparse
import hashlib
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
FINITE_PREDICTIONS_PLAN = DOCS_PLANS / "2026-06-14-finite-model-predictions.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "check.yml"
RESOURCE_SHA256 = {
    "app/data/tensorflow_inception_graph.pb": "a39b08b826c9d5a5532ff424c03a3a11a202967544e389aca4b06c2bd8aef63f",
    "app/data/imagenet_comp_graph_label_strings.txt": "da2a31ecfe9f212ae8dd07379b11a74cb2d7a110eba12c5fc8c862a65b8e6606",
    "app/data/grace_hopper.jpg": "e1f57e98cf38076c0f9a058d74ffddf90f20453e436033784606b63c8ed2e49a",
}


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def require_paths():
    errors = []
    for relative_path in (
        "app/tensorflow_camera.xcodeproj/project.pbxproj",
        "app/Info.plist",
        "app/CameraExampleViewController.mm",
        "app/CameraExampleAppDelegate.m",
        "app/data/tensorflow_inception_graph.pb",
        "app/data/imagenet_comp_graph_label_strings.txt",
        "app/data/grace_hopper.jpg",
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
    if not FINITE_PREDICTIONS_PLAN.exists():
        errors.append("docs/plans/2026-06-14-finite-model-predictions.md is missing")

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

    for relative_path in ("README.md", "SECURITY.md", "VISION.md", "CHANGES.md"):
        if "sampling coordinate arithmetic" not in read_text(relative_path).lower():
            errors.append(f"{relative_path} must document sampling coordinate arithmetic")
        if "finite model predictions" not in read_text(relative_path).lower():
            errors.append(f"{relative_path} must document finite model predictions")

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


def project_checks():
    errors = docs_plan_checks() + require_paths() + ci_checks() + resource_checks()
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
    root_declaration = "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))"
    root_assignments = re.findall(r"^(?:override\s+)?ROOT\s*[:+?]?=", makefile, re.MULTILINE)
    if len(root_assignments) != 1 or makefile.count(root_declaration) != 1:
        errors.append("Makefile must contain exactly one protected repository-root declaration")
    tool_and_root_block = "\n".join((
        "PYTHON ?= python3",
        "XCODEBUILD ?= xcodebuild",
        root_declaration,
    ))
    if makefile.count(tool_and_root_block) != 1:
        errors.append("Makefile must keep tool overrides before the protected repository root")
    for fragment in (
        ".PHONY: build check contract-test lint test verify",
        "build: lint",
        "verify: lint contract-test test build",
        "check: verify",
        '"$(ROOT)/scripts/check-ios-camera-source.py"',
        '"$(ROOT)/scripts/test_workflow_contract.py"',
        '"$(ROOT)/app/tensorflow_camera.xcodeproj"',
        "-target CameraExample",
    ):
        if fragment not in makefile:
            errors.append(f"Makefile is missing root-independent fragment: {fragment}")

    if "docs/plans/2026-06-14-make-root-override-protection.md" not in read_text("README.md"):
        errors.append("README must index Make root override protection evidence")
    if "docs/plans/2026-06-14-finite-model-predictions.md" not in read_text("README.md"):
        errors.append("README must index finite model prediction evidence")

    return errors


def behavior_checks():
    errors = require_paths()
    if errors:
        return errors

    source = read_text("app/CameraExampleViewController.mm")
    utils_source = read_text("app/tensorflow_utils.mm")
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
        "sourceWidth == 0 || sourceFullHeight == 0 || sourceWidth > INT_MAX",
        "sourceFullHeight > INT_MAX",
        "sourceWidth > (sourceRowBytes / image_channels)",
        'LOG(ERROR) << "Invalid pixel buffer geometry";',
        "const int image_width = (int)sourceWidth;",
        "const int fullHeight = (int)sourceFullHeight;",
    ):
        if fragment not in source:
            errors.append(f"frame preprocessing geometry contract is missing: {fragment}")
    if "const int sourceRowBytes =" in source:
        errors.append("frame preprocessing must not truncate the Core Video row stride")
    geometry_guard = source.find("sourceWidth == 0 || sourceFullHeight == 0")
    pixel_lock = source.find("CVPixelBufferLockBaseAddress(pixelBuffer, 0)")
    if geometry_guard < 0 or pixel_lock < 0 or geometry_guard > pixel_lock:
        errors.append("frame preprocessing must validate geometry before locking frame memory")
    if "const size_t in_x =\n          (static_cast<size_t>(x) * sourceWidth) /" not in source:
        errors.append("frame preprocessing must derive source x coordinates with size-aware arithmetic")
    if "const size_t in_y =\n          (static_cast<size_t>(y) * static_cast<size_t>(image_height)) /" not in source:
        errors.append("frame preprocessing must derive source y coordinates with size-aware arithmetic")
    if "const int in_x" in source or "const int in_y" in source:
        errors.append("frame preprocessing must not narrow source sampling coordinates to int")
    if "(x * image_width)" in source or "(y * image_height)" in source:
        errors.append("frame preprocessing must not multiply sampling coordinates as signed int")
    if "in + (in_y * sourceRowBytes) + (in_x * image_channels)" not in source:
        errors.append("frame preprocessing must use CVPixelBuffer row bytes for source rows")
    if "&outputs[0]" in source:
        errors.append("model output handling must not assume outputs[0] exists")
    if "outputs.empty()" not in source:
        errors.append("model output handling must guard empty output tensors")
    if "labels.empty()" not in source:
        errors.append("model output handling must guard empty label lists")
    if "labels[index % predictions.size()]" in source:
        errors.append("model output handling must not index labels by prediction count modulo")
    if "const int result_count" not in source:
        errors.append("model output handling must bound iteration by labels and predictions")
    if "stringWithCString:label.c_str()" in source:
        errors.append("model labels must not use unchecked legacy C-string conversion")
    if "stringWithUTF8String:label.c_str()" not in source:
        errors.append("model labels must use explicit UTF-8 conversion")
    if "if (!labelObject)" not in source:
        errors.append("model label rendering must reject failed string conversion")
    if "Skipping invalid UTF-8 model label" not in source:
        errors.append("model label rendering must log skipped invalid labels")
    if "#include <cmath>" not in source:
        errors.append("model output handling must include the finite-value predicate")
    if "if (!std::isfinite(predictionValue))" not in source:
        errors.append("model output handling must reject non-finite prediction values")
    if "Skipping non-finite model prediction" not in source:
        errors.append("model output handling must log skipped non-finite predictions")
    if "if (predictionValue > 0.05f)" not in source:
        errors.append("model output handling must preserve the finite prediction display threshold")
    finite_guard = source.find("if (!std::isfinite(predictionValue))")
    number_creation = source.find("[NSNumber numberWithFloat:predictionValue]")
    if finite_guard < 0 or number_creation < 0 or finite_guard > number_creation:
        errors.append("model output handling must reject non-finite predictions before NSNumber creation")
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
