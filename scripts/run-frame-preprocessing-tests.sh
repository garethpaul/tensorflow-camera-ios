#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/frame-preprocessing-tests.XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM

"${CXX:-c++}" -std=c++11 -Wall -Wextra -Werror \
  -I"$ROOT/app" \
  "$ROOT/tests/frame_preprocessing_test.cc" \
  -o "$TEMP_DIR/frame_preprocessing_test"
"$TEMP_DIR/frame_preprocessing_test"
