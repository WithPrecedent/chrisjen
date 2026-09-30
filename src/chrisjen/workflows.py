"""Workflow designs.

A workflow is a directed graph (a `holden.System`) of nodes. The graph stores
the names of nodes and a `library` stores the nodes themselves. Each design is
a subclass with its own rules for how the nodes are applied to an item.

Contents:
    Workflow: base class for all designs.
    Waterfall: nodes are applied one after another.
    Kanban: like `Waterfall`, but each stage works on an isolated copy and
        leaves a deliverable.
    Scrum: like `Waterfall`, but the user can advance one node at a time.
    Pert: nodes form a graph with dependencies and a critical path.
    Agile: sequence repeats until a criterion is met.
    Lean: sequence repeats while it keeps improving.
    Contest: tries every alternative path and keeps the best.
    Survey: tries every alternative path and averages the results.
    criterion: decorator that registers a function as a criterion.

"""

from __future__ import annotations

import abc
import copy
import dataclasses
import functools
import itertools
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any, ClassVar

import holden
import wonka

from . import nodes, utilities

if TYPE_CHECKING:
    from collections.abc import Mapping

Branch = list[tuple[str, Callable[..., Any]]]


@dataclasses.dataclass
class Workflow(holden.Storage, holden.System, wonka.Subclasser, abc.ABC):
    """Base class for workflow designs.

    Every design can be built from its snake case class name with `design`
    (for example, `Workflow.design('contest', nodes)`).

    The graph itself (`contents`, an adjacency list of node names) and the
    `library` of node names and nodes come from `holden.System` and
    `holden.Storage`.

    Args:
        name: name of the workflow. Defaults to `None`.
        criteria: function (or the name of a function registered with
            `criterion`) that scores a result. It is used by `Agile`, `Lean`,
            and `Contest`. Defaults to `None`.
        max_iterations: the most times that `Agile` and `Lean` repeat their
            sequence. Defaults to 10.
        tolerance: the smallest improvement `Lean` considers worth another
            iteration. Defaults to 0.0.
        select: whether `Contest` keeps the 'max' or the 'min' score. Defaults
            to 'max'.
        durations: `dict` of node names and their durations, for `Pert`.
            Defaults to an empty `dict`.
        results: `dict` of results from the most recent execution, keyed by
            node or branch name. Defaults to an empty `dict`.

    Attributes:
        aliases: alternative names for designs.
        criteria_registry: functions registered with `criterion`.

    """

    name: str | None = None
    criteria: Callable[[Any], Any] | str | None = None
    max_iterations: int = 10
    tolerance: float = 0.0
    select: str = "max"
    durations: dict[str, float] = dataclasses.field(default_factory = dict)
    results: dict[str, Any] = dataclasses.field(default_factory = dict)
    aliases: ClassVar[dict[str, str]] = {
        "compete": "contest",
        "competition": "contest",
        "sequential": "waterfall",
    }
    criteria_registry: ClassVar[dict[str, Callable[[Any], Any]]] = {}

    """ Class Methods """

    @classmethod
    def design(
        cls,
        item: str,
        contents: Sequence[nodes.Node] = (),
        requirements: Mapping[str, Sequence[str]] | None = None,
        **kwargs: Any,
    ) -> Workflow:
        """Builds a workflow of a named design.

        Args:
            item: name of a design, such as 'waterfall'.
            contents: nodes in the workflow, in their default order.
            requirements: `dict` of node names and the names of nodes that must
                come before them. If it is empty, the nodes are connected in
                sequence. Otherwise, only the listed requirements are
                connected, so nodes without requirements are roots.
            **kwargs: other arguments for the workflow (`name`, `criteria`,
                `max_iterations`, `tolerance`, `select`, or `durations`).

        Raises:
            KeyError: if `item` is not the name of a design.

        Returns:
            A `Workflow` with `contents` added and connected.

        """
        key = cls.aliases.get(item, item)
        try:
            workflow = cls.create(key, parameters = kwargs)
        except KeyError as error:
            known = sorted(wonka.options._KEY_NAMER(s) for s in _all(cls))
            message = (
                f"{item!r} is not a known workflow design. Known designs: "
                f"{', '.join(known)}"
            )
            raise KeyError(message) from error
        workflow.populate(contents, requirements = requirements)
        return workflow

    """ Properties """

    @property
    def sequence(self) -> list[nodes.Node]:
        """Returns the nodes in the order they would be applied.

        Returns:
            The stored nodes in topological order.

        """
        return [self.retrieve(name) for name in self.order()]

    """ Public Methods """

    def critical_path(self) -> tuple[list[str], float]:
        """Returns the longest path through the graph and its length.

        The length of a path is the sum of the `durations` of its nodes. A node
        without a duration counts as 1.

        Returns:
            A `tuple` of the list of node names on the critical path and the
                total duration of the path.

        """
        best: dict[str, tuple[float, list[str]]] = {}
        parents = self._parents()
        for name in self.order():
            duration = self.durations.get(name, 1.0)
            before = max(
                (best[p] for p in parents[name]),
                key = lambda option: option[0],
                default = (0.0, []),
            )
            best[name] = (before[0] + duration, [*before[1], name])
        if not best:
            return [], 0.0
        total, path = max(best.values(), key = lambda option: option[0])
        return path, total

    @abc.abstractmethod
    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Applies the nodes of the workflow to `item`.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the workflow.

        """

    def order(self) -> list[str]:
        """Returns node names in topological order.

        Nodes that could go in either order stay in the order they were added.

        Raises:
            ValueError: if the graph has a cycle.

        Returns:
            A `list` of node names.

        """
        parents = self._parents()
        remaining = list(self.contents)
        ordered: list[str] = []
        while remaining:
            ready = [
                n for n in remaining if all(p in ordered for p in parents[n])
            ]
            if not ready:
                message = f"workflow has a cycle involving {remaining}"
                raise ValueError(message)
            ordered.append(ready[0])
            remaining.remove(ready[0])
        return ordered

    def populate(
        self,
        contents: Sequence[nodes.Node],
        requirements: Mapping[str, Sequence[str]] | None = None,
    ) -> None:
        """Adds nodes to the workflow and connects them.

        Args:
            contents: nodes to add, in their default order.
            requirements: `dict` of node names and the names of nodes that must
                come before them. If it is empty, the nodes are connected in
                sequence. Otherwise, only the listed requirements are
                connected, so nodes without requirements are roots.

        Raises:
            KeyError: if a requirement names a node that is not in `contents`.
            ValueError: if two nodes have the same name or the requirements
                make the graph circular.

        """
        names = [node.name for node in contents]
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if duplicates:
            message = (
                f"the nodes of a workflow must have unique names, but "
                f"{duplicates} appear more than once"
            )
            raise ValueError(message)
        for node in contents:
            self.add(node.name)
            self.store(node.name, node)
        self._wire(names, requirements or {})
        # Finding the order raises an error if the graph has a cycle.
        self.order()

    """ Private Methods """

    def _apply(
        self,
        item: Any,
        names: Sequence[str] | None = None,
        *,
        isolate: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Applies nodes in order, saving each result in `results`.

        Args:
            item: data or object to change.
            names: names of nodes to apply. Defaults to all nodes.
            isolate: whether each node works on a deep copy of its input.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the last node.

        """
        for name in self.order() if names is None else names:
            source = copy.deepcopy(item) if isolate else item
            item = self.retrieve(name).complete(source, **kwargs)
            self.results[name] = item
        return item

    def _branches(self) -> list[tuple[str, Callable[..., Any]]]:
        """Returns every alternative way through the workflow.

        If every node is a `Step`, a branch is one technique for each step (so
        there is a branch for every combination of techniques). Otherwise, each
        node is its own branch.

        Returns:
            A `list` of `tuple` pairs of a branch label and a function that
                applies the branch to an item.

        """
        sequence = self.sequence
        if sequence and all(isinstance(n, nodes.Step) for n in sequence):
            options = [
                [(step, technique) for technique in step.alternatives]
                for step in sequence
            ]
            branches = []
            counts: dict[str, int] = {}
            for combination in itertools.product(*options):
                label = " > ".join(
                    technique.name for _, technique in combination
                )
                # Repeated techniques would otherwise share (and overwrite) a
                # label, which drops paths from `results`.
                counts[label] = counts.get(label, 0) + 1
                if counts[label] > 1:
                    label = f"{label} ({counts[label]})"
                branches.append(
                    (label, functools.partial(_run_combination, combination))
                )
            return branches
        return [(node.name, node.complete) for node in sequence]

    def _criteria(self) -> Callable[[Any], Any]:
        """Returns the criteria function.

        Raises:
            ValueError: if there is no criteria.
            KeyError: if `criteria` names a function that was not registered.

        Returns:
            The criteria function.

        """
        if self.criteria is None:
            message = (
                f"the {self.__class__.__name__.lower()} design needs a "
                f"criteria function: pass criteria or register one with "
                f"@chrisjen.criterion"
            )
            raise ValueError(message)
        if callable(self.criteria):
            return self.criteria
        try:
            return self.criteria_registry[self.criteria]
        except KeyError as error:
            known = ", ".join(sorted(self.criteria_registry)) or "none"
            message = (
                f"{self.criteria!r} is not a registered criterion. "
                f"Registered criteria: {known}"
            )
            raise KeyError(message) from error

    def _parents(self) -> dict[str, set[str]]:
        """Returns a `dict` of node names and the names that point to them."""
        parents: dict[str, set[str]] = {name: set() for name in self.contents}
        for name, children in self.contents.items():
            for child in children:
                parents[child].add(name)
        return parents

    def _wire(
        self, names: Sequence[str], requirements: Mapping[str, Sequence[str]]
    ) -> None:
        """Connects nodes in sequence or according to `requirements`."""
        unknown = {
            r for required in requirements.values() for r in required
        } - set(names)
        if unknown:
            message = f"requirements refer to unknown nodes: {sorted(unknown)}"
            raise KeyError(message)
        if not requirements:
            for previous, name in itertools.pairwise(names):
                self.connect((previous, name))
        for name, required in requirements.items():
            for other in required:
                self.connect((other, name))


