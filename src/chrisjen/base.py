"""Base classes for a project.

Contents:
    Library: stores `Genre` classes in the hierarchy of their subclasses.
    library: the `Library` that `Genre` subclasses are added to.
    Genre: base class for every class that is stored in the `library`.
    Idea: settings of a project, with properties for building its workflow.
    Vertex: base class for nodes in a project workflow.
    Criteria: scores the results of a workflow.
    Report: base class for reports that describe a project.

"""

from __future__ import annotations

import abc
import dataclasses
import inspect
from collections.abc import (
    Callable,
    Hashable,
    Iterator,
    MutableMapping,
    Sequence,
)
from typing import TYPE_CHECKING, Any, TypeAlias

import bobbie
import camina
import holden

from . import options, utilities

if TYPE_CHECKING:
    from . import interface


GenericDict: TypeAlias = MutableMapping[Hashable, Any]
# A layer of `Library.contents`: names of genres (abstract classes) map to
# nested layers and names of other classes map to the classes.
Layer: TypeAlias = MutableMapping[str, Any]
# Fields of a `Vertex` that are not filled from settings by `Vertex.build`.
# Criteria are named by the "criterion" setting and built separately.
_NOT_SETTINGS: tuple[str, ...] = (
    'name', 'contents', 'parameters', 'criteria', 'default_factory')


