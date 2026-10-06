"""Shared tools.

Contents:
    accepted_arguments: limits keyword arguments to those a function accepts.
    import_object: imports an object from its import path.

"""

from __future__ import annotations

import abc
import importlib
import inspect
import re
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence


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
    if ':' in path:
        module_name, _, attributes = path.partition(':')
        candidates = [(module_name, attributes.split('.'))]
    else:
        parts = path.split('.')
        candidates = [
            ('.'.join(parts[:cut]), parts[cut:])
            for cut in range(len(parts), 0, -1)
        ]
    for module_name, attributes in candidates:
        try:
            item = importlib.import_module(module_name)
        except ModuleNotFoundError as error:
            # Only a missing candidate module means to try a shorter prefix.
            # A module that is found but is missing one of its own imports is
            # a real problem, so it is not hidden.
            missing = error.name or ''
            if module_name == missing or module_name.startswith(f'{missing}.'):
                continue
            raise
        try:
            for attribute in attributes:
                item = getattr(item, attribute)
        except AttributeError as error:
            message = f'cannot import {path!r}: {error}'
            raise ImportError(message) from error
        return item
    message = f'cannot import {path!r}: no module of that name was found'
    raise ImportError(message)


""" Private Functions """

# Marks a name that was not found (`None` could be a stored value).
_MISSING = object()


def _all_classes(layer: MutableMapping[str, Any]) -> dict[str, type]:
    """Returns the stored classes in a nested `dict`, at every level.

    Args:
        layer: nested `dict` of names that map to classes or nested `dict`s.

    Returns:
        A flat `dict` of the names and classes. If a name is in more than one
            place, the first one found is kept.

    """
    classes: dict[str, type] = {}
    for name, value in layer.items():
        if isinstance(value, dict):
            classes.update(_all_classes(value))
        else:
            classes.setdefault(name, value)
    return classes


def _all_genres(layer: MutableMapping[str, Any]) -> list[str]:
    """Returns the names of the nested `dict`s (genres), at every level.

    Args:
        layer: nested `dict` of names that map to classes or nested `dict`s.

    Returns:
        The names that map to nested `dict`s, depth first.

    """
    genres: list[str] = []
    for name, value in layer.items():
        if isinstance(value, dict):
            genres.append(name)
            genres.extend(_all_genres(value))
    return genres


def _apply_path(path: Sequence[Any], item: Any, **kwargs: Any) -> Any:
    """Applies each node in `path`, in order, to `item`.

    Args:
        path: nodes with an `apply` method.
        item: data or object to change.
        **kwargs: keyword arguments passed to each node.

    Returns:
        The result of the last node.

    """
    for node in path:
        item = node.apply(item, **kwargs)
    return item


def _average(items: Sequence[Any]) -> Any:
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
        message = 'cannot average an empty sequence'
        raise ValueError(message)
    try:
        total = items[0]
        for item in items[1:]:
            total = total + item
        return total / len(items)
    except TypeError as error:
        message = (
            f'cannot average results of type {type(items[0]).__name__}: they '
            f'must support addition and division by an int'
        )
        raise TypeError(message) from error


def _flatten_dict(item: MutableMapping[str, Any]) -> dict[str, Any]:
    """Returns the values of a nested `dict` that are not `dict`s, in one level.

    The keys of the nested `dict`s themselves are dropped.

    Args:
        item: nested `dict` to flatten.

    Returns:
        A flat `dict` of the keys and values at every level whose values are
            not nested `dict`s. If a key is at more than one level, the first
            one found is kept.

    """
    flat: dict[str, Any] = {}
    for key, value in item.items():
        if isinstance(value, MutableMapping):
            for nested_key, nested_value in _flatten_dict(value).items():
                flat.setdefault(nested_key, nested_value)
        else:
            flat.setdefault(key, value)
    return flat


