"""Hypothesis shrinks failing inputs to a minimal counterexample."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from python_scaffold.core import example

pytestmark = pytest.mark.property


@given(st.integers())
def test_doubling_is_addition(value: int) -> None:
    assert example(value) == value + value
