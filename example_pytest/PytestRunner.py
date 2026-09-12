# Copyright (c) 2026 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

"""
PytestRunner.py

Runner for executing pytest tests from Robot Framework.

Review hello.robot and test_greeter.py for usage examples.
"""

###############################################################################
# Imports
###############################################################################
import subprocess
import sys
from robot.api.deco import keyword, library


###############################################################################
# Public Functions
###############################################################################
@library
class PytestRunner:

    @keyword("Run Pytest Test")
    def run_pytest_test(self, node_id, extra_args=""):
        """Runs a single pytest test by node id and fails the RF test on nonzero exit."""
        cmd = [sys.executable, "-m", "pytest", node_id, "-q"]
        if extra_args:
            cmd.extend(extra_args.split())

        result = subprocess.run(cmd, capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode != 0:
            raise AssertionError(
                f"Pytest test failed (exit code {result.returncode}):\n{result.stdout}"
            )
