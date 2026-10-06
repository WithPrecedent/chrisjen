"""Tests the global settings."""

from __future__ import annotations

from typing import Any

import pytest

from chrisjen import options, utilities


@pytest.fixture(autouse = True)
def restore_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Puts the global settings back after each test."""
    for name in (
        '_KEY_NAMER',
        '_VERBOSE',
        '_STRICT_COMPATIBILITY',
        '_METHOD_NAMER',
        '_OVERWRITE',
    ):
        if hasattr(options, name):
            monkeypatch.setattr(options, name, getattr(options, name))
        else:
            monkeypatch.setattr(options, name, None, raising = False)


def test_defaults() -> None:
    assert options._KEY_NAMER is utilities._namify
    assert options._VERBOSE is False


def test_set_keyer() -> None:
    def shout(item: Any) -> str:
        return str(item).upper()

    options.set_keyer(shout)
    assert options._KEY_NAMER is shout
    with pytest.raises(TypeError, match = 'callable'):
        options.set_keyer('not a function')  # type: ignore[arg-type]
    assert options._KEY_NAMER is shout


def test_set_method_namer() -> None:
    def namer(item: Any) -> str:
        return f'make_{item}'

    options.set_method_namer(namer)
    assert options._METHOD_NAMER is namer
    with pytest.raises(TypeError, match = 'callable'):
        options.set_method_namer(3)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ('function', 'attribute'),
    [
        (options.set_compatibility_rule, '_STRICT_COMPATIBILITY'),
        (options.set_overwrite_rule, '_OVERWRITE'),
        (options.set_verbose_rule, '_VERBOSE'),
    ],
)
def test_boolean_rules(function: Any, attribute: str) -> None:
    function(True)
    assert getattr(options, attribute) is True
    function(False)
    assert getattr(options, attribute) is False
    with pytest.raises(TypeError, match = 'boolean'):
        function('yes')
    with pytest.raises(TypeError, match = 'boolean'):
        function(1)
    assert getattr(options, attribute) is False
