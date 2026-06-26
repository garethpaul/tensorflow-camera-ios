#!/usr/bin/env python3
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "app" / "prediction_output.h").read_text(encoding="utf-8")
VALIDATION_HEADER = ROOT / "app" / "prediction_validation.h"
TEST = ROOT / "tests" / "prediction_output_test.cc"
CXX = os.environ.get("CXX", "c++")


def rejected(description, old, new):
    mutated = HEADER.replace(old, new, 1)
    if mutated == HEADER:
        raise AssertionError(f"mutation did not apply: {description}")
    with tempfile.TemporaryDirectory(prefix="prediction-output-mutation-") as directory:
        temp = Path(directory)
        (temp / "prediction_output.h").write_text(mutated, encoding="utf-8")
        (temp / "prediction_validation.h").write_bytes(VALIDATION_HEADER.read_bytes())
        executable = temp / "prediction_output_test"
        compile_result = subprocess.run(
            [
                CXX,
                "-std=c++11",
                "-Wall",
                "-Wextra",
                "-Werror",
                f"-I{temp}",
                str(TEST),
                "-o",
                str(executable),
            ],
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            return
        run_result = subprocess.run(
            [str(executable)], capture_output=True, text=True
        )
        if run_result.returncode == 0:
            raise AssertionError(f"mutation survived: {description}")


mutations = {
    "capture intent publication gate": (
        "return capture_requested && view_is_visible && application_is_active;",
        "return view_is_visible && application_is_active;",
    ),
    "visible view publication gate": (
        "return capture_requested && view_is_visible && application_is_active;",
        "return capture_requested && application_is_active;",
    ),
    "active application publication gate": (
        "return capture_requested && view_is_visible && application_is_active;",
        "return capture_requested && view_is_visible;",
    ),
    "inclusive threshold": ("value <= threshold", "value < threshold"),
    "label bound": (
        "predictions.size() < labels.size() ? predictions.size() : labels.size()",
        "predictions.size()",
    ),
    "prediction range": ("!IsValidModelPrediction(value) ||", ""),
    "label association": ("labels[index]", "labels[0]"),
    "finite threshold": ("!std::isfinite(threshold)", "false"),
}

for description, (old, new) in mutations.items():
    rejected(description, old, new)

print(f"prediction output mutation tests passed ({len(mutations)} mutations rejected)")
