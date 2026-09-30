"""Tests shared utilities."""

from __future__ import annotations

import inspect
import re
from typing import Any

import pytest

from chrisjen import utilities


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        (None, []),
        ("abc", ["abc"]),
        ("", [""]),
        (b"ab", [b"ab"]),
        ([1, 2], [1, 2]),
        ((1, 2), [1, 2]),
        (range(3), [0, 1, 2]),
        ({"a": 1}, ["a"]),
        (5, [5]),
        (2.5, [2.5]),
    ],
)
def test_iterify(item: Any, expected: list[Any]) -> None:
    assert utilities.iterify(item) == expected


def test_iterify_returns_a_new_list() -> None:
    original = [1, 2]
    result = utilities.iterify(original)
    result.append(3)
    assert original == [1, 2]


def test_how_soon_is_now() -> None:
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
    assert re.fullmatch(pattern, utilities.how_soon_is_now())
    assert re.fullmatch(
        rf"run_{pattern}\.log",
        utilities.how_soon_is_now(prefix = "run_", suffix = ".log"),
    )


class Vector:
    def __init__(self, values: list[float]) -> None:
        self.values = values

    def __add__(self, other: Vector) -> Vector:
        return Vector([a + b for a, b in zip(self.values, other.values)])

    def __truediv__(self, divisor: int) -> Vector:
        return Vector([a / divisor for a in self.values])


def test_average_of_numbers() -> None:
    assert utilities.average([1, 2, 3]) == 2
    assert utilities.average([1.5]) == 1.5
    assert utilities.average([1, 2]) == 1.5
    assert utilities.average((4, 6, 8, 10)) == 7


def test_average_of_objects_that_support_arithmetic() -> None:
    result = utilities.average([Vector([1, 2]), Vector([3, 6])])
    assert result.values == [2, 4]


def test_average_does_not_change_its_items() -> None:
    first = Vector([1, 2])
    utilities.average([first, Vector([3, 4])])
    assert first.values == [1, 2]


def test_average_of_nothing() -> None:
    with pytest.raises(ValueError, match = "empty"):
        utilities.average([])


def test_average_of_things_that_cannot_be_added() -> None:
    with pytest.raises(TypeError, match = "cannot average results of type str"):
        utilities.average(["a", 1])
    with pytest.raises(TypeError, match = "type list.*division by an int"):
        utilities.average([[1], [2]])


def test_accepted_arguments_filters_by_signature() -> None:
    def function(item: Any, a: int, b: int = 1) -> None:
        return None

    arguments = {"a": 1, "b": 2, "c": 3}
    assert utilities.accepted_arguments(function, arguments) == {"a": 1, "b": 2}
    assert utilities.accepted_arguments(function, {}) == {}


def test_accepted_arguments_with_keywords_argument() -> None:
    def function(item: Any, **kwargs: Any) -> None:
        return None

    arguments = {"a": 1, "b": 2}
    result = utilities.accepted_arguments(function, arguments)
    assert result == arguments
    assert result is not arguments


def test_accepted_arguments_with_keyword_only_and_callable_objects() -> None:
    def function(item: Any, *, a: int) -> None:
        return None

    assert utilities.accepted_arguments(function, {"a": 1, "z": 2}) == {"a": 1}

    class Callable:
        def __call__(self, item: Any, factor: int = 2) -> None:
            return None

    assert utilities.accepted_arguments(Callable(), {"factor": 3, "z": 1}) == {
        "factor": 3
    }


def test_accepted_arguments_when_signature_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def broken(function: Any) -> inspect.Signature:
        raise ValueError

    monkeypatch.setattr(inspect, "signature", broken)
    arguments = {"a": 1}
    assert utilities.accepted_arguments(len, arguments) == arguments


""" Importing by path """


def test_import_object_from_dotted_and_colon_paths() -> None:
    import collections
    import os.path
    import statistics

    assert utilities.import_object("statistics.fmean") is statistics.fmean
    assert utilities.import_object("statistics:fmean") is statistics.fmean
    assert utilities.import_object("statistics") is statistics
    assert utilities.import_object("os.path") is os.path
    assert utilities.import_object("builtins.str.upper") is str.upper
    assert utilities.import_object("builtins:str.upper") is str.upper
    assert (
        utilities.import_object("collections:OrderedDict.fromkeys")
        == collections.OrderedDict.fromkeys
    )
    assert utilities.import_object("statistics.NormalDist") is (
        statistics.NormalDist
    )


def test_import_object_errors() -> None:
    with pytest.raises(ImportError, match = "'no_such_module.tool'.*no module"):
        utilities.import_object("no_such_module.tool")
    with pytest.raises(ImportError, match = "'no_such_module:tool'.*no module"):
        utilities.import_object("no_such_module:tool")
    with pytest.raises(ImportError, match = "'statistics.nope'"):
        utilities.import_object("statistics.nope")
    with pytest.raises(ImportError, match = "'statistics:fmean.nope'"):
        utilities.import_object("statistics:fmean.nope")
    # A bare name that is not a module cannot be imported.
    with pytest.raises(ImportError):
        utilities.import_object("str.upper")


def test_import_object_does_not_hide_a_modules_own_import_errors(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = tmp_path / "tt_broken_module.py"
    module.write_text("import tt_dependency_that_does_not_exist\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(ModuleNotFoundError) as error:
        utilities.import_object("tt_broken_module.tool")
    assert error.value.name == "tt_dependency_that_does_not_exist"
    with pytest.raises(ModuleNotFoundError):
        utilities.import_object("tt_broken_module:tool")


def test_import_object_finds_modules_created_after_the_first_call(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ImportError):
        utilities.import_object("tt_late_module.tool")
    (tmp_path / "tt_late_module.py").write_text(
        "def tool(item):\n    return 7\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    assert utilities.import_object("tt_late_module.tool")(0) == 7


def test_import_object_imports_submodules_that_are_not_imported_yet(
    tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "tt_package"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "sub.py").write_text("def tool(item):\n    return item + 1\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    assert utilities.import_object("tt_package.sub.tool")(1) == 2
    assert utilities.import_object("tt_package.sub:tool")(1) == 2
