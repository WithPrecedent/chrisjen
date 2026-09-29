"""Workers that iterate over branching workflows

Contents:
    Step
    Technique

"""
from __future__ import annotations

import dataclasses
from collections.abc import Hashable, MutableMapping
from typing import Any

from .. import nodes
from . import tasks


@dataclasses.dataclass
class Copier(tasks.Contractor):
    """Makes a set number of copies of

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.

    """
    name: str | None = None
    contents: Any | None = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)

    """ Public Methods """

    def implement(self, item: Any, **kwargs: base.Kwargs) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item: any item or data to which 'contents' should be applied,
                but most often it is an instance of 'Project'.
            kwargs: additional keyword arguments.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.

        """


@dataclasses.dataclass
class Splitter(tasks.Contractor):
    """Base class for nodes in a project workflow.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.

    """
    name: str | None = None
    contents: Any | None = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)

    """ Public Methods """

    def implement(self, item: Any, **kwargs: base.Kwargs) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item: any item or data to which 'contents' should be applied,
                but most often it is an instance of 'Project'.
            kwargs: additional keyword arguments.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.

        """
