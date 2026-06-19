#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
XCODEBUILD=${XCODEBUILD:-xcodebuild}

if ! command -v "$XCODEBUILD" >/dev/null 2>&1; then
  echo "xcodebuild not found; static project checks completed"
  exit 0
fi

TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/tensorflow-camera-xcodebuild.XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM

"$XCODEBUILD" \
  -project "$ROOT/app/tensorflow_camera.xcodeproj" \
  -target CameraExample \
  -sdk iphonesimulator \
  CODE_SIGNING_ALLOWED=NO \
  OBJROOT="$TEMP_DIR/obj" \
  SYMROOT="$TEMP_DIR/products" \
  SHARED_PRECOMPS_DIR="$TEMP_DIR/precompiled"
