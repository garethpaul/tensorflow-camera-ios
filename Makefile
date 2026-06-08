.PHONY: lint test build verify

PYTHON ?= python3
XCODEBUILD ?= xcodebuild

lint:
	$(PYTHON) scripts/check-ios-camera-source.py --mode project

test:
	$(PYTHON) scripts/check-ios-camera-source.py --mode behavior

build: lint
	@if command -v "$(XCODEBUILD)" >/dev/null 2>&1; then \
		"$(XCODEBUILD)" -project app/tensorflow_camera.xcodeproj -target tensorflow_camera -sdk iphonesimulator CODE_SIGNING_ALLOWED=NO build; \
	else \
		echo "xcodebuild not found; static project checks completed"; \
	fi

verify: lint test build