def _find(layer: MutableMapping[str, Any], name: str) -> Any:
    """Returns the first value named `name` in a nested `dict`, at any level.

    Args:
        layer: nested `dict` to search.
        name: key to find.

    Returns:
        The value of `name`, or `_MISSING` if `name` is not in `layer`.

    """
    if name in layer:
        return layer[name]
    for value in layer.values():
        if isinstance(value, dict):
            found = _find(value, name)
            if found is not _MISSING:
                return found
    return _MISSING


def _find_genre(
    layer: MutableMapping[str, Any],
    name: str,
    genre: str | None = None) -> str | object | None:
    """Returns the name of the nested `dict` (genre) that `name` is in.

    Args:
        layer: nested `dict` to search.
        name: key to find.
        genre: name of `layer` itself. Defaults to `None`, which is the top
            level.

    Returns:
        The name of the innermost `dict` that holds `name`, `None` if it is at
            the top level, or `_MISSING` if `name` is not in `layer`.

    """
    if name in layer:
        return genre
    for key, value in layer.items():
        if isinstance(value, dict):
            found = _find_genre(value, name, key)
            if found is not _MISSING:
                return found
    return _MISSING


def _get_path(
    item: type,
    root: type,
    namer: Callable[[type], str]) -> list[str]:
    """Returns the names of the abstract ancestors of `item` below `root`.

    It follows the first base of each class that is a subclass of `root`.

    Args:
        item: subclass of `root`.
        root: class at which to stop.
        namer: function that returns the name of a class.

    Returns:
        The names of the abstract ancestors of `item`, from just below `root`
            down. A direct subclass of `root` has an empty path.

    """
    path: list[str] = []
    parent = next(base for base in item.__bases__ if issubclass(base, root))
    while parent is not root:
        if _is_abstract(parent):
            path.insert(0, namer(parent))
        parent = next(
            base for base in parent.__bases__ if issubclass(base, root))
    return path


def _get_all_keys(item: MutableMapping[str, Any]) -> list[str]:
    """Returns `list` of all keys in a nested `dict`.

    Args:
        item: mapping to find keys from.

    Returns:
        All keys in the nested dictionary, at every level.

    """
    keys = []
    for key, value in item.items():
        keys.append(key)
        if isinstance(value, MutableMapping):
            keys.extend(_get_all_keys(value))
    return keys


def _is_abstract(item: type) -> bool:
    """Returns whether `abc.ABC` is one of the bases of `item`.

    Args:
        item: class to check.

    Returns:
        Whether `item` lists `abc.ABC` among its bases.

    """
    return abc.ABC in item.__bases__


def _iterify(item: Any) -> list[Any]:
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


def _listify_names(item: Any) -> list[str]:
    """Returns a `list` of names from a setting.

    Args:
        item: a `str` of names separated by commas, a sequence of names (each
            of which may also have commas), or `None`.

    Returns:
        The names, with whitespace removed and empty names dropped.

    """
    return [
        part.strip()
        for value in _iterify(item)
        for part in str(value).split(',')
        if part.strip()]


def _namify(item: Any, default: str | None = None) -> str | None:
    """Returns `str` name representation of `item`.

    Args:
        item: item to determine a `str` name for.
        default: default name to return if a name cannot be created.

    Returns:
        A name for `item`: `item` itself if it is a `str`, the `name` of an
            instance that has a `str` name, or the snake case name of its
            class.

    """
    if isinstance(item, str):
        return item
    elif (
        hasattr(item, 'name')
        and not inspect.isclass(item)
        and isinstance(item.name, str)
    ):
        return item.name
    else:
        try:
            return _snakify(item.__name__)
        except AttributeError:
            if item.__class__.__name__ is not None:
                return _snakify(item.__class__.__name__)
            else:
                return default


def _snakify(item: str) -> str:
    """Converts a capitalized `str` to snake case.

    Args:
        item: `str` to convert.

    Returns:
        `item` converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()
