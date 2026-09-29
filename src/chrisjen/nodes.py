"""Nodes in a workflow.

Contents:
    Node: base class for anything that can be applied to an item in a
        workflow.
    Technique: a single action, either a function or a subclass with its own
        `implement` method.
    NullNode: a `Technique` that does nothing.
    Step: a stage of a workflow with one or more techniques.
    Worker: a node with a workflow of its own.
    technique: decorator that registers a function as a `Technique`.

"""

from __future__ import annotations

import abc
import dataclasses
from collections.abc import Callable, MutableMapping, MutableSequence
from typing import TYPE_CHECKING, Any, ClassVar

import holden
import wonka

from . import utilities

if TYPE_CHECKING:
    from . import workflows


@dataclasses.dataclass
class Node(holden.Labeled, wonka.Subclasser, abc.ABC):
    """Base class for nodes in a chrisjen workflow.

    Nodes are hashed and compared by `name`. Every subclass can be built from
    its snake case class name with `create` (a `wonka` factory method). For
    example, `Technique.create('slice', parameters = {'name': 'slice'})`
    returns an instance of a `Technique` subclass named `Slice`.

    Args:
        name: name used to refer to the node in a workflow. Defaults to `None`,
            in which case the name is inferred from the class or `contents`.
        contents: item(s) to be applied to the `item` passed to `complete`.
            Defaults to `None`.
        parameters: keyword arguments passed to `implement` by `complete`.
            Defaults to an empty `dict`.

    """

    name: str | None = None
    contents: Any | None = None
    parameters: MutableMapping[str, Any] = dataclasses.field(
        default_factory=dict
    )

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Makes subclass instances hashable by `name`.

        `dataclasses` does not inherit `__hash__` and `__eq__` from parent
        classes, so they are copied to every subclass before it is decorated.

        """
        super().__init_subclass__(*args, **kwargs)
        cls.__hash__ = holden.Labeled.__hash__
        cls.__eq__ = holden.Labeled.__eq__

    """ Properties """

    @property
    def alternatives(self) -> list[Node]:
        """Returns the nodes that can be swapped for this one in a contest.

        Returns:
            A `list` containing this node. A `Step` returns its techniques.

        """
        return [self]

    """ Public Methods """

    def complete(self, item: Any, **kwargs: Any) -> Any:
        """Applies this node to `item`.

        Args:
            item: data or object (often the result of the previous node) to
                which this node should be applied.
            **kwargs: keyword arguments for `implement` that take precedence over
                `parameters`.

        Returns:
            The result of applying this node to `item`.

        """
        return self.implement(item, **{**self.parameters, **kwargs})

    @abc.abstractmethod
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies `contents` to `item`.

        Args:
            item: data or object to which `contents` should be applied.
            **kwargs: parameters for the implementation.

        Returns:
            The result of applying `contents` to `item`.

        """


@dataclasses.dataclass
class Technique(Node):
    """A single action in a workflow.

    A `Technique` can be made in three ways:

    1. Register a function with the `technique` decorator. The function must
       accept `item` as its first argument and returns the changed `item`.
       Only the keyword parameters that the function accepts are passed.
    2. Subclass `Technique` and override `implement`. The subclass is found
       automatically by its snake case class name.
    3. Pass a function as `contents` when creating an instance.

    Args:
        name: name used to refer to the technique in a workflow.
        contents: function to call with `item`. Defaults to `None`.
        parameters: keyword arguments passed to `contents`. Defaults to an
            empty `dict`.

    Attributes:
        functions: functions registered with the `technique` decorator.
        aliases: alternative names for techniques.

    """

    contents: Callable[..., Any] | None = None
    functions: ClassVar[dict[str, Callable[..., Any]]] = {}
    aliases: ClassVar[dict[str, str]] = {
        "none": "null_node",
        "null": "null_node",
    }

    """ Class Methods """

    @classmethod
    def create(
        cls,
        item: str,
        parameters: MutableMapping[Any, Any] | None = None,
        **kwargs: Any,
    ) -> Technique:
        """Creates a technique by name.

        Args:
            item: name of a function registered with `technique`, a snake case
                `Technique` subclass name, or an alias.
            parameters: arguments for the created instance (such as `name` or
                `parameters`). Defaults to `None`.
            **kwargs: additional keyword arguments for `wonka`.

        Raises:
            KeyError: if `item` matches no known technique.

        Returns:
            A `Technique` instance.

        """
        parameters = dict(parameters or {})
        parameters.setdefault("name", item)
        if item in cls.functions:
            return cls(contents=cls.functions[item], **parameters)
        key = cls.aliases.get(item, item)
        try:
            return super().create(key, parameters=parameters, **kwargs)
        except KeyError as error:
            known = sorted(
                {*cls.functions, *cls.aliases, *_subclass_names(cls)}
            )
            message = (
                f"{item!r} is not a known technique: define a Technique "
                f"subclass or register a function with @chrisjen.technique. "
                f"Known techniques: {', '.join(known)}"
            )
            raise KeyError(message) from error

    """ Public Methods """

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Calls `contents` with `item`.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments for `contents`. Any that `contents` does
                not accept are dropped.

        Raises:
            NotImplementedError: if there is no function in `contents` and a
                subclass does not override this method.

        Returns:
            The changed `item`.

        """
        if self.contents is None:
            message = (
                f"technique {self.name!r} has no function: pass a function as "
                f"contents or override implement in a subclass"
            )
            raise NotImplementedError(message)
        arguments = utilities.accepted_arguments(self.contents, kwargs)
        return self.contents(item, **arguments)


@dataclasses.dataclass
class NullNode(Technique):
    """A technique that does nothing.

    It is included for comparisons where doing nothing is one of the options
    (e.g., a "none" technique among techniques for scaling data). It is
    available as "none", "null", and "null_node".

    """

    name: str | None = "none"

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Returns `item` unchanged.

        Args:
            item: data or object.
            **kwargs: ignored.

        Returns:
            `item`.

        """
        return item


