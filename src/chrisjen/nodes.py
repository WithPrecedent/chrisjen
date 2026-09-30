"""Nodes in a workflow.

Contents:
    Node: base class for anything that can be applied to an item in a
        workflow.
    Technique: a single action that wraps a tool, and the base class of all
        types of techniques.
    NullNode: a `Technique` that does nothing.
    Step: a stage of a workflow with one or more techniques.
    Worker: a node with a workflow of its own.

"""

from __future__ import annotations

import abc
import copy
import dataclasses
import inspect
from collections.abc import Callable, MutableMapping, MutableSequence
from typing import TYPE_CHECKING, Any, ClassVar

import holden
import wonka

from . import utilities

if TYPE_CHECKING:
    from . import workflows


@dataclasses.dataclass
class Node(holden.Labeled, abc.ABC):
    """Base class for nodes in a chrisjen workflow.

    Nodes are hashed and compared by `name`, so a `str` equal to the name of a
    node can be used in its place.

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
        default_factory = dict
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
class Technique(Node, wonka.Registrar):
    """A single action in a workflow, which usually wraps another tool.

    A `Technique` is an ordinary object (not a decorated function). Its
    `contents` is the tool that it wraps: any callable, or the import path of
    one, such as `"statistics.fmean"`. A path is only imported when the
    technique is first used, so techniques can wrap optional packages.

    ```py
    technique = chrisjen.Technique("mean", contents = "statistics.fmean")
    technique.complete([1, 2, 3])  # 2.0
    ```

    **Registering.** Techniques are found by name in a registry (a `wonka`
    `Registrar`). Create and register one in a single step with `register`:

    ```py
    chrisjen.Technique.register("mean", "statistics.fmean")
    ```

    **Types.** Each type of technique has a registry of its own. To create a
    type, subclass `Technique` and `abc.ABC` (the direct subclass of `Technique`
    that lists `abc.ABC` is the type):

    ```py
    class Cleaner(chrisjen.Technique, abc.ABC):
        \"\"\"Techniques that clean data.\"\"\"

    Cleaner.register("drop_missing", "package.module.drop_missing")
    ```

    Any other subclass registers its *class* in the registry of its type (or in
    the general registry, if it is a direct subclass of `Technique`) under its
    snake case class name, so it is found automatically. To change how a type
    of technique calls its tool (for example, to build an object from
    parameters and then call one of its methods), override `implement`.

    **Finding techniques.** A name is looked up in the registry of every type.
    If the name is registered in more than one type, write it with its type
    (`"cleaner.drop_missing"`) or name the type with `kind`. Calling `create`
    on a type only looks in that type. The registered technique is copied
    before it is used, so each use has its own parameters and state.

    Args:
        name: name used to refer to the technique in a workflow.
        contents: the tool to wrap: a callable or the import path of one.
            Defaults to `None`, which is only useful for subclasses that
            override `implement`.
        parameters: keyword arguments passed to the tool. Defaults to an empty
            `dict`.

    Attributes:
        registry: techniques and technique classes of this type by name.
        types: `dict` of the names of all technique types and the types.

    """

    contents: Callable[..., Any] | str | None = None
    registry: ClassVar[dict[str, Any]] = {}
    types: ClassVar[dict[str, type[Technique]]] = {}

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Creates a new technique type or registers the subclass."""
        super().__init_subclass__(*args, **kwargs)
        key = wonka.options._KEY_NAMER(cls)
        if Technique in cls.__bases__ and abc.ABC in cls.__bases__:
            cls.registry = {}
            Technique.types[key] = cls
        else:
            cls.registry[key] = cls

    """ Class Methods """

    @classmethod
    def available(cls) -> dict[str, list[str]]:
        """Returns the names of the registered techniques of each type.

        Returns:
            A `dict` of type names and sorted lists of technique names.
                Types with no registered techniques are left out.

        """
        return {
            kind: sorted(technique_type.registry)
            for kind, technique_type in Technique.types.items()
            if technique_type.registry
        }

    @classmethod
    def create(
        cls,
        item: str,
        parameters: MutableMapping[Any, Any] | None = None,
        kind: str | type[Technique] | None = None,
    ) -> Technique:
        """Creates a copy of a registered technique.

        Args:
            item: name of the technique, optionally with its type ("type.name").
            parameters: attributes to set on the copy (such as `name`,
                `contents`, or `parameters`). The name defaults to the name
                looked up. A `parameters` `dict` is combined with the
                technique's own parameters, and takes precedence. Defaults to
                `None`.
            kind: type of technique (a name or a class) to look in. Defaults to
                `None`, which looks in the type that `create` was called on or,
                for `Technique`, in every type.

        Raises:
            KeyError: if `item` is not registered, or is registered in more
                than one type and `kind` was not used to choose one.

        Returns:
            A `Technique` (or subclass) instance.

        """
        owner, key = cls.locate(item, kind)
        # The copy is named for the name that was asked for (so "null" and
        # "none" stay distinct), unless a name is passed.
        parameters = {"name": key, **(parameters or {})}
        return super(Technique, owner).create(key, parameters)

    @classmethod
    def locate(
        cls, item: str, kind: str | type[Technique] | None = None
    ) -> tuple[type[Technique], str]:
        """Finds the type of technique that has `item` registered.

        Args:
            item: name of the technique, optionally with its type ("type.name").
            kind: type of technique (a name or a class) to look in.

        Raises:
            KeyError: if `item` is not registered, or is registered in more
                than one type and `kind` was not used to choose one.

        Returns:
            A `tuple` of the technique type and the name in its registry.

        """
        if kind is not None:
            owner = cls._get_type(kind)
            key = item.removeprefix(f"{wonka.options._KEY_NAMER(owner)}.")
            candidates = [(owner, key)] if key in owner.registry else []
        elif cls is not Technique:
            candidates = [(cls, item)] if item in cls.registry else []
        else:
            head, _, tail = item.partition(".")
            if tail and head in Technique.types:
                owner = Technique.types[head]
                candidates = [(owner, tail)] if tail in owner.registry else []
            else:
                candidates = [
                    (technique_type, item)
                    for technique_type in Technique.types.values()
                    if item in technique_type.registry
                ]
        if len(candidates) == 1:
            return candidates[0]
        if candidates:
            kinds = ", ".join(
                wonka.options._KEY_NAMER(owner) for owner, _ in candidates
            )
            message = (
                f"{item!r} is registered in more than one type of technique "
                f"({kinds}): use a name like '{wonka.options._KEY_NAMER(candidates[0][0])}.{item}' "
                f"or pass kind"
            )
            raise KeyError(message)
        known = "; ".join(
            f"{kind_name}: {', '.join(names)}"
            for kind_name, names in cls.available().items()
        )
        message = (
            f"{item!r} is not a known technique. Register one with "
            f"Technique.register(name, tool) or define a subclass of "
            f"Technique. Known techniques: {known or 'none'}"
        )
        raise KeyError(message)

    @classmethod
    def produce(
        cls, item: Any, parameters: MutableMapping[Any, Any] | None = None
    ) -> Technique:
        """Applies `parameters` to a technique (or creates one from a class).

        `wonka` calls this method to finish creating a technique.

        Args:
            item: a copy of a registered technique, or a registered class.
            parameters: attributes to set, or arguments for a class. A
                `parameters` `dict` is combined with the technique's own.

        Returns:
            The technique.

        """
        parameters = dict(parameters or {})
        if inspect.isclass(item):
            return item(**parameters)
        if "parameters" in parameters:
            parameters["parameters"] = {
                **item.parameters,
                **parameters["parameters"],
            }
        for key, value in parameters.items():
            setattr(item, key, value)
        return item

    @classmethod
    def register(
        cls,
        item: str | Technique,
        contents: Callable[..., Any] | str | None = None,
        parameters: MutableMapping[str, Any] | None = None,
        *,
        name: str | None = None,
    ) -> Technique:
        """Registers a technique, so it can be found by name.

        Args:
            item: the name of a new technique, or a technique to register.
            contents: the tool to wrap, if `item` is a name. Defaults to
                `None`.
            parameters: default keyword parameters for the tool, if `item` is a
                name. Defaults to `None`.
            name: name to register under. Defaults to `item` (or its `name`).

        Raises:
            TypeError: if `item` is not a `str` or an instance of this type of
                technique.

        Returns:
            The registered technique. It replaces any technique with the same
                name in the registry.

        """
        if isinstance(item, str):
            key = name or item
            technique = cls(
                name = key, contents = contents, parameters = dict(parameters or {})
            )
        elif isinstance(item, cls):
            key = name or item.name
            technique = item
        else:
            message = (
                f"item must be a name or a {cls.__name__} instance, not "
                f"{type(item).__name__}"
            )
            raise TypeError(message)
        cls.registry[key] = technique
        return technique

    """ Private Methods """

    @classmethod
    def _get_type(cls, kind: str | type[Technique]) -> type[Technique]:
        """Returns the technique type that `kind` names."""
        if inspect.isclass(kind) and issubclass(kind, Technique):
            return kind
        name = str(kind).lower()
        if name in Technique.types:
            return Technique.types[name]
        message = (
            f"{kind!r} is not a type of technique. Known types: "
            f"{', '.join(Technique.types)}"
        )
        raise KeyError(message)

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
            NotImplementedError: if there is no tool in `contents` and a
                subclass does not override this method.
            TypeError: if the tool is not callable.

        Returns:
            The changed `item`.

        """
        tool = self.resolve()
        if tool is None:
            message = (
                f"technique {self.name!r} has no tool: pass a callable or "
                f"import path as contents or override implement in a subclass"
            )
            raise NotImplementedError(message)
        if not callable(tool):
            message = (
                f"technique {self.name!r} wraps {tool!r}, which is not "
                f"callable: override implement to use it"
            )
            raise TypeError(message)
        return tool(item, **utilities.accepted_arguments(tool, kwargs))

    def resolve(self) -> Any:
        """Returns the wrapped tool, importing it if `contents` is a path.

        Raises:
            ImportError: if `contents` is an import path that cannot be
                imported.

        Returns:
            The tool in `contents`, or `None` if there is none.

        """
        if isinstance(self.contents, str):
            return utilities.import_object(self.contents)
        return self.contents

    """ Dunder Methods """

    def __deepcopy__(self, memo: dict[int, Any]) -> Technique:
        """Copies the technique, sharing a tool that cannot be copied.

        The registry copies a technique each time it creates one. Everything is
        copied, including a tool in `contents` (so that a tool with its own
        state, such as a model, is not shared). If the tool cannot be copied
        (because it holds a lock or a connection, for example), the copy uses
        the same tool.

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
                if field.name != "contents":
                    raise
            setattr(clone, field.name, value)
        return clone


Technique.types["technique"] = Technique


@dataclasses.dataclass
class NullNode(Technique):
    """A technique that does nothing.

    It is included for comparisons where doing nothing is one of the options
    (e.g., a "none" technique among techniques for scaling data). It is
    registered as "none", "null", and "null_node".

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


Technique.registry.update({"none": NullNode, "null": NullNode})


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
        default_factory = list
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
