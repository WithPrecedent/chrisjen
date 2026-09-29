"""Configuration settings and convenience functions for changing those settings.

Contents:
    set_verbose_rule: sets the global attribute message verbosity rule.

"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from . import nodes, utilities

if TYPE_CHECKING:
    from . import base

_AUTO_EXECUTE: bool = False
_NULL_NODE: type[base.Node] = nodes.NullNode
_UNIQUE_IDENTIFIER: Callable[[], str] = utilities.how_soon_is_now
# Whether to return more elaborate error messages and feedback.
_VERBOSE: bool = False
_WARNINGS: bool = False

def set_verbose_rule(verbose: bool) -> None:
    """Sets the global attribute message verbosity rule.

    Args:
        verbose: whether to set the default rule to verbosity in logging and
            messaging.

    Raises:
        TypeError: if `verbose` is not bool.

    """
    if isinstance(verbose, bool):
        globals()["_VERBOSE"] = verbose
    else:
        raise TypeError('verbose argument must be boolean')


# @dataclasses.dataclass
# class _MISSING_VALUE(object):
#     """Sentinel object for a missing data or parameter.

#     This follows the same pattern as the '__MISSING_TYPE` class in the builtin
#     dataclasses library.
#     https://github.com/python/cpython/blob/3.10/Lib/dataclasses.py#L182-L186

#     Because None is sometimes a valid argument or data option, this class
#     provides an alternative that does not create the confusion that a default of
#     None can sometimes lead to.

#     """
#     pass


# # _MISSING, instance of _MISSING_VALUE, should be used for missing values as an
# # alternative to None when None is a valid value for an argument. This provides
# # a fuller repr and traceback.
# _MISSING = _MISSING_VALUE()
