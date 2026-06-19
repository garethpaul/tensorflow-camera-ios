#!/usr/bin/env python3
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = (ROOT / "app" / "frame_preprocessing.h").read_text(encoding="utf-8")
TEST = ROOT / "tests" / "frame_preprocessing_test.cc"
CXX = os.environ.get("CXX", "c++")


def rejected(description, old, new):
    mutated = HEADER.replace(old, new, 1)
    if mutated == HEADER:
        raise AssertionError(f"mutation did not apply: {description}")
    with tempfile.TemporaryDirectory(prefix="frame-preprocessing-mutation-") as directory:
        temp = Path(directory)
        (temp / "frame_preprocessing.h").write_text(mutated, encoding="utf-8")
        executable = temp / "frame_preprocessing_test"
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
    "BGRA red/blue swap": ("*source_channel = 2 - output_channel;", "*source_channel = output_channel;"),
    "ARGB alpha exposure": ("*source_channel = output_channel + 1;", "*source_channel = output_channel;"),
    "landscape crop removal": (
        "const size_t crop_x = (width - crop_size) / 2;",
        "const size_t crop_x = 0;",
    ),
    "portrait crop removal": (
        "const size_t crop_y = (height - crop_size) / 2;",
        "const size_t crop_y = 0;",
    ),
    "backing-size check removal": (
        "final_offset >= data_size",
        "final_offset > data_size",
    ),
    "resize overflow check removal": (
        "!CheckedMultiply(position, source_extent, &product)",
        "(product = position * source_extent, false)",
    ),
}

for description, (old, new) in mutations.items():
    rejected(description, old, new)

print(f"frame preprocessing mutation tests passed ({len(mutations)} mutations rejected)")
