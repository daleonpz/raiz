# Copyright (c) 2026 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

"""
test_greeter.py

Example pytest test file for demonstrating Robot Framework integration.
"""

###############################################################################
# Imports
###############################################################################
import asyncio
import pytest


###############################################################################
# Public Functions
###############################################################################
class Greeter:
    async def say_hello(self, name: str) -> str:
        await asyncio.sleep(0.1)
        return f"Hello, {name}!"


###############################################################################
# Fixtures
###############################################################################
@pytest.fixture
def greeter():
    return Greeter()


###############################################################################
# Tests
###############################################################################
@pytest.mark.asyncio
async def test_greeter_says_hello_world(greeter):
    """Greeter should respond with a properly formatted greeting."""
    result = await greeter.say_hello("World")
    assert result == "Hello, World!", f"unexpected greeting: {result!r}"
