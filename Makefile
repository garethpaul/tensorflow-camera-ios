.PHONY: build check contract-test lint test verify

PYTHON ?= python3
XCODEBUILD ?= xcodebuild
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

lint:
	$(PYTHON) "$(ROOT)/scripts/check-ios-camera-source.py" --mode project

test:
	$(PYTHON) "$(ROOT)/scripts/check-ios-camera-source.py" --mode behavior

contract-test:
	$(PYTHON) "$(ROOT)/scripts/test_workflow_contract.py"

build: lint
	@if command -v "$(XCODEBUILD)" >/dev/null 2>&1; then \
		"$(XCODEBUILD)" -project "$(ROOT)/app/tensorflow_camera.xcodeproj" -target CameraExample -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild not found; static project checks completed"; \
	fi

verify: lint contract-test test build

check: verify
