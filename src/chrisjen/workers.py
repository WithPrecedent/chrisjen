"""Worker designs.

A worker is a directed graph (a `holden.System`) of nodes. Each design is a
subclass with its own rules for how the nodes are connected (`populate`) and
applied to an item (`implement`). Designs are found by their snake case names,
which are used for the "design" setting.

Contents:
    Flow: nodes are applied one after another.
    Benchmark: the sequence repeats until a criterion is met.
    Comparator: mixin for workers that compare every combination of
        alternatives.
    Contest: tries every combination of alternatives and keeps the best.
    Survey: tries every combination of alternatives and averages the results.

"""

from __future__ import annotations

import abc
import copy
import dataclasses
from collections.abc import Hashable, MutableMapping, Sequence
from typing import Any

from . import base, nodes, utilities


@dataclasses.dataclass
class Flow(nodes.Worker):
    """Applies nodes one after another.

    This is the default design: a rigid, pre-planned sequence. If a step has
    more than one technique, they are applied one after another as well.

    Args:
        name: name used to refer to the worker in a workflow.
        contents: the graph of nodes. Defaults to an empty `dict`.
        parameters: keyword arguments for the worker to use. Defaults to an
            empty `dict`.

    """

    """ Public Methods """

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies each node, in order, to `item`.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the last node.

        """
        for path in self.walk():
            item = utilities._apply_path(path, item, **kwargs)
        return item


@dataclasses.dataclass
class Benchmark(Flow):
    """Repeats the sequence of nodes until `criteria` is met.

    After each pass, `criteria` tests the result. The worker stops when the
    test passes or after `max_iterations` passes. In settings, `criteria` is
    named by the "criterion" setting, and "max_iterations" can be set as well.

    Args:
        name: name used to refer to the worker in a workflow.
        contents: the graph of nodes. Defaults to an empty `dict`.
        parameters: keyword arguments for the worker to use. Defaults to an
            empty `dict`.
        criteria: the criteria that decide when to stop. Defaults to `None`.
        max_iterations: most passes to make. If `None`, passes are made until
            `criteria` is met. Defaults to `None`.

    Attributes:
        iterations: number of passes made by the most recent call.

    """

    criteria: base.Criteria | None = None
    max_iterations: int | None = None
    iterations: int = 0

    """ Public Methods """

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Repeats the sequence until `criteria` is met.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Raises:
            ValueError: if there is no `criteria`.

        Returns:
            The result of the last pass.

        """
        if self.criteria is None:
            message = f'benchmark {self.name!r} needs criteria'
            raise ValueError(message)
        self.iterations = 0
        while (
            self.max_iterations is None
            or self.iterations < self.max_iterations):
            item = super().implement(item, **kwargs)
            self.iterations += 1
            if self.criteria.test(item):
                break
        return item


