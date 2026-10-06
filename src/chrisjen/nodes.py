"""Nodes of a workflow: the subclasses of `base.Vertex`.

Contents:
    Technique: a single action that wraps a tool.
    NullVertex: a `Vertex` that does nothing.
    Step: a stage of a workflow that wraps a technique or a worker.
    Worker: base class for the designs in the `workers` module, which are
        vertexes that are graphs of other vertexes.

"""

from __future__ import annotations

import abc
import copy
import dataclasses
from collections.abc import Callable, Hashable, MutableMapping, Sequence
from typing import Any

import holden

from . import base, utilities


@dataclasses.dataclass
class Technique(base.Vertex):
    """A single action in a workflow, which usually wraps another tool.

    A `Technique` is an ordinary object. Its `contents` is the tool that it
    wraps: any callable, or the import path of one, such as
    `statistics.fmean`. A path is only imported when the technique is first
    used, so techniques can wrap optional packages. A subclass can set a
    default `contents` or override `implement` instead. Subclasses are stored
    in the library under their snake case names, which is how settings refer
    to them.

    Args:
        name: name used to refer to the technique in a workflow.
        contents: the tool to wrap: a callable or the import path of one.
            Defaults to `None`, which is only useful for subclasses that
            override `implement`.
        parameters: keyword arguments passed to the tool. Defaults to an empty
            `dict`.

    """

    name: str | None = dataclasses.field(default = None)
    contents: str | Callable[..., Any] | None = dataclasses.field(
        default = None)
    parameters: base.GenericDict = dataclasses.field(default_factory = dict)

    """ Public Methods """

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Calls the wrapped tool with `item`.

        Override this method to call a tool differently (for example, to build
        an object from the parameters and then call one of its methods).

        Args:
            item: data or object to change.
            **kwargs: keyword arguments for the tool. Any that the tool does
                not accept are dropped.

        Raises:
            ImportError: if `contents` is an import path that cannot be
                imported.
            NotImplementedError: if there is no tool in `contents` and a
                subclass does not override this method.
            TypeError: if the tool is not callable.

        Returns:
            The changed `item`.

        """
        tool = self.contents
        if isinstance(tool, str):
            tool = utilities.import_object(tool)
        if tool is None:
            message = (
                f'technique {self.name!r} has no tool: pass a callable or '
                f'import path as contents or override implement in a subclass'
            )
            raise NotImplementedError(message)
        if not callable(tool):
            message = (
                f'technique {self.name!r} wraps {tool!r}, which is not '
                f'callable: override implement to use it'
            )
            raise TypeError(message)
        return tool(item, **utilities.accepted_arguments(tool, kwargs))

    """ Dunder Methods """

    def __deepcopy__(self, memo: dict[int, Any]) -> Technique:
        """Copies the technique, sharing a tool that cannot be copied.

        Everything is copied, including a tool in `contents` (so that a tool
        with its own state, such as a model, is not shared). If the tool cannot
        be copied (because it holds a lock or a connection, for example), the
        copy uses the same tool.

        Args:
            memo: `dict` of objects already copied.

        Returns:
            A copy of the technique.

        """
        clone = copy.copy(self)
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            try:
                value = copy.deepcopy(value, memo)
            except Exception:
                if field.name != 'contents':
                    raise
            setattr(clone, field.name, value)
        return clone


@dataclasses.dataclass
class NullVertex(base.Vertex):
    """A Vertex that does nothing.

    This node is stored in the library as "none" (and as "null_vertex").

    This is a useful node when you want to compare using one technique with
    making no changes.

    Args:
        name: name used to refer to the node in a workflow. Defaults to
            "none".

    """

    name: str = dataclasses.field(default = 'none')

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Returns `item` unchanged.

        Args:
            item: data or object.
            **kwargs: ignored.

        Returns:
            `item`.

        """
        return item


# Lets settings refer to a `NullVertex` as "none".
base.library.add(NullVertex, name = 'none')


