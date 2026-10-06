"""Interface for creating and running a project.

Contents:
    Project: the universal interface for `chrisjen` projects.

"""

from __future__ import annotations

import dataclasses
import inspect
import pathlib
from collections.abc import MutableMapping
from typing import Any

import camina
import nagata

from . import base, nodes, options, utilities, workshop


@dataclasses.dataclass
class Project:
    """Creates a workflow from settings and applies it.

    A project moves through two stages:

    1. `draft`: the settings (`idea`) are turned into a `workflow`.
    2. `apply`: the workflow is applied to an item.

    Creating a `Project` drafts it. If `automatic` is `True`, the project is
    also applied.

    Use the `create` class method to create a Project instance unless you are
    passing all the arguments to the `Project` instance. The `create` method
    is more flexible and converts datatypes, validates arguments, and loads
    appropriate files and classes.

    Args:
        name: name of the project.
        id: unique name for this run of the project.
        automatic: whether to apply the project as soon as it is created.
        library: library of the classes used to build the workflow.
        clerk: file manager for the project's files.
        idea: settings that describe the project.
        workflow: the workflow of the project. Defaults to `None`, in which
            case it is built by `draft`.
        report: report generated after the project is applied. Defaults to
            `None`, in which case `options._DEFAULT_REPORT` is used.
        item: data or object that the workflow is applied to. Defaults to
            `None`.

    Attributes:
        result: the result of the last call to `apply`.

    """

    name: str
    id: str
    automatic: bool
    library: base.Library = dataclasses.field(repr = False)
    clerk: nagata.FileManager = dataclasses.field(repr = False)
    idea: base.Idea = dataclasses.field(repr = False)
    workflow: nodes.Worker | None = dataclasses.field(
        default = None, repr = False)
    report: base.Report | None = dataclasses.field(default = None, repr = False)
    item: Any = dataclasses.field(default = None, repr = False)
    result: Any = dataclasses.field(default = None, init = False, repr = False)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Drafts the project and applies it, if `automatic` is `True`."""
        if self.report is None:
            self.report = self.library.all[options._DEFAULT_REPORT]()
        if self.workflow is None:
            self.draft()
        if self.automatic:
            self.apply()

    """ Class Methods """

    @classmethod
    def create(
        cls,
        idea: base.Idea | MutableMapping[str, Any] | pathlib.Path | str,
        *,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        automatic: bool = True,
        library: base.Library = base.library,
        clerk: nagata.FileManager | pathlib.Path | str | None = None,
        **kwargs: Any) -> Project:
        """Creates a project.

        Every argument after `idea` must be passed by keyword.

        Args:
            idea: settings that describe the project: an `Idea`, a `dict`, or
                the path to a settings file.
            name: name of the project. Defaults to `None`, in which case it is
                found in `idea`.
            id: unique name for this run. Defaults to `None`, in which case it
                is the name of the project and the current date and time.
            automatic: whether to apply the project as soon as it is created.
                Defaults to `True`.
            library: library of the classes used to build the workflow.
                Defaults to `base.library`.
            clerk: file manager, or the root folder for one. Defaults to
                `None`, in which case `options._DEFAULT_ROOT` is used.
            **kwargs: other arguments for `Project`.

        Returns:
            A `Project` instance.

        """
        idea = _validate_idea(idea)
        name = _validate_name(name, idea)
        return cls(
            name = name,
            id = _validate_id(id, name),
            automatic = automatic,
            library = library,
            clerk = _validate_clerk(clerk, idea),
            idea = idea,
            **kwargs)

    """ Public Methods """

    def apply(self, item: Any = None, **kwargs: Any) -> Any:
        """Applies the workflow to `item` and generates the report.

        Args:
            item: data or object to change. Defaults to `None`, in which case
                the project's `item` is used.
            **kwargs: keyword arguments passed to the nodes in the workflow.

        Returns:
            The result of the workflow, which is also stored in `result`.

        """
        if item is None:
            item = self.item
        self.result = self.workflow.apply(item, **kwargs)
        self.report.generate(self)
        return self.result

    def draft(self) -> None:
        """Builds the `workflow` from the settings."""
        self.workflow = workshop.build_workflow(self)

    def to_dot(
        self,
        path: pathlib.Path | str | None = None,
        name: str | None = None) -> str:
        """Returns the workflow as a Graphviz dot `str`.

        Args:
            path: file to save the text to. Defaults to `None`.
            name: name of the graph. Defaults to the name of the project.

        Returns:
            The dot text.

        """
        return self.workflow.to_dot(path = path, name = name or self.name)

    def to_mermaid(
        self,
        path: pathlib.Path | str | None = None,
        name: str | None = None) -> str:
        """Returns the workflow as a mermaid flowchart `str`.

        Args:
            path: file to save the text to. Defaults to `None`.
            name: name of the chart. Defaults to the name of the project.

        Returns:
            The mermaid text.

        """
        return self.workflow.to_mermaid(path = path, name = name or self.name)

""" Private Functions """

def _validate_clerk(
    clerk: nagata.FileManager | pathlib.Path | str | None,
    idea: base.Idea) -> nagata.FileManager:
    """Returns a file manager for the project.

    Args:
        clerk: file manager, or the root folder for one, or `None`.
        idea: settings of the project. Its "files" section, if any, holds
            arguments for the file manager.

    Returns:
        A file manager.

    """
    if isinstance(clerk, nagata.FileManager):
        return clerk
    root = options._DEFAULT_ROOT if clerk is None else pathlib.Path(clerk)
    manager = options._DEFAULT_CLERK
    settings = utilities.accepted_arguments(manager, idea.get('files', {}))
    return manager(root_folder = root, **settings)


def _validate_id(id: str | None, name: str) -> str:  # noqa: A002
    """Returns `id` or a new one made from `name` and the time.

    Args:
        id: unique name for this run, or `None`.
        name: name of the project.

    Returns:
        The id of the project.

    """
    if id is None:
        # Seconds are included so that two projects created within a minute
        # do not share a folder.
        id = camina.how_soon_is_now(
            prefix = f'{name}_', time_format = '%Y-%m-%d_%H-%M-%S')
    return id


def _validate_idea(
    idea: base.Idea | MutableMapping[str, Any] | pathlib.Path | str,
) -> base.Idea:
    """Returns `idea` as an `Idea`.

    Args:
        idea: an `Idea`, a `dict`, or the path to a settings file.

    Returns:
        An `Idea` instance.

    """
    if isinstance(idea, base.Idea):
        return idea
    if inspect.isclass(idea) and issubclass(idea, base.Idea):
        return idea()
    return base.Idea.create(idea)


def _validate_name(name: str | None, idea: base.Idea) -> str:
    """Verifies the project name.

    If `name` is `None`, the name is found in `idea`: it is the part before
    "_project" of the first section whose name ends in "_project" or, if there
    is none, the name of the first section that is not special (such as
    "files").

    Args:
        name: the project name, or `None`.
        idea: the project settings.

    Raises:
        ValueError: if `name` is `None` and no name is found in `idea`.

    Returns:
        The validated project name.

    """
    if name is None:
        for key in idea:
            if key.endswith('_project'):
                return key.removesuffix('_project')
        for key in idea:
            if key not in options._SPECIAL_SETTINGS:
                return key
        message = 'A Project name was not given and could not be found in idea'
        raise ValueError(message)
    return name
