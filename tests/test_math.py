import pytest
import mathlib  # Assume ctypes wrapper or binding

@pytest.mark.req("REQ-001")
def test_add():
    assert mathlib.add(3, 5) == 8

@pytest.mark.req("REQ-002")
def test_multiply():
    assert mathlib.multiply(2, 4) == 8

