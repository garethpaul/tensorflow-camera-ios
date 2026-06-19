#!/usr/bin/env python3
from pathlib import Path

from workflow_contract import CHECKOUT_ACTION, SETUP_ACTION, validate


ROOT = Path(__file__).resolve().parents[1]
BASELINE = (ROOT / ".github" / "workflows" / "check.yml").read_text(encoding="utf-8")


def mutate(description, target, replacement):
    mutated = BASELINE.replace(target, replacement, 1)
    if mutated == BASELINE:
        raise AssertionError(f"{description} mutation did not alter the fixture")
    return mutated


def assert_invalid(description, workflow):
    if not validate(workflow):
        raise AssertionError(f"{description} mutation was accepted")


baseline_errors = validate(BASELINE)
if baseline_errors:
    raise AssertionError(f"baseline workflow is invalid: {baseline_errors}")

mutations = {
    "contradictory credentials": mutate("contradictory credentials", "persist-credentials: false", "persist-credentials: false\n          persist-credentials: true"),
    "relocated credentials": mutate("relocated credentials", "        with:\n          persist-credentials: false\n", "").replace("permissions:", "persist-credentials: false\n\npermissions:", 1),
    "floating checkout": mutate("floating checkout", CHECKOUT_ACTION, "actions/checkout@v6"),
    "floating setup": mutate("floating setup", SETUP_ACTION, "actions/setup-python@v6"),
    "extra action": mutate("extra action", "      - name: Set up Python", "      - uses: example/unreviewed-action@v1\n      - name: Set up Python"),
    "write permission": mutate("write permission", "contents: read", "contents: read\n  issues: write"),
    "missing push": mutate("missing push", "  push:\n    branches:\n      - master\n", ""),
    "missing pull request": mutate("missing pull request", "  pull_request:\n", ""),
    "missing manual dispatch": mutate("missing manual dispatch", "  workflow_dispatch:\n", ""),
    "duplicate runner": mutate("duplicate runner", "    runs-on: ubuntu-24.04", "    runs-on: ubuntu-24.04\n    runs-on: ubuntu-24.04"),
    "unbounded job": mutate("unbounded job", "    timeout-minutes: 5\n", ""),
    "continued failure": mutate("continued failure", "    steps:", "    continue-on-error: true\n    steps:"),
    "wrong Python": mutate("wrong Python", 'python-version: "3.12"', 'python-version: "3.11"'),
    "dependency installation": mutate("dependency installation", "run: make check", "run: pip install -r requirements.txt && make check"),
    "hosted Xcode": mutate("hosted Xcode", "run: make check", "run: xcodebuild build && make check"),
    "weakened gate": mutate("weakened gate", "run: make check", "run: make lint"),
}

for description, workflow in mutations.items():
    assert_invalid(description, workflow)

print(f"workflow contract tests passed ({len(mutations)} mutations rejected).")