@dataclasses.dataclass
class Library(MutableMapping[str, Any]):
    """Stores `Genre` classes in the hierarchy of their subclasses.

    `contents` is a nested `dict` that follows the subclasses of `Genre`. An
    abstract class (one that lists `abc.ABC` among its bases) is only a key: its
    value is a new layer for its subclasses, and the class itself is not
    stored. Any other class is stored, under its name, in the layer of its
    nearest abstract ancestor (or at the top level, if it has none). For
    example, `Vertex`, `Step`, and `Worker` are abstract, so if `Scaler` is a
    subclass of `Technique` and `Scale` is a subclass of `Step`:

    ```py
    {
        'vertex': {
            'technique': Technique,
            'scaler': Scaler,
            'step': {'scale': Scale},
            'worker': {'flow': Flow, 'contest': Contest},
        }
    }
    ```

    A class can also be added under another name (`NullVertex` is also stored
    as "none"). `all` is a flat `dict` of every stored class, and `borrow`
    finds classes by name.

    Attributes:
        contents: nested dictionary of `Genre` subclasses. Keys are the names of
            the subclasses (by default, snake case versions of their class
            names). Values are either subclasses or nested dictionaries
            containing subclasses.

    """

    contents: Layer = dataclasses.field(default_factory = dict)

    """ Properties """

    @property
    def genres(self) -> list[str]:
        """Returns names of the genres (abstract classes) at every level."""
        return utilities._all_genres(self.contents)

    @property
    def plurals(self) -> list[str]:
        """Returns a list of pluralized names of genres."""
        return camina.add_suffix_to_list(self.genres, 's')

    @property
    def all(self) -> dict[str, type]:
        """Returns a flattened dictionary of all classes in the library."""
        return utilities._flatten_dict(self.contents)

    """ Public Methods """

    def add(self, item: type, name: str | None = None) -> None:
        """Adds `item` to its place in `contents`.

        An abstract class (one that lists `abc.ABC` among its bases) adds a
        new, empty layer named for it, unless that layer already exists. Any
        other class is stored under its name in the layer of its nearest
        abstract ancestor. A direct subclass of `Genre` is at the top level.

        Args:
            item: `Genre` subclass to add.
            name: name to store `item` under. Defaults to `None`, which uses
                the snake case name of the class.

        Raises:
            TypeError: if `item` is not a subclass of `Genre`.
            ValueError: if `item` is `Genre` itself, or if its name is already
                used in the same layer for a different kind of entry (a class
                where a layer is, or a layer where a class is).

        """
        if not (inspect.isclass(item) and issubclass(item, Genre)):
            message = f'item must be a subclass of Genre, not {item!r}'
            raise TypeError(message)
        if item is Genre:
            message = 'Genre itself cannot be added: add its subclasses'
            raise ValueError(message)
        name = self._get_name(item, name)
        layer = self._get_layer(
            utilities._get_path(item, Genre, self._get_name))
        existing = layer.get(name)
        if utilities._is_abstract(item):
            if existing is not None and not isinstance(existing, dict):
                message = (
                    f'{name!r} is already a stored class, so the abstract '
                    f'class {item.__name__} cannot form a genre with it'
                )
                raise ValueError(message)
            # Keeps the layer (and what is in it) if it already exists.
            layer.setdefault(name, {})
        else:
            if isinstance(existing, dict):
                message = (
                    f'{name!r} is already a genre, so the class '
                    f'{item.__name__} cannot be stored with that name'
                )
                raise ValueError(message)
            layer[name] = item

    def borrow(
        self,
        names: str | Sequence[str],
        genre: str | type[Genre] | None = None) -> type[Genre]:
        """Returns the first class found that is named in `names`.

        Listing more than one name allows a specific class to be used if it
        exists, with a general one as a fallback. For example, a worker named
        "analyst" can use an `Analyst` class, if there is one, and otherwise
        the class of its design.

        Args:
            names: name or names of classes, in the order to look for them.
            genre: name of the genre (or the abstract class) to look in.
                Defaults to `None`, which looks in the whole library.

        Raises:
            KeyError: if none of `names` are in the library (or `genre`), or
                if `genre` is not a genre in the library.

        Returns:
            The first class found.

        """
        if genre is None:
            classes = self.all
        else:
            classes = utilities._flatten_dict(self.get_genre(genre))
        for name in utilities._iterify(names):
            if name in classes:
                return classes[name]
        message = f'no class named {names!r} is in the library'
        raise KeyError(message)

    def classify(self, item: str | type[Genre] | Genre) -> str:
        """Returns the genre (abstract base class) that `item` is in.

        Args:
            item: `Genre` subclass, subclass instance, or its name.

        Raises:
            ValueError: if `item` is not in the library, or if it is at the
                top level of the library (and so is not in a genre).

        Returns:
            The name of the genre to which `item` belongs: the innermost layer
                that it is in.

        """
        if isinstance(item, str):
            genre = utilities._find_genre(self.contents, item)
            if genre is utilities._MISSING:
                message = f'{item!r} is not in the library'
                raise ValueError(message)
        else:
            if not inspect.isclass(item):
                item = item.__class__
            if not issubclass(item, Genre) or item is Genre:
                message = f'{item!r} is not in the library'
                raise ValueError(message)
            path = utilities._get_path(item, Genre, self._get_name)
            genre = path[-1] if path else None
        if genre is None:
            message = f'{item!r} is at the top level, so it is not in a genre'
            raise ValueError(message)
        return genre

    def delete(self, item: str) -> None:
        """Deletes the class or layer named `item`, wherever it is.

        Deleting a layer deletes everything in it.

        Args:
            item: name of a class or a layer.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        removed: set[str] = set()
        def remove(layer: Layer) -> None:
            for key in list(layer):
                value = layer[key]
                if key == item:
                    removed.add(key)
                    if isinstance(value, dict):
                        removed.update(utilities._get_all_keys(value))
                    del layer[key]
                elif isinstance(value, dict):
                    remove(value)
        remove(self.contents)
        if not removed:
            message = f'{item!r} is not in the library'
            raise KeyError(message)

    def get_genre(
        self,
        item: str | type[Genre]) -> Layer:
        """Returns the layer of `contents` formed by a genre abstract class.

        Args:
            item: abstract `Genre` subclass or its name.

        Raises:
            KeyError: if there is no layer for `item`.

        Returns:
            The nested `dict` of the subclasses of `item`.

        """
        name = item if isinstance(item, str) else self._get_name(item)
        found = utilities._find(self.contents, name)
        if not isinstance(found, dict):
            message = f'{name!r} is not a layer of the library'
            raise KeyError(message)
        return found

    """ Private Methods """

    def _get_layer(self, path: list[str]) -> Layer:
        """Returns the layer at `path`, creating any layers that are missing.

        Args:
            path: names of the genres that lead to the layer, from the top
                level of `contents` down.

        Returns:
            The nested `dict` at `path`.

        """
        layer = self.contents
        for key in path:
            layer = layer.setdefault(key, {})
        return layer

    @staticmethod
    def _get_name(item: type[Genre], name: str | None = None) -> str:
        """Returns `name` or the name to store `item` under.

        Args:
            item: `Genre` subclass to name.
            name: name to use. Defaults to `None`, which uses the snake case
                name of `item`.

        Returns:
            The name for `item`.

        """
        return name or options._KEY_NAMER(item)

    """ Dunder Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns value for `key` at the top level of `contents`.

        Args:
            key: key in `contents` for which a value is sought.

        Returns:
            Value stored in `contents`: a layer or a class.

        """
        return self.contents[key]

    def __setitem__(
        self, key: str,
        value: type[Genre] | dict[str, type[Genre]]) -> None:
        """Adds `value` to the library under the name `key`.

        A `Genre` subclass is added to its place in `contents` (see `add`). A
        dictionary of subclasses is stored as is, as a genre at the top level.

        Args:
            key: name to store `value` under.
            value: `Genre` subclass or dictionary of subclasses.

        """
        if isinstance(value, dict):
            self.contents[key] = value
        else:
            self.add(value, name = key)

    def __delitem__(self, item: str) -> None:
        """Deletes the class or layer named `item`.

        Args:
            item: name of a class or layer, at any level.

        Raises:
            KeyError: if `item` is not in `contents`.

        """
        self.delete(item)

    def __add__(self, other: type[Genre]) -> Library:
        """Adds `other` to the library using the `add` method.

        Args:
            other: `Genre` subclass to add.

        Returns:
            This library.

        """
        self.add(other)
        return self

    def __iter__(self) -> Iterator[str]:
        """Returns iterator of the top level of `contents`.

        Returns:
            Iterator of `contents`.

        """
        return iter(self.contents)

    def __len__(self) -> int:
        """Returns length of the top level of `contents`.

        Returns:
            Length of `contents`.

        """
        return len(self.contents)


library: Library = Library()


@dataclasses.dataclass
class Genre(abc.ABC):  # noqa: B024
    """Stores itself in the project library.

    Every subclass of `Genre` is added to `library` when it is defined. A
    subclass that lists `abc.ABC` among its bases is abstract: it forms a new
    layer of `Library.contents`. Any other subclass is stored in the layer of
    its nearest abstract ancestor.

    """

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """Automatically adds subclasses to the library."""
        super().__init_subclass__(*args, **kwargs)
        library.add(cls)


@dataclasses.dataclass
class Idea(bobbie.Settings, Genre):
    """Loads and stores configuration settings.

    Idea is a subclass of the Settings class in the bobbie repo. See its
    documentation for information about its functionality.
    https://withprecedent.github.io/bobbie/

    Idea adds properties (`workers`, `steps`, `techniques`, `designs`,
    `criteria`, and `parameters`) and a `get_settings` method that read the
    parts of a `chrisjen` workflow from the settings. Its fields (`contents`,
    `default_factory`, and `name`) are those of `bobbie.Settings`.

    """

    """ Properties """

    @property
    def criteria(self) -> dict[str, str]:
        """Returns the criteria of the workers and steps in the settings.

        In each worker section, a "criterion" setting is the criterion of the
        worker and a "{name}_criterion" setting is the criterion of `name`.

        Returns:
            A `dict` mapping names (the prefix of the setting, or the worker
                name for "criterion") to criteria.

        """
        return self._find_settings('criterion')

    @property
    def designs(self) -> dict[str, str]:
        """Returns the designs of the workers in the settings.

        In each worker section, a "design" setting is the design of the worker
        and a "{name}_design" setting is the design of `name`. A worker without
        a design uses `options._DEFAULT_DESIGN`.

        Returns:
            A `dict` mapping names (the prefix of the setting, or the worker
                name for "design") to designs.

        """
        designs = self._find_settings('design')
        for worker in self.workers:
            # Uses the default design for a worker that does not name one.
            if worker not in designs:
                designs[worker] = options._DEFAULT_DESIGN
        return designs

    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        """Returns the parameters sections of the settings.

        Returns:
            A `dict` mapping the prefix of each section that ends in
                "_parameters" to that section.

        """
        parameters = {}
        for key, section in self.contents.items():
            # Skips settings that are not sections.
            if not isinstance(section, MutableMapping):
                continue
            # Stores each parameters section under the name before
            # "_parameters".
            if key.endswith('_parameters'):
                name = key.removesuffix('_parameters')
                parameters[name] = dict(section)
        return parameters

    @property
    def steps(self) -> dict[str, list[str]]:
        """Returns the steps of the workers in the settings.

        In each worker section, a "steps" setting lists the steps of the worker
        and a "{name}_steps" setting lists the steps of `name`. A "workers" or
        "{name}_workers" setting (as in the project section) lists steps the
        same way.

        Returns:
            A `dict` mapping names (the prefix of the setting, or the worker
                name for "steps") to `list`s of step names.

        """
        found = self._find_settings('workers')
        found.update(self._find_settings('steps'))
        steps = {}
        for name, value in found.items():
            # Converts a setting such as "clean, scale" to a list of names.
            steps[name] = utilities._listify_names(value)
        return steps

    @property
    def techniques(self) -> dict[str, list[str]]:
        """Returns the techniques of the workers and steps in the settings.

        In each worker section, a "techniques" setting lists the techniques of
        the worker and a "{name}_techniques" setting lists the techniques of
        `name` (usually a step).

        Returns:
            A `dict` mapping names (the prefix of the setting, or the worker
                name for "techniques") to `list`s of technique names.

        """
        techniques = {}
        for name, value in self._find_settings('techniques').items():
            # Converts a setting such as "min_max, standard" to a list of
            # names.
            techniques[name] = utilities._listify_names(value)
        return techniques

    @property
    def workers(self) -> dict[str, dict[str, Any]]:
        """Returns the worker sections of the settings.

        The project section (whose name ends in "_project") is included under
        the name of the project, the part before "_project", so its settings
        are found by the other properties as well.

        Returns:
            A `dict` mapping the name of each section of `contents` that does
                not end in "parameters" and is not in
                `options._SPECIAL_SETTINGS` to that section.

        """
        workers = {}
        for key, section in self.contents.items():
            # Skips settings that are not sections.
            if not isinstance(section, MutableMapping):
                continue
            # Skips parameters sections and special sections (such as "files").
            if key.endswith('parameters') or key in options._SPECIAL_SETTINGS:
                continue
            # Stores the project section under the name of the project.
            name = key.removesuffix('_project')
            workers[name] = section
        return workers

    """ Public Methods """

    def get_settings(self, name: str, keys: Sequence[str]) -> dict[str, Any]:
        """Returns the settings in `keys` that belong to `name`.

        A setting belongs to `name` if it is in the section for `name` or if
        it is named "{name}_{key}" in any worker section. This is how settings
        such as "max_iterations" reach the class that `name` is built from.

        Args:
            name: name of a worker, step, or technique.
            keys: names of the settings to look for.

        Returns:
            A `dict` mapping each key in `keys` that is found to its value.

        """
        found = {}
        for key in keys:
            settings = self._find_settings(key)
            if name in settings:
                found[key] = settings[name]
        return found

    """ Private Methods """

    def _find_settings(self, suffix: str) -> dict[str, Any]:
        """Returns the settings named `suffix` or ending in `_{suffix}`.

        Args:
            suffix: name of the setting to find in each worker section.

        Returns:
            A `dict` mapping names to the values of the settings. A setting
                named `suffix` is stored under the name of its worker section,
                and a setting named "{name}_{suffix}" under `name`.

        """
        found = {}
        for worker, section in self.workers.items():
            for key, value in section.items():
                # A setting such as "design" belongs to the worker itself.
                if key == suffix:
                    found[worker] = value
                # A setting such as "clean_design" belongs to "clean".
                elif key.endswith(f'_{suffix}'):
                    name = key.removesuffix(f'_{suffix}')
                    found[name] = value
        return found


@dataclasses.dataclass
class Vertex(holden.Labeled, holden.Node, Genre, abc.ABC):
    """Base class for nodes in a `chrisjen` workflow.

    Vertexes are hashed and compared by `name`, so a `str` equal to the name of
    a node can be used in its place. Each vertex is applied to an item with
    `apply` and can be built from a project's settings with `build`. The
    subclasses are in the `nodes` and `workers` modules.

    Args:
        contents: item(s) to be applied to the `item` passed to `apply`.
            Defaults to `None`.
        name: name used to refer to the node in a workflow. Defaults to `None`,
            in which case the name is inferred from the class or `contents`.
        parameters: keyword arguments passed to `implement` by `apply`.
            Defaults to an empty `dict`.

    """

    contents: Any | None = None
    name: str | None = None
    parameters: GenericDict = dataclasses.field(default_factory = dict)

    """ Class Methods """

    @classmethod
    def build(
        cls,
        name: str,
        project: interface.Project,
        parameters: GenericDict | None = None,
        **kwargs: Any) -> Vertex:
        """Builds an instance named `name` from the settings of `project`.

        Settings that belong to `name` (see `Idea.get_settings`) and match a
        field of the class are passed to the constructor, so a setting such as
        "max_iterations" reaches the class that uses it. The "{name}_parameters"
        section of the settings is added to the default parameters of the
        class. Subclasses can override this method to build themselves
        differently.

        Args:
            name: name of the node.
            project: the project the node belongs to.
            parameters: more parameters, which take precedence over those in
                the settings. Defaults to `None`.
            **kwargs: other arguments for the constructor, which take
                precedence over the settings.

        Returns:
            The built instance.

        """
        fields = [
            field.name for field in dataclasses.fields(cls)
            if field.name not in _NOT_SETTINGS]
        settings = project.idea.get_settings(name, fields)
        vertex = cls(name = name, **{**settings, **kwargs})
        vertex.parameters.update(project.idea.parameters.get(name, {}))
        vertex.parameters.update(parameters or {})
        return vertex

    """ Public Methods """

    def apply(self, item: Any, **kwargs: Any) -> Any:
        """Applies this node to `item`.

        Args:
            item: data or object (often the result of the previous node) to
                which this node should be applied.
            **kwargs: keyword arguments for `implement` that take precedence
                over `parameters`.

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
class Criteria(Genre, abc.ABC):
    """Scores the results of a workflow.

    `Criteria` can be used directly, by wrapping a tool, or subclassed to
    override `score`. A `Contest` keeps the result with the highest score, and
    a `Benchmark` stops when `test` passes.

    Args:
        contents: tool that scores a result: a callable or the import path of
            one. Defaults to `None`.
        parameters: keyword arguments passed to the tool. Defaults to an empty
            `dict`.

    """

    contents: str | Callable[..., Any] | None = None
    parameters: GenericDict = dataclasses.field(default_factory = dict)

    """ Public Methods """

    def score(self, item: Any) -> Any:
        """Returns the score of `item`. Higher scores are better.

        Args:
            item: data or object to score.

        Raises:
            NotImplementedError: if there is no tool in `contents` and a
                subclass does not override this method.

        Returns:
            The result of calling the tool with `item` and `parameters`.

        """
        tool = self.contents
        if isinstance(tool, str):
            tool = utilities.import_object(tool)
        if tool is None:
            message = 'criteria has no tool: pass one as contents'
            raise NotImplementedError(message)
        return tool(item, **self.parameters)

    def test(self, item: Any) -> bool:
        """Returns whether `item` meets the criteria (has a true score).

        Args:
            item: data or object to test.

        Returns:
            Whether the score of `item` is true.

        """
        return bool(self.score(item))


@dataclasses.dataclass
class Report(Genre, abc.ABC):
    """Describes a project after it is applied.

    `Project.apply` calls `generate` after each run of the workflow.

    Args:
        contents: data for the report. Defaults to `None`.

    """

    contents: Any = dataclasses.field(default = None)

    """ Required Methods """

    @abc.abstractmethod
    def generate(self, project: interface.Project) -> Any:
        """Generates the report for `project`.

        Args:
            project: the project to report on, after it has been applied.

        Returns:
            The generated report.

        """
        raise NotImplementedError