@dataclasses.dataclass
class Waterfall(Workflow):
    """Applies nodes one after another.

    This is the default design: a rigid, pre-planned sequence.

    """

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Applies every node in order.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the last node.

        """
        self.results.clear()
        return self._apply(item, **kwargs)


@dataclasses.dataclass
class Kanban(Workflow):
    """Applies nodes one after another with isolated stages.

    Each stage works on a deep copy of the previous deliverable, so a stage
    cannot change what an earlier stage produced. Every deliverable is kept in
    `results`.

    """

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Applies every node in order on isolated copies.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The final deliverable.

        """
        self.results.clear()
        return self._apply(item, isolate = True, **kwargs)


@dataclasses.dataclass
class Scrum(Workflow):
    """Applies nodes one after another, under the user's control.

    Use `advance` to apply one node at a time and inspect or change the item
    between nodes. `execute` applies all of the nodes that remain.

    Attributes:
        position: index of the next node to apply.

    """

    position: int = 0

    """ Properties """

    @property
    def done(self) -> bool:
        """Returns whether every node has been applied."""
        return self.position >= len(self.contents)

    @property
    def upcoming(self) -> str | None:
        """Returns the name of the next node, or `None` if none remain."""
        return None if self.done else self.order()[self.position]

    """ Public Methods """

    def advance(self, item: Any, **kwargs: Any) -> Any:
        """Applies the next node.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the node.

        Raises:
            StopIteration: if every node has been applied.

        Returns:
            The result of the node.

        """
        if self.done:
            raise StopIteration
        name = self.order()[self.position]
        item = self._apply(item, [name], **kwargs)
        self.position += 1
        return item

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Applies all of the nodes that remain and resets the position.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the last node.

        """
        while not self.done:
            item = self.advance(item, **kwargs)
        self.position = 0
        return item


@dataclasses.dataclass
class Pert(Workflow):
    """Applies nodes in an order that respects their dependencies.

    Nodes may depend on more than one earlier node (for example, a step that
    needs the results of two others), which makes parallel paths possible. If
    no requirements are given, the nodes run in sequence.
    `critical_path` finds the sequence of nodes with the longest total
    duration, which determines the shortest possible time to finish.

    """

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Applies every node in dependency order.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the last node.

        """
        self.results.clear()
        return self._apply(item, **kwargs)


