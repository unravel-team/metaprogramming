import pytest

from python_scaffold import add

pytestmark = pytest.mark.unit


def test_add() -> None:
    assert add(2, 3) == 5
