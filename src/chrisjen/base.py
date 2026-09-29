"""Basic framework for a project.

Contents:
    Resources
    Resource
    Idea
    Manager
    Project

To Do:


"""
from __future__ import annotations

import abc
import contextlib
import dataclasses
import inspect
import sys
import warnings
from collections.abc import MutableMapping, MutableSequence
from typing import TYPE_CHECKING, Any, ClassVar, Unpack

import bobbie
import holden
import wonka

from . import setup, utilities

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Hashable, MutableMapping

if sys.version_info < (3, 12):
    from typing import TypeAlias
    GenericDict: TypeAlias = MutableMapping[Hashable, Any]
    GenericList: TypeAlias = MutableSequence[Any]
    Kwargs: TypeAlias = Unpack(GenericDict)
else:
    type GenericDict = MutableMapping[Hashable, Any]
    type GenericList = MutableSequence[Any]
    type Kwargs = Unpack[GenericDict]


@dataclasses.dataclass
class Resources(wonka.Hub):
    """Stores Resource classes.

    Attributes:
        contents: dictionary of all direct Resource subclasses. Keys are
            snakecase names of the Resource subclass and values are the base
            Resource subclasses.
        defaults: dictionary of the default class for each of the Resource
            subclasses. Keys are snakecase names of the base type and values are
            Resource subclasses.
        All direct Resource subclasses will have an attribute name added
        dynamically.

    """
    contents: wonka.ConstructorDict = dataclasses.field(default_factory = dict)
    defaults: GenericDict = dataclasses.field(default_factory = lambda: {
        'settings': 'idea',
        'manager': 'publisher',
        'engineer': 'up_front',
        'superviser': 'copier',
        'task': 'technique',
        'workflow': 'waterfall'})


@dataclasses.dataclass
class Resource(wonka.Keystone):
    """_summary

    Attributes:
        registry: stores classes and/or instances to be used in item
            construction. Defaults to an empty `dict`.
        hub: central depository for dictionaries of all `Resource` subclasses.

    """

    registry: ClassVar[GenericDict] = {}
    hub: ClassVar[Resources] = Resources

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Kwargs):
        """Automatically registers subclass in Resources."""
        # Because Resource will be used as a mixin, it is important to call
        # other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs)
        if Resource in cls.__bases__:
            Resources.add(item = cls)
        else:
            Resources.register(item = cls)


@dataclasses.dataclass
class Clerk(Resource):
    """Basic File and folder management interface.

    Creates and stores dynamic and static file paths, properly formats files
    for import and export, and provides methods for loading and saving items.

    Args:
        framework: class with default settings, dict of supported file formats,
            and any other information needed for file management. Defaults to
            a FileFramework instance.

    """

    root_folder: descriptors.Folder = descriptors.Folder(default = '.')  # noqa: RUF009
    input_folder: pathlib.Path | str = 'root'
    interim_folder: pathlib.Path | str = 'root'
    output_folder: pathlib.Path | str = 'root'
    framework: type[FileFramework] = dataclasses.field(
        default_factory = FileFramework)