@dataclasses.dataclass
class Agile(Workflow):
    """Repeats the sequence of nodes until `criteria` is satisfied.

    After each pass, `criteria` is called with the result. The workflow stops
    when it returns a true value or after `max_iterations` passes.

    Attributes:
        iterations: number of passes made by the most recent execution.

    """

    iterations: int = 0

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Repeats the sequence until `criteria` returns a true value.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The result of the last pass.

        """
        criteria = self._criteria()
        self.results.clear()
        self.iterations = 0
        for _ in range(self.max_iterations):
            item = self._apply(item, **kwargs)
            self.iterations += 1
            if criteria(item):
                break
        return item


@dataclasses.dataclass
class Lean(Workflow):
    """Repeats the sequence of nodes while the score keeps improving.

    After each pass, `criteria` is called with the result. The workflow keeps
    going while the score improves by more than `tolerance` (up to
    `max_iterations` passes) and returns the best result.

    Attributes:
        iterations: number of passes made by the most recent execution.
        score: the best score from the most recent execution.

    """

    iterations: int = 0
    score: float | None = None

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Repeats the sequence until the score stops improving.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The best result.

        """
        criteria = self._criteria()
        self.results.clear()
        self.iterations = 0
        self.score = None
        best = item
        current = item
        for _ in range(self.max_iterations):
            candidate = self._apply(copy.deepcopy(current), **kwargs)
            self.iterations += 1
            score = criteria(candidate)
            if self.score is None:
                best, self.score, current = candidate, score, candidate
                continue
            improvement = score - self.score
            if improvement > 0:
                best, self.score, current = candidate, score, candidate
            if improvement <= self.tolerance:
                break
        return best


