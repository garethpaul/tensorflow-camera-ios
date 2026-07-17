#!/usr/bin/env python3
"""Prove that each native test runner executes its binary and gates on defects.

The source checks in check-ios-camera-source.py can only prove that a compile
line and an execution line exist inside a runner script. Text cannot prove the
compiled binary is ever executed:

  * A substring pin on '"$TEMP_DIR/prediction_validation_test"' is already
    satisfied by the compile line's own -o argument, so deleting the execution
    line leaves every pin green while the suite stops running.
  * An anchored whole-line pin is satisfied by an execution line that is kept
    byte-identical inside an `if false; then ... fi` block.

This test observes behaviour instead. For each runner it builds an isolated
copy of the headers, tests and runner, injects a defect that compiles cleanly
but breaks a documented behaviour, and requires the runner to fail *and* to
report that specific assertion. Requiring the diagnostic - not merely a
non-zero exit - distinguishes a genuinely caught defect from a compile error,
which would otherwise look identical.

The clean direction is asserted too: an unmodified runner must exit zero and
print its success marker, so a runner that always fails cannot pass this test.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CXX = os.environ.get("CXX", "c++")

# label, runner, header, defect (old -> new), success marker, required diagnostic
SUITES = (
    (
        "frame preprocessing",
        "run-frame-preprocessing-tests.sh",
        "frame_preprocessing.h",
        "*source_channel = 2 - output_channel;",
        "*source_channel = output_channel;",
        "Frame preprocessing tests passed",
        "FAIL: BGRA input is published to TensorFlow as RGB",
    ),
    (
        "model prediction range",
        "run-prediction-range-tests.sh",
        "prediction_validation.h",
        "value <= 1.0f;",
        "value <= 100.0f;",
        "Prediction range tests passed",
        "FAIL: predictions above one are rejected",
    ),
    (
        "model prediction output",
        "run-prediction-output-tests.sh",
        "prediction_output.h",
        "value <= threshold",
        "value < threshold",
        "Prediction output tests passed",
        "FAIL: only scores above the threshold are selected",
    ),
)


def build_tree(directory):
    """Copy the headers, native tests and runners into an isolated checkout."""
    tree = Path(directory) / "checkout"
    (tree / "app").mkdir(parents=True)
    (tree / "tests").mkdir(parents=True)
    (tree / "scripts").mkdir(parents=True)
    for header in sorted((ROOT / "app").glob("*.h")):
        shutil.copy2(header, tree / "app" / header.name)
    for test in sorted((ROOT / "tests").glob("*.cc")):
        shutil.copy2(test, tree / "tests" / test.name)
    for _, runner, _, _, _, _, _ in SUITES:
        shutil.copy2(ROOT / "scripts" / runner, tree / "scripts" / runner)
    return tree


def run_runner(tree, runner):
    result = subprocess.run(
        ["/bin/sh", str(tree / "scripts" / runner)],
        capture_output=True,
        text=True,
        env={**os.environ, "CXX": CXX},
    )
    return result.returncode, result.stdout + result.stderr


def check_executes(label, runner, marker):
    """An unmodified runner must run its binary: exit zero and print marker."""
    with tempfile.TemporaryDirectory(prefix="native-suite-execution-") as directory:
        tree = build_tree(directory)
        status, output = run_runner(tree, runner)
        if status != 0:
            raise AssertionError(
                f"{label} runner failed on an unmodified checkout "
                f"(exit {status}):\n{output}"
            )
        if marker not in output:
            raise AssertionError(
                f"{label} runner exited zero without printing {marker!r}; it "
                f"compiled the test without executing it:\n{output}"
            )


def check_gates(label, runner, header, old, new, diagnostic):
    """A defective header must make the runner fail with its own diagnostic."""
    with tempfile.TemporaryDirectory(prefix="native-suite-execution-") as directory:
        tree = build_tree(directory)
        path = tree / "app" / header
        source = path.read_text(encoding="utf-8")
        if source.count(old) < 1:
            raise AssertionError(
                f"{label} defect anchor is missing from app/{header}: {old!r}"
            )
        path.write_text(source.replace(old, new, 1), encoding="utf-8")

        status, output = run_runner(tree, runner)
        if status == 0:
            raise AssertionError(
                f"{label} runner accepted a defective app/{header}; it does not "
                f"execute {runner} against the compiled binary:\n{output}"
            )
        if diagnostic not in output:
            raise AssertionError(
                f"{label} runner failed without reporting {diagnostic!r}, so the "
                f"failure is not a caught defect (a compile error would look the "
                f"same):\n{output}"
            )


def main():
    executed = 0
    for label, runner, header, old, new, marker, diagnostic in SUITES:
        check_executes(label, runner, marker)
        check_gates(label, runner, header, old, new, diagnostic)
        executed += 2
    if executed != 6:
        raise AssertionError(f"expected 6 execution cases, ran {executed}")
    print(
        f"native suite execution tests passed ({executed} cases: "
        f"{len(SUITES)} runners execute their binaries and gate on defects)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