# `eq` is `False` so that the mixin does not set `__hash__` to `None`, which
# would stop workers that use it from being hashed by name.
@dataclasses.dataclass(eq = False)
class Comparator(abc.ABC):  # noqa: B024
    """Mixin for workers that compare every combination of alternatives.

    The techniques of each step are alternatives to each other, and the paths
    through the graph are every combination of one technique from each step
    (see `populate`). A worker without steps has one path for each of its
    techniques. List the mixin before `Worker` in the bases of a design.

    Args:
        contents: the graph of nodes. Defaults to an empty `dict`.
        name: name used to refer to the worker in a workflow. Defaults to
            `None`.
        parameters: keyword arguments for the worker to use. Defaults to an
            empty `dict`.
        criteria: the criteria used to score the result of each path.
            Defaults to `None`.

    Attributes:
        results: the result of each path in the most recent call, by the
            names of the nodes in the path (joined by " > ").

    """
    contents: MutableMapping[Hashable, set[Hashable]] = dataclasses.field(
        default_factory = dict)
    name: str | None = dataclasses.field(default = None)
    parameters: base.GenericDict = dataclasses.field(default_factory = dict)
    criteria: base.Criteria | None = None
    results: dict[str, Any] = dataclasses.field(default_factory = dict)

    """ Public Methods """

    def compare(self, items: Sequence[Any]) -> list[Any]:
        """Returns the score of each item in `items`.

        Args:
            items: results to score.

        Raises:
            ValueError: if there is no `criteria`.

        Returns:
            The scores, in the same order as `items`.

        """
        if self.criteria is None:
            message = f'{self.name!r} needs criteria to compare results'
            raise ValueError(message)
        return [self.criteria.score(item) for item in items]

    def populate(
        self,
        nodes: Sequence[base.Vertex | Sequence[base.Vertex]]) -> None:
        """Adds `nodes` so that every combination of alternatives is a path.

        Each item in `nodes` is a list of alternatives (such as the techniques
        of a step) or a single vertex. Every vertex in an item is connected to
        every vertex in the next item, so the paths through the graph are every
        combination of one vertex from each item.

        Args:
            nodes: vertexes and lists of alternative vertexes, in order.

        """
        previous = []
        for item in nodes:
            layer = item if isinstance(item, list) else [item]
            for node in layer:
                self.add(node)
                for before in previous:
                    self.connect((before, node))
            previous = layer

    def try_paths(self, item: Any, **kwargs: Any) -> dict[str, Any]:
        """Applies every path to its own copy of `item`.

        Each path also uses its own copies of its nodes, so that nothing they
        store (such as a fitted model) carries over from one path to another.

        Args:
            item: data or object to change. It is not changed itself.
            **kwargs: keyword arguments passed to the nodes.

        Raises:
            ValueError: if there are no paths.

        Returns:
            The result of each path, which is also stored in `results`.

        """
        paths = self.walk()
        if not paths:
            message = f'{self.name!r} has no paths to compare'
            raise ValueError(message)
        self.results = {}
        for path in paths:
            label = ' > '.join(node.name for node in path)
            copies = [copy.deepcopy(node) for node in path]
            self.results[label] = utilities._apply_path(
                copies, copy.deepcopy(item), **kwargs)
        return self.results


@dataclasses.dataclass
class Contest(Comparator, nodes.Worker):
    """Tries every combination of alternatives and keeps the best result.

    Each path (every combination of one technique from each step) is applied
    to its own copy of the item, and the result with the highest score from
    `criteria` is kept.

    Args:
        name: name used to refer to the worker in a workflow.
        contents: the graph of nodes. Defaults to an empty `dict`.
        parameters: keyword arguments for the worker to use. Defaults to an
            empty `dict`.
        criteria: the criteria used to score each result. Higher scores are
            better. Defaults to `None`.

    Attributes:
        winner: label of the path with the best result in the most recent
            call.

    """

    winner: str | None = None

    """ Public Methods """

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Returns the result of the path with the best score.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Raises:
            ValueError: if there are no paths or no `criteria`.

        Returns:
            The best result. Ties go to the first path.

        """
        results = self.try_paths(item, **kwargs)
        scores = self.compare(list(results.values()))
        best = scores.index(max(scores))
        self.winner = list(results)[best]
        return results[self.winner]


@dataclasses.dataclass
class Survey(Comparator, nodes.Worker):
    """Tries every combination of alternatives and averages the results.

    Each path (every combination of one technique from each step) is applied
    to its own copy of the item. The results must support addition and
    division by an `int`, as numbers, `numpy` arrays, and `pandas` objects do.

    Args:
        name: name used to refer to the worker in a workflow.
        contents: the graph of nodes. Defaults to an empty `dict`.
        parameters: keyword arguments for the worker to use. Defaults to an
            empty `dict`.

    Attributes:
        average: the average result of the most recent call.

    """

    average: Any = None

    """ Public Methods """

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Returns the mean of the results of every path.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Raises:
            ValueError: if there are no paths.

        Returns:
            The average result.

        """
        results = self.try_paths(item, **kwargs)
        self.average = utilities._average(list(results.values()))
        return self.average
