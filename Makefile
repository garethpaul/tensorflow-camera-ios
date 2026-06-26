.DEFAULT_GOAL := check
.PHONY: __repository-make-authority build check contract-test lint root-test test verify
.SECONDEXPANSION:

PYTHON ?= python3
CXX ?= c++
XCODEBUILD ?= xcodebuild
override PYTHON := $(value PYTHON)
override CXX := $(value CXX)
override XCODEBUILD := $(value XCODEBUILD)
export PYTHON CXX XCODEBUILD
override SHELL := /bin/sh
override .SHELLFLAGS := -c

ifneq ($(filter command line,$(origin MAKEFLAGS)),)
$(error MAKEFLAGS must not be overridden for repository verification)
endif
override REPOSITORY_MAKE_FIRST_FLAGS := $(firstword $(MAKEFLAGS))
ifneq ($(filter -%,$(REPOSITORY_MAKE_FIRST_FLAGS)),)
override REPOSITORY_MAKE_FIRST_FLAGS :=
endif
override REPOSITORY_MAKE_SHORT_FLAGS := $(REPOSITORY_MAKE_FIRST_FLAGS) $(filter-out --%,$(filter -%,$(MAKEFLAGS)))
ifneq ($(findstring n,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring t,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring q,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(findstring i,$(REPOSITORY_MAKE_SHORT_FLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(filter --just-print --dry-run --recon --touch --question --ignore-errors,$(MAKEFLAGS)),)
$(error non-executing or error-ignoring MAKEFLAGS are not supported for repository verification)
endif
ifneq ($(strip $(MAKEFILES)),)
$(error MAKEFILES must be empty; repository verification requires this Makefile to be loaded alone)
endif
override MAKEFILES :=
ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(value MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); [ -f "$$path" ] || exit 1; directory=$$(/usr/bin/dirname -- "$$path"); CDPATH= cd -- "$$directory" && /bin/pwd -P)
export ROOT
ifeq ($(strip $(ROOT)),)
$(error repository Makefile path could not be resolved)
endif

build check contract-test lint root-test test verify: $$(if $$(filter file,$$(origin MAKEFILE_LIST)),,$$(error MAKEFILE_LIST must not be overridden))
build check contract-test lint root-test test verify: $$(if $$(shell path=$$$$(/usr/bin/printf '%s' '$$(subst ','"'"',$$(MAKEFILE_LIST))' | /usr/bin/sed 's/^ //') && [ -f "$$$$path" ] && /usr/bin/printf '%s' ok),,$$(error repository Makefile must be loaded alone))
build check contract-test lint root-test test verify: __repository-make-authority

__repository-make-authority::
	@:

lint:
	"$$PYTHON" "$$ROOT/scripts/check-ios-camera-source.py" --mode project

test:
	"$$PYTHON" "$$ROOT/scripts/check-ios-camera-source.py" --mode behavior
	CXX="$$CXX" "$$ROOT/scripts/run-frame-preprocessing-tests.sh"
	CXX="$$CXX" "$$PYTHON" "$$ROOT/scripts/test_frame_preprocessing_mutations.py"
	CXX="$$CXX" "$$ROOT/scripts/run-prediction-range-tests.sh"
	CXX="$$CXX" "$$ROOT/scripts/run-prediction-output-tests.sh"
	CXX="$$CXX" "$$PYTHON" "$$ROOT/scripts/test_prediction_output_mutations.py"

contract-test:
	"$$PYTHON" "$$ROOT/scripts/test_workflow_contract.py"
	"$$PYTHON" "$$ROOT/scripts/test_credential_fixture_policy.py"

build: lint
	XCODEBUILD="$$XCODEBUILD" "$$ROOT/scripts/run-ios-build.sh"

root-test:
	/bin/sh "$$ROOT/scripts/test-makefile-root.sh"

verify: root-test lint contract-test test build

check: verify