@dataclasses.dataclass
class Step(base.Vertex, abc.ABC):
    """A stage of a workflow that wraps a technique or a worker.

    Unlike a simple Technique, a Step includes preparatory and finishing code
    (in the `begin` and `end` methods). Subclasses of Step can store methods
    and attributes shared by all of the techniques that a step might use,
    which is useful when a worker compares several techniques for the same
    step. When a workflow is built from settings, each technique of a step is
    wrapped in its own step node, named "{technique}_{step}", and a subclass
    named after the step (such as `Scale` for "scale") is used if there is
    one.

    A Step returns the attributes of `contents` that it does not have itself.

    Args:
        name: name used to refer to the step in a workflow.
        contents: the technique or worker to wrap. Defaults to `None`, which
            is only useful for subclasses that override `implement`.
        parameters: keyword arguments for the step to use. Defaults to an empty
            `dict`.

    """

    name: str | None = None
    contents: Technique | Worker | None = None
    parameters: base.GenericDict = dataclasses.field(default_factory = dict)

    """ Public Methods """

    def begin(self, item: Any) -> Any:
        """Runs any preparation needed for the step.

        Args:
            item: data or object to change.

        Returns:
            The item in a prepared state.

        """
        return item

    def end(self, item: Any) -> Any:
        """Finalizes the step's execution.

        Args:
            item: data or object to change.

        Returns:
            The final result of the step.

        """
        return item

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies the technique or worker in `contents` to `item`.

        Parameter priority, from lowest to highest, is the `parameters` of
        `contents`, the step's `parameters`, and `kwargs`.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments for the `apply` method of `contents`.

        Raises:
            ValueError: if there is nothing in `contents`.

        Returns:
            The result of `begin`, the `apply` method of `contents`, and
                `end`.

        """
        if self.contents is None:
            message = (
                f'step {self.name!r} has no technique or workflow in contents'
            )
            raise ValueError(message)
        item = self.begin(item)
        item = self.contents.apply(item, **kwargs)
        return self.end(item)

    """ Dunder Methods """

    def __getattr__(self, attribute: str) -> Any:
        """Returns an attribute of `contents` that the step does not have.

        Args:
            attribute: name of the attribute.

        Raises:
            AttributeError: if neither the step nor `contents` has `attribute`.

        Returns:
            The attribute of `contents`.

        """
        # Dunder and private attributes are not passed on, so that copying
        # and comparing a step use the step's own methods. 'contents' is also
        # not passed on, which avoids endless recursion before it is set.
        if attribute.startswith('_') or attribute == 'contents':
            raise AttributeError(attribute)
        return getattr(self.contents, attribute)


@dataclasses.dataclass
class Worker(holden.System, base.Vertex, abc.ABC):
    """Base class for nodes that are workflows of other nodes.

    A worker is a directed graph (a `holden.System`) whose nodes are vertexes.
    Each subclass is a design with its own rules for how the nodes are
    connected (`populate`) and applied to an item (`implement`). Workers are
    hashed and compared by name, like other vertexes, so a worker can be a
    node in another worker.

    Args:
        name: name used to refer to the worker in a workflow.
        contents: the graph: a `dict` mapping each node to the `set` of nodes
            that come after it. Defaults to an empty `dict`.
        parameters: keyword arguments for the worker to use. Defaults to an
            empty `dict`.

    """

    name: str | None = None
    contents: MutableMapping[Hashable, set[Hashable]] = dataclasses.field(
        default_factory = dict)
    parameters: base.GenericDict = dataclasses.field(default_factory = dict)

    # Workers are hashed and compared by name, like other vertexes, so that
    # they can be nodes in other workers.
    __eq__ = base.Vertex.__eq__
    __hash__ = base.Vertex.__hash__

    """ Public Methods """

    def populate(
        self,
        nodes: Sequence[base.Vertex | Sequence[base.Vertex]]) -> None:
        """Adds `nodes` to the graph, each one after the one before it.

        Args:
            nodes: vertexes to add, in order. An item may also be a list of
                vertexes (such as the techniques of a step), which are added
                one after another as well.

        """
        previous = None
        for item in nodes:
            layer = item if isinstance(item, list) else [item]
            for node in layer:
                self.add(node)
                if previous is not None:
                    self.connect((previous, node))
                previous = node

    @abc.abstractmethod
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies the nodes to `item`, so that the worker can be a node.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the workflow.

        """