@dataclasses.dataclass
class Step(Node):
    """A stage of a workflow with one or more techniques.

    In sequential designs, every technique is applied in order. In comparative
    designs (`Contest` and `Survey`), the techniques are alternatives.

    Args:
        name: name used to refer to the step in a workflow.
        contents: techniques in the step. Defaults to an empty `list`.
        parameters: keyword arguments shared by all of the techniques.
            Parameters set on a technique take precedence. Defaults to an empty
            `dict`.

    """

    contents: MutableSequence[Technique] = dataclasses.field(
        default_factory=list
    )

    """ Properties """

    @property
    def alternatives(self) -> list[Node]:
        """Returns the techniques of the step.

        Returns:
            The techniques in `contents`.

        """
        return list(self.contents)

    """ Public Methods """

    def complete(self, item: Any, **kwargs: Any) -> Any:
        """Applies every technique in order.

        Unlike other nodes, the step's `parameters` are not merged into
        `kwargs` here. They are the lowest precedence defaults in `run`.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments for the techniques.

        Returns:
            The result of the last technique.

        """
        return self.implement(item, **kwargs)

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies every technique in order.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments for the techniques.

        Returns:
            The result of the last technique.

        """
        for technique in self.contents:
            item = self.run(technique, item, **kwargs)
        return item

    def run(self, technique: Technique, item: Any, **kwargs: Any) -> Any:
        """Applies one technique with the parameters of the step.

        Parameter precedence, from lowest to highest, is the step's
        `parameters`, the technique's `parameters`, and `kwargs`.

        Args:
            technique: technique to apply.
            item: data or object to change.
            **kwargs: keyword arguments for the technique.

        Returns:
            The result of applying `technique` to `item`.

        """
        parameters = {**self.parameters, **technique.parameters, **kwargs}
        return technique.implement(item, **parameters)


@dataclasses.dataclass
class Worker(Node):
    """A node with a workflow of its own.

    Args:
        name: name used to refer to the worker in a workflow.
        contents: the worker's workflow. Defaults to `None`.
        parameters: keyword arguments passed to every node in the workflow.
            Defaults to an empty `dict`.

    """

    contents: workflows.Workflow | None = None

    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Executes the worker's workflow.

        Args:
            item: data or object to change.
            **kwargs: keyword arguments for the nodes in the workflow.

        Raises:
            ValueError: if the worker has no workflow.

        Returns:
            The result of the workflow.

        """
        if self.contents is None:
            message = f"worker {self.name!r} has no workflow"
            raise ValueError(message)
        return self.contents.execute(item, **kwargs)


def technique(
    function: Callable[..., Any] | None = None, *, name: str | None = None
) -> Any:
    """Registers a function as a `Technique`.

    It can be used with or without arguments:

    ```py
    @chrisjen.technique
    def scale(item, factor = 2):
        return item * factor

    @chrisjen.technique(name = 'double')
    def twice(item):
        return item * 2
    ```

    Args:
        function: function to register. It should accept the item as its first
            argument and return the changed item.
        name: name to register the function under. Defaults to the function's
            `__name__`.

    Returns:
        The function itself, so that it can still be used directly. If
            `function` is `None`, a decorator is returned.

    """

    def register(func: Callable[..., Any]) -> Callable[..., Any]:
        Technique.functions[name or func.__name__] = func
        return func

    return register if function is None else register(function)


def _subclass_names(cls: type) -> list[str]:
    """Returns the snake case names of all subclasses of `cls`."""
    names: list[str] = []
    for subclass in cls.__subclasses__():
        names.append(wonka.options._KEY_NAMER(subclass))
        names.extend(_subclass_names(subclass))
    return names
