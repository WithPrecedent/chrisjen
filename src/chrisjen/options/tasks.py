"""Primitive task nodes for chrisjen workflows.

Contents:
    Step
    Technique

"""
from __future__ import annotations

import dataclasses
from collections.abc import Callable, Hashable, MutableMapping
from typing import Any

from .. import nodes


@dataclasses.dataclass
class Step(nodes.Task):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful
    when creating branching, parallel workflows which test a variety of
    strategies with similar or identical parameters and/or methods.

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

    """ Properties """

    @property
    def technique(self) -> Technique | None:
        """_summary_

        Returns:
            Optional[Technique]: _description_
        """
        return self.contents

    @technique.setter
    def technique(self, value: Technique) -> None:
        """_summary_

        Args:
            value (Technique): _description_

        Returns:
            _type_: _description_
        """
        self.contents = value
        return self

    @technique.deleter
    def technique(self) -> None:
        """Deletes the technique stored in `contents`."""
        self.contents = None
        return self

    """ Public Methods """

    # @classmethod
    # def create(
    #     cls,
    #     name: str,
    #     technique: str,
    #     project: nodes.Project,
    #     **kwargs: base.Kwargs) -> Technique:
    #     """Creates a Task instance based on passed arguments.

    #     Returns:
    #         Task: an instance based on passed arguments.

    #     """
    #     contents = project.manager.librarian.acquire(name = technique)
    #     return cls(name = name, contents = contents, **kwargs)

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
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if hasattr(self.parameters, 'finalize'):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if self.technique.parameters:
                if hasattr(self.technique.parameters, 'finalize'):
                    self.technique.parameters.finalize(project = project)
                technique_parameters = self.technique.parameters
                parameters.update(technique_parameters)
            self.technique.implement(item = item, **parameters)
        return item


@dataclasses.dataclass
class Technique(nodes.Task):
    """Primitive node for single task execution.

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
    step: Step | None = None

    """ Properties """

    @property
    def algorithm(self) -> Callable[..., Any | None] | None:
        """_summary_

        Returns:
            Callable[..., Any | None] | None: _description_

        """
        return self.contents

    @algorithm.setter
    def algorithm(self, value: Callable[..., Any | None]) -> None:
        self.contents = value
        return self

    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self

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
class Contractor(nodes.Task):
    """Base class for making multiple instances of a project.

    Args:
        name: designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents: stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters: parameters to be attached to
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
class Judge(nodes.Task):
    """Base class for selecting a node or path.

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
class Scorer(nodes.Task):
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
    score_attribute: str | None = None

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
        try:
            item = self.contents.complete(item = item, **kwargs)
        except AttributeError:
            item = self.contents(item, **kwargs)
        return item
