"""Shared tools.

Contents:
    iterify: wraps an item in a `list` without splitting `str` types.
    how_soon_is_now: returns a timestamp `str`.
    average: computes the mean of a `Sequence` of results.
    accepted_arguments: limits keyword arguments to those a function accepts.
    import_object: imports an object from its import path.

"""

from __future__ import annotations

import datetime
import importlib
import inspect
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence


def iterify(item: Any) -> list[Any]:
    """Returns `item` as a `list`, but does not iterate `str` types.

    Args:
        item: item to turn into a `list`.

    Returns:
        A `list` of `item`. A `str` is stored as a single item, `None` becomes
            an empty `list`, and any other non-iterable is wrapped in a `list`.

    """
    if item is None:
        return []
    if isinstance(item, str | bytes):
        return [item]
    try:
        return list(item)
    except TypeError:
        return [item]


def how_soon_is_now(prefix: str = "", suffix: str = "") -> str:
    """Returns a `str` of the current date and time.

    Args:
        prefix: text to place before the timestamp.
        suffix: text to place after the timestamp.

    Returns:
        A timestamp like '2024-01-31_13-45-59' with `prefix` and `suffix`.

    """
    stamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}{stamp}{suffix}"


def average(items: Sequence[Any]) -> Any:
    """Returns the mean of `items`.

    This works for numbers and for any objects that support addition and
    division by an `int` (e.g., `numpy` arrays or `pandas` objects).

    Args:
        items: results to average.

    Raises:
        ValueError: if `items` is empty.
        TypeError: if `items` cannot be added together and divided by an
            `int`.

    Returns:
        The mean of `items`.

    """
    if not items:
        message = "cannot average an empty sequence"
        raise ValueError(message)
    try:
        total = items[0]
        for item in items[1:]:
            total = total + item
        return total / len(items)
    except TypeError as error:
        message = (
            f"cannot average results of type {type(items[0]).__name__}: they "
            f"must support addition and division by an int"
        )
        raise TypeError(message) from error


def accepted_arguments(
    function: Callable[..., Any], arguments: Mapping[str, Any]
) -> dict[str, Any]:
    """Returns the `arguments` that `function` can accept as keywords.

    If `function` takes `**kwargs` (or its signature cannot be inspected), all
    of `arguments` are returned.

    Args:
        function: callable to examine.
        arguments: keyword arguments to filter.

    Returns:
        A `dict` of the `arguments` that `function` accepts.

    """
    try:
        parameters = inspect.signature(function).parameters
    except (TypeError, ValueError):
        return dict(arguments)
    if any(
        p.kind is inspect.Parameter.VAR_KEYWORD for p in parameters.values()
    ):
        return dict(arguments)
    return {k: v for k, v in arguments.items() if k in parameters}


def import_object(path: str) -> Any:
    """Imports an object (such as a function or class) from its import path.

    The path can be dotted (`"statistics.fmean"` or
    `"sklearn.preprocessing.StandardScaler"`) or use a colon between the module
    and the attributes (`"package.module:Class.method"`). With a dotted path,
    the longest prefix that is a module is imported and the rest are attributes.

    Args:
        path: import path of the object.

    Raises:
        ImportError: if no module or attribute matches `path`.

    Returns:
        The imported object.

    """
    if ":" in path:
        module_name, _, attributes = path.partition(":")
        candidates = [(module_name, attributes.split("."))]
    else:
        parts = path.split(".")
        candidates = [
            (".".join(parts[:cut]), parts[cut:])
            for cut in range(len(parts), 0, -1)
        ]
    for module_name, attributes in candidates:
        try:
            item = importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            # Only a missing candidate module means to try a shorter prefix.
            # A module that is found but is missing one of its own imports is
            # a real problem, so it is not hidden.
            missing = error.name or ""
            if module_name == missing or module_name.startswith(f"{missing}."):
                continue
            raise
        try:
            for attribute in attributes:
                item = getattr(item, attribute)
        except AttributeError as error:
            message = f"cannot import {path!r}: {error}"
            raise ImportError(message) from error
        return item
    message = f"cannot import {path!r}: no module of that name was found"
    raise ImportError(message)
