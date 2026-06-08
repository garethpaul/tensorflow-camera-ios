#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
    ):
        if not (ROOT / relative_path).exists():
            errors.append(f"missing required file: {relative_path}")
    return errors


def project_checks():
    errors = require_paths()
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

    return errors


def behavior_checks():
    errors = require_paths()
    if errors:
        return errors

    source = read_text("app/CameraExampleViewController.mm")
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
    if "Unsupported pixel format:" not in source:
        errors.append("frame preprocessing must log unsupported pixel formats")
    if "CVPixelBufferLockBaseAddress(pixelBuffer, 0) != kCVReturnSuccess" not in source:
        errors.append("frame preprocessing must handle pixel buffer lock failures")
    if "CVPixelBufferUnlockBaseAddress(pixelBuffer, 0);" not in source:
        errors.append("frame preprocessing must unlock locked pixel buffers")

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