@dataclasses.dataclass
class Comparative(Workflow, abc.ABC):
    """Base class for designs that compare alternative paths.

    If every node is a `Step`, a path takes one technique from each step, so
    there is a path for every combination of techniques. Otherwise, each node
    is its own path. Each path works on a deep copy of the item.

    """

    def compare(self, item: Any, **kwargs: Any) -> dict[str, Any]:
        """Applies every path to a copy of `item`.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            A `dict` of path labels and the result of each path.

        """
        self.results = {
            label: function(copy.deepcopy(item), **kwargs)
            for label, function in self._branches()
        }
        return self.results


@dataclasses.dataclass
class Contest(Comparative):
    """Tries every alternative path and keeps the best result.

    Attributes:
        scores: `dict` of path labels and their scores from the most recent
            execution.
        winner: label of the winning path from the most recent execution.

    """

    scores: dict[str, Any] = dataclasses.field(default_factory = dict)
    winner: str | None = None

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Returns the result of the path with the best score.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Raises:
            ValueError: if `select` is not 'max' or 'min', or there are no
                paths to compare.

        Returns:
            The best result. Ties go to the first path.

        """
        select = str(self.select).lower()
        if select not in {"max", "min"}:
            message = f"select must be 'max' or 'min', not {self.select!r}"
            raise ValueError(message)
        criteria = self._criteria()
        results = self.compare(item, **kwargs)
        if not results:
            message = "there are no paths to compare"
            raise ValueError(message)
        self.scores = {label: criteria(r) for label, r in results.items()}
        choose = max if select == "max" else min
        self.winner = choose(self.scores, key = lambda label: self.scores[label])
        return results[self.winner]


@dataclasses.dataclass
class Survey(Comparative):
    """Tries every alternative path and averages the results.

    The results must support addition and division by an `int`, as numbers,
    `numpy` arrays, and `pandas` objects do.

    """

    def execute(self, item: Any, **kwargs: Any) -> Any:
        """Returns the mean of the results of every path.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments passed to the nodes.

        Returns:
            The average result.

        """
        return utilities.average(list(self.compare(item, **kwargs).values()))


def criterion(
    function: Callable[[Any], Any] | None = None, *, name: str | None = None
) -> Any:
    """Registers a function as a criterion for a workflow design.

    A criterion takes a result and returns a score (for `Contest` and `Lean`)
    or a `bool` (for `Agile`). Registered criteria can be named in settings
    with a `criteria` option.

    ```py
    @chrisjen.criterion
    def accuracy(result):
        return result.score
    ```

    Args:
        function: function to register.
        name: name to register the function under. Defaults to the function's
            `__name__`.

    Returns:
        The function itself, so that it can still be used directly. If
            `function` is `None`, a decorator is returned.

    """

    def register(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
        Workflow.criteria_registry[name or func.__name__] = func
        return func

    return register if function is None else register(function)


def _run_combination(
    combination: Sequence[tuple[nodes.Step, nodes.Technique]],
    item: Any,
    **kwargs: Any,
) -> Any:
    """Applies one technique from each step, in order."""
    for step, technique in combination:
        item = step.run(technique, item, **kwargs)
    return item


def _all(cls: type) -> list[type]:
    """Returns all subclasses of `cls`, including indirect ones."""
    found: list[type] = []
    for subclass in cls.__subclasses__():
        found.append(subclass)
        found.extend(_all(subclass))
    return found


__all__: list[str] = [
    "Agile",
    "Comparative",
    "Contest",
    "Kanban",
    "Lean",
    "Pert",
    "Scrum",
    "Survey",
    "Waterfall",
    "Workflow",
    "criterion",
]
