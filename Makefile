.PHONY: build check contract-test lint test verify

PYTHON ?= python3
CXX ?= c++
XCODEBUILD ?= xcodebuild
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

lint:
	$(PYTHON) "$(ROOT)/scripts/check-ios-camera-source.py" --mode project

test:
	$(PYTHON) "$(ROOT)/scripts/check-ios-camera-source.py" --mode behavior
	CXX="$(CXX)" "$(ROOT)/scripts/run-frame-preprocessing-tests.sh"
	CXX="$(CXX)" $(PYTHON) "$(ROOT)/scripts/test_frame_preprocessing_mutations.py"
	CXX="$(CXX)" "$(ROOT)/scripts/run-prediction-range-tests.sh"

contract-test:
	$(PYTHON) "$(ROOT)/scripts/test_workflow_contract.py"
	$(PYTHON) "$(ROOT)/scripts/test_credential_fixture_policy.py"

build: lint
	XCODEBUILD="$(XCODEBUILD)" "$(ROOT)/scripts/run-ios-build.sh"

verify: lint contract-test test build

check: verify
