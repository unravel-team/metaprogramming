"""Example test file showing pytest patterns."""

import pytest

pytestmark = pytest.mark.unit


def test_example() -> None:
    """Basic test example."""
    assert True


@pytest.mark.parametrize("a,b,expected", [(1, 2, 3), (2, 3, 5)])
def test_parametrized(a: int, b: int, expected: int) -> None:
    """Parametrized test example."""
    assert a + b == expected