@dataclasses.dataclass
class Engineer(Resource, abc.ABC):
    """Stores, organizes, and builds nodes.

    Args:
        project: linked Project instance with a `library` attribute containing
            Keystones.

    """
    project: Project | None = dataclasses.field(
        default = None,
        repr = False,
        compare = False)

    """ Public Methods """

    def acquire(
        self,
        name: str | tuple[str, str],
        **kwargs: Kwargs) -> Node:
        """Gets node from the project library and returns an instance.

        Args:
            name: name of the node that should match a key in the project
                library.
            kwargs: additional keyword arguments.

        Returns:
            Node subclass instance based on passed arguments.

        """
        if isinstance(name, tuple):
            step = self.acquire(name = name[0])
            technique = self.acquire(name = name[1])
            return step.create(
                name = name[0],
                technique = technique,
                project = self.project)
        else:
            lookups = self._get_lookups(name = name)
            # initialization = self._get_initialization(lookups = lookups)
            # initialization.update(**kwargs)
            node = self._get_node(lookups = lookups)
            return node.create(name = name, project = self.project, **kwargs)

    @classmethod
    def create(
        cls,
        project: Project,
        name: str | None = None,
        **kwargs: Kwargs) -> Engineer:
        """Returns a subclass instance based on passed arguments.

        Args:
            project: related Project instance.
            name: name or key to lookup the subclass.
            kwargs: additional keyword arguments.

        Returns:
            Engineer subclass instance based on passed arguments.

        """
        return cls(project = project, **kwargs)

    """ Private Methods """

    # def _get_implementation(self, lookups: list[str]) -> dict[str, Any]:
    #     """_summary_

    #     Args:
    #         lookups: _description_

    #     Raises:
    #         TypeError: _description_

    #     Returns:
    #         dict[str, Any]: _description_

    #     """
    #     for key in lookups:
    #         try:
    #             return self.project.outline.implementation[key]
    #         except KeyError:
    #             pass
    #     return {}

    def _get_initialization(self, lookups: list[str]) -> dict[str, Any]:
        """_summary_

        Args:
            lookups: _description_

        Raises:
            TypeError: _description_

        Returns:
            _description_

        """
        for key in lookups:
            with contextlib.suppress(KeyError):
                return self.project.outline.initialization[key]
        return {}

    def _get_lookups(self, name: str) -> list[str]:
        """_summary_

        Args:
            name: _description_

        Returns:
            _description_

        """
        if name in setup.null_nodes:
            return ['null_node']
        keys = [name]
        if name in self.project.outline.designs:
            keys.append(self.project.outline.designs[name])
        elif name == self.project.name:
            keys.append(workflow)
        if name in self.project.outline.kinds:
            keys.append(self.project.outline.kinds[name])
        return keys

    def _get_node(self, lookups: list[str]) -> Node:
        """_summary_

        Args:
            lookups: _description_

        Raises:
            KeyError: _description_

        Returns:
            _description_
        """
        for key in lookups:
            with contextlib.suppress(KeyError):
                return self.project.library.node[key]
        raise KeyError(f'No matching node found for these: {lookups}')


@dataclasses.dataclass
class Idea(bobbie.Settings, Resource):
    """Loads and stores configuration settings.

    Args:
        contents: configuration options. Defaults to an empty `dict`.
        name: the `str` name of `Settings`. The top-level of a `Settings` need
            not have any name, but may include one for use by custom parsers.
            Defaults to `None`.

    Attributes:
        sources: `dict` with keys that are types and values are substrings of
            the names of methods to call when the key type is passed to the
            `create` method. Defaults to an empty `dict`.

    """

    contents: GenericDict = dataclasses.field(default_factory = dict)
    name: str | None = None
    sources: ClassVar[MutableMapping[type[Any], str]] = {
        pathlib.Path: 'file',
        str: 'file',
        MutableMapping: 'dict'}
    registry: ClassVar[GenericDict] = {}
    hub: ClassVar[Resources] = Resources


