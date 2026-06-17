#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/prediction-range-tests.XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT HUP INT TERM

"${CXX:-c++}" -std=c++11 -Wall -Wextra -Werror \
  -I"$ROOT/app" \
  "$ROOT/tests/prediction_validation_test.cc" \
  -o "$TEMP_DIR/prediction_validation_test"
"$TEMP_DIR/prediction_validation_test"
