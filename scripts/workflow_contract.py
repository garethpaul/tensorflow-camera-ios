import re


CHECKOUT_ACTION = "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10"
SETUP_ACTION = "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"
CHECKOUT_BLOCK = "\n".join((
    "      - name: Check out repository",
    f"        uses: {CHECKOUT_ACTION} # v6.0.3",
    "        with:",
    "          persist-credentials: false",
))


def validate(workflow):
    errors = []
    actions = re.findall(
        r"^[ \t]*(?:-[ \t]*)?uses:[ \t]*(\S+)(?:[ \t]+#.*)?$",
        workflow,
        re.MULTILINE,
    )

    if "  push:\n    branches:\n      - master" not in workflow:
        errors.append("validate pushes to master")
    if len(re.findall(r"^  pull_request:$", workflow, re.MULTILINE)) != 1:
        errors.append("validate pull requests exactly once")
    if len(re.findall(r"^  workflow_dispatch:$", workflow, re.MULTILINE)) != 1:
        errors.append("allow manual dispatch exactly once")
    if len(re.findall(r"^permissions:$", workflow, re.MULTILINE)) != 1:
        errors.append("declare workflow permissions exactly once")
    if not re.search(r"^permissions:\n  contents: read$", workflow, re.MULTILINE):
        errors.append("use read-only contents permission")
    if re.search(r"^[ \t]+[A-Za-z-]+:[ \t]+write[ \t]*$", workflow, re.MULTILINE):
        errors.append("not request write permissions")
    if len(re.findall(r"^  cancel-in-progress: true$", workflow, re.MULTILINE)) != 1:
        errors.append("cancel superseded runs exactly once")
    if len(re.findall(r"^    runs-on: ubuntu-24.04$", workflow, re.MULTILINE)) != 1:
        errors.append("use the fixed Ubuntu runner exactly once")
    if len(re.findall(r"^    timeout-minutes: 5$", workflow, re.MULTILINE)) != 1:
        errors.append("bound the job to five minutes exactly once")
    if CHECKOUT_BLOCK not in workflow:
        errors.append("use the exact credential-free checkout contract")
    if actions != [CHECKOUT_ACTION, SETUP_ACTION]:
        errors.append("use only the reviewed checkout and setup-python actions")
    if workflow.count("persist-credentials:") != 1:
        errors.append("configure checkout credential persistence exactly once")
    if len(re.findall(r'^          python-version: "3\.12"$', workflow, re.MULTILINE)) != 1:
        errors.append("select Python 3.12 exactly once")
    if len(re.findall(r"^        run: make check$", workflow, re.MULTILINE)) != 1:
        errors.append("run the canonical gate exactly once")
    if "continue-on-error" in workflow:
        errors.append("not allow contract failures")
    if re.search(r"\b(?:pip|pip3) install\b", workflow):
        errors.append("not install dependencies for the SDK-free contract")
    if "xcodebuild" in workflow:
        errors.append("not imply an unsupported hosted Xcode build")

    return errors