@dataclasses.dataclass
class Manager(Resource, abc.ABC):
    """Controller for chrisjen projects.

    Args:
        project: linked Project instance to modify and control.
        clerk: a filing clerk for loading and saving files throughout a
            chrisjen project. Defaults to None.
        engineer: class to access stored keystones. Defaults to None.

    """
    project: Project | None = dataclasses.field(
        default = None, repr = False, compare = False)
    clerk: Clerk| None = None
    engineer: Engineer | None = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # Validates core attributes.
        self.validate()
        if self.project.automatic:
            self.complete()

    """ Required Subclass Methods """

    @abc.abstractmethod
    def complete(self) -> None:
        """Applies workflow to 'project'."""
        return

    """ Public Methods """

    @classmethod
    def create(
        cls,
        project: Project,
        name: str | None = None,
        **kwargs: Kwargs) -> Manager:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (structure.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            Manager: subclass instance based on passed arguments.

        """
        return cls(project = project, **kwargs)

    def validate(self) -> None:
        """Validates or creates required portions of 'project'."""
        self._validate_idea()
        self._validate_name()
        self._validate_id()
        self._validate_clerk()
        self._set_parallelization()
        self = Resources.validate(
            item = self,
            attribute = 'engineer',
            parameters = {'project': self})
        return

    """ Private Methods """

    def _validate_clerk(self) -> None:
        """Creates or validates 'project.clerk'.

        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is
        required.

        """
        with contextlib.suppress(KeyError):
            defaults = self.project.defaults.settings['files']
            nagata.Filestructure.settings.update(defaults)
        for key in self.project.defaults.parsers['files']:
            with contextlib.suppress(KeyError):
                project_settings = self.project.idea[key]
                nagata.Filestructure.settings.update(project_settings)
        root_folder = pathlib.Path('..').joinpath('data')
        root_folder = pathlib.Path(root_folder).joinpath(
            self.project.identification)
        self.clerk = nagata.FileManager(
            root_folder = root_folder,
            input_folder = 'input',
            interim_folder = 'interim',
            output_folder = 'output')
        return

    def _validate_id(self) -> None:
        """Creates unique 'project.identification' if one doesn't exist.

        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.

        Args:
            project (Project): project to examine and validate.

        """
        if self.project.identification is None:
            prefix = f'{self.project.name}_'
            self.project.identification = miller.how_soon_is_now(
                prefix = prefix)
        elif not isinstance(self.project.identification, str):
            raise TypeError('identification must be a str or None type')
        return

    def _validate_name(self) -> None:
        """Creates or validates 'project.name'."""
        if self.project.name is None:
            idea_name = self._infer_project_name()
            if idea_name is None:
                self.project.name = utilities._namify(item = self.project)
            else:
                self.project.name = idea_name
        if self.project.name.endswith('_project'):
            self.project.name = self.project.name[:-8]
        return

    def _validate_idea(self) -> None:
        """Creates or validates 'project.idea'."""
        if inspect.isclass(self.project.idea):
            self.project.idea = self.project.idea()
        elif not isinstance(self.project.idea, Architect):
            base = Architect
            self.project.idea = create(
                source = self.project.idea,
                default = Defaults.settings)
        return

    def _infer_project_name(self) -> str | None:
        """Infers project name from 'project.idea'.

        Returns:
            Optional[str]: name of project based on project settings. Returns
                None if a name can not be inferred.

        """
        name = None
        for key in self.project.idea:
            if key.endswith('_project'):
                name = key.removesuffix('_project')
                break
        return name

    def _validate_engineer(self) -> None:
        """Creates or validates 'engineer'."""
        if self.engineer is None:
            self.engineer = Resources.engineer[
                Defaults.engineer]
        elif isinstance(self.manager, str):
            self.engineer = Resources.engineer[
                self.engineer]
        if inspect.isclass(self.engineer):
            self.engineer = self.engineer(project = self)
        else:
            self.engineer.project = self
        return

    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'settings'.

        Args:
            project (Project): project containing parallelization settings.

        """
        if ('general' in self.project.idea
                and 'parallelize' in self.project.idea['general']
                and self.project.idea['general']['parallelize']):
            if not globals()['multiprocessing']:
                import multiprocessing
            multiprocessing.set_start_method('spawn')
        return

    """ Dunder Methods """

    def __getattr__(self, item: str) -> Any:
        """Checks 'engineer' for attribute named 'item'.

        Args:
            item (str): name of attribute to check.

        Returns:
            Any: contents of engineer attribute named 'item'.

        """
        try:
            return getattr(self.engineer, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project manager or its engineer')


@dataclasses.dataclass
class Node(holden.Labeled, Resource, Hashable, abc.ABC):
    """Base class for nodes in a chrisjen project.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty dict.

    """
    name: str | None = None
    contents: Any | None = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

    """ Initialization Methods """

    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Kwargs):
        """Makes subclass instances hashable.

        This method forces subclasses to use the same hash methods as
        Node. This is necessary because dataclasses, by design, do not
        automatically inherit the hash and equivalance dunder methods from their
        parent classes.

        """
        # Because Node will be used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs)
        # Copies hashing related methods to a subclass.
        cls.__hash__ = Node.__hash__
        cls.__eq__ = Node.__eq__
        cls.__ne__ = Node.__ne__

    """ Public Methods """

    def complete(self, item: Any, **kwargs: Kwargs) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied,
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.

        """
        with contextlib.suppress(AttributeError):
            self.parameters.finalize(item = item)
        return self.implement(item = item, **self.parameters, **kwargs)

    @classmethod
    def create(
        cls,
        project: Project,
        name: str | None = None,
        **kwargs: Kwargs) -> Node:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (structure.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            Node: subclass instance based on passed arguments.

        """
        return cls(name = name, **kwargs)

    @abc.abstractmethod
    def implement(self, item: Any, **kwargs: Kwargs) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied,
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.

        """

    """ Dunder Methods """

    def __eq__(self, other: object) -> bool:
        """Test eqiuvalence based on 'name' attribute.

        Args:
            other (object): other object to test for equivalance.

        Returns:
            bool: whether 'name' is the same as 'other.name'.

        """
        try:
            return str(self.name) == str(other.name) # type: ignore
        except AttributeError:
            return str(self.name) == other

    def __ne__(self, other: object) -> bool:
        """Completes equality test dunder methods.

        Args:
            other (object): other object to test for equivalance.

        Returns:
            bool: whether 'name' is not the same as 'other.name'.

        """
        return not(self == other)

    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equal to 'contents'.

        Args:
            item (Any): item to check versus 'contents'

        Returns:
            bool: if 'item' is in or equal to 'contents' (True). Otherwise, it
                returns False.

        """
        try:
            return item in self.contents
        except TypeError:
            try:
                return item is self.contents
            except TypeError:
                return item == self.contents

    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a graph object that uses a dict as
        its base storage type.

        Returns:
            int: hashable of 'name'.

        """
        return hash(self.name)


@dataclasses.dataclass
class Project:
    """User interface for a chrisjen project.

    Args:
        name: designates the name of a class instance that is used for internal
            referencing throughout chrisjen. Defaults to None.
        idea: configuration settings for the project. Defaults to None.
        manager: constructor for a chrisjen project. Defaults to None.
        identification: a unique identification name for a
            chrisjen project. The name is primarily used for creating file
            folders related to the project. If it is None, a str will be created
            from 'name' and the date and time. This prevents files from one
            project from overwriting another. Defaults to None.
        automatic: whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False).
            Defaults to False.

    Attributes:
        defaults: a class storing the default project
            options. Defaults to Defaults.
        library: library of nodes for executing a
            chrisjen project. Defaults to an instance of ProjectLibrary.

    """
    idea: bobbie.Settings | None = dataclasses.field(
        default = None, repr = False)
    manager: Manager = dataclasses.field(
        default_factory = Manager, repr = False)
    workflow: holden.Composite | None = dataclasses.field(
        default = None)
    resources: type[Resources] | None = dataclasses.field(
        default = Resources, repr = False)
    name: str | None = None
    identification: str | None = dataclasses.field(
        default = None, compare = False)
    automatic: bool = dataclasses.field(default = False, compare = False)

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Removes various python warnings from console output.
        if not setup._WARNINGS:
            warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        Resources.validate(
            item = self,
            attribute = 'manager',
            parameters = {'project': self})

    """ Public Class Methods """

    @classmethod
    def create(
        cls,
        idea: pathlib.Path | str | Idea,
        **kwargs: Kwargs) -> Project:
        """Returns a Project instance based on `idea` and kwargs.

        Args:
            idea: a path to a file containing configuration settings, a python
                dict, or an Idea instance.
            kwargs: other keyword arguments to pass to the created Project
                instance.

        Returns:
            A `Project` instance based on `idea` and kwargs.

        """
        return cls(idea = idea, **kwargs)

    def validate(self) -> None:
        """Validates all attributes that are Resource subclasses."""
        resources = self._identify_resouces()
        for resource in resources:
            method_name = f'_validate_{resource}'
            validator = getattr(self, method_name)
            validator()
        return self

    """ Dunder Methods """

    def __getattr__(self, item: str) -> Any:
        """Checks 'manager' for attribute named 'item'.

        Args:
            item: name of attribute to check.

        Returns:
            Any: contents of manager attribute named 'item'.

        """
        try:
            return getattr(self.manager, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project or its manager')


@dataclasses.dataclass
class View(Resource, abc.ABC):
    """Organizes data in a related project to increase accessibility.

    View subclasses should emphasize the used of properties so that any changes
    to the related project are automatically reflected in the View subclass.

    Args:
        name
        project: a related project instance which has data
            from which the properties of a View can be derived.

    """
    name: str | None = None
    project: Project | None = dataclasses.field(
        default = None, repr = False, compare = False)

    """ Public Methods """

    @classmethod
    def create(
        cls,
        project: Project,
        name: str | None = None,
        **kwargs: Kwargs) -> View:
        """Returns a subclass instance based on passed arguments.

        Args:
            project: related Project instance.
            name: name or key to lookup the subclass.

        Returns:
            View: subclass instance based on passed arguments.

        """
        return cls(name = name, project = project, **kwargs)
