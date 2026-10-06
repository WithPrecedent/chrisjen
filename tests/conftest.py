"""Shared fixtures for the tests."""

from __future__ import annotations

import copy
from collections.abc import Iterator

import pytest

import chrisjen


@pytest.fixture(autouse = True)
def restore_library() -> Iterator[None]:
    """Removes the classes that a test adds to the library."""
    saved = copy.deepcopy(chrisjen.library.contents)
    yield
    chrisjen.library.contents.clear()
    chrisjen.library.contents.update(saved)
