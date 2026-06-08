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
