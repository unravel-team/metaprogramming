"""Unit tests exercise the shipped library and HTTP application."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from python_scaffold.api import app
from python_scaffold.core import example

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("value, expected", [(0, 0), (2, 4), (-3, -6)])
def test_example(value: int, expected: int) -> None:
    assert example(value) == expected


def test_health() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
