"""
base: base classes for a chrisjen project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:


To Do:

            
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping, MutableSequence
import contextlib
import dataclasses
import inspect
import pathlib
from selectors import EpollSelector
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union
import warnings

import amos
import bobbie
import holden
import miller

if TYPE_CHECKING:
    from . import workshop

       
@dataclasses.dataclass
class Keystone(abc.ABC):
    """Mixin for all project base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because Keystone will be used as a mixin, it is important to call 
        # other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if Keystone in cls.__bases__:
            key = amos.namify(item = cls)
            Structure.keystones[key] = cls
        
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(cls, *args, **kwargs):
        """Creates a class instance."""
        pass

    
@dataclasses.dataclass  # type: ignore
class Repository(amos.Library):
    """Stores classes instances and classes in a chained mapping.
    
    When searching for matches, instances are prioritized over classes.
    
    Args:
        classes (amos.Catalog): a catalog of stored classes. Defaults to any 
            empty Catalog.
        instances (amos.Catalog): a catalog of stored class instances. Defaults 
            to an empty Catalog.
                 
    """
    classes: amos.Catalog[str, Type[Keystone]] = dataclasses.field(
        default_factory = amos.Catalog)
    instances: amos.Catalog[str, Keystone] = dataclasses.field(
        default_factory = amos.Catalog)
    generics: MutableMapping[str, Type[Keystone]] = dataclasses.field(
        default_factory = dict)
    kinds: MutableMapping[str, str] = dataclasses.field(
        default_factory = dict)
    
    """ Properties """
    
    @property
    def plurals(self) -> tuple[str]:
        """Returns all stored subclass names as naive plurals of those names.
        
        Returns:
            tuple[str]: all names with an 's' added in order to create simple 
                plurals combined with the stored keys.
                
        """
        suffixes = []
        for catalog in ['classes', 'instances']:
            plurals = [k + 's' for k in getattr(self, catalog).keys()]
            suffixes.extend(plurals)
        return tuple(suffixes)

    """ Public Methods """
                
    def classify(self, item: Union[Keystone, Type[Keystone]]) -> str:
        """Returns name of kind that 'item' is an instance or subclass of.

        Args:
            item (Union[object, Type[Any]]): item to test for matching kind.

        Raises:
            TypeError: if no matching base kind is found.

        Returns:
            str: name of matching base kind.
            
        """
        if not inspect.isclass(item):
            item = item.__class__
        for name, kind in self.generics.items():
            if issubclass(item, kind):
                return name
        raise TypeError(f'{item} does not match a known type')
  
    def deposit(
        self, 
        item: Union[Keystone, Type[Keystone]],
        name: Optional[Hashable] = None) -> None:
        """Adds 'item' to 'classes' and/or 'instances'.

        If 'item' is a class, it is added to 'classes.' If it is an object, it
        is added to 'instances' and its class is added to 'classes'. The key
        used to store instances and classes are different if the instance has
        a 'name' attribute (which is used as the key for the instance).
        
        Args:
            item (Union[Type[Any], object]): class or instance to add to the 
                Library instance.
            name (Optional[Hashable]): key to use to store 'item'. If not
                passed, a key will be created using the 'namify' method.
                Defaults to None
                
        """
        self.kindify(item = item)
        super().deposit(item = item, name = name)
        return
            
    def genericify(self, item: Type[Keystone]) -> None:
        """Adds 'item' as a base kind in the 'generics' dict.

        Args:
            item (Type[Any]): item to add to the 'generics' dict.
            
        """
        name = amos.namify(item = item)
        self.generics[name] = item
        return
        
    def kindify(self, item: Union[Keystone, Type[Keystone]]) -> None:
        """Adds 'item' as a base kind in the 'kinds' dict.

        Args:
            item (Type[Any]): item to add to the 'kinds' dict.
            
        """
        base = self.classify(item = item)
        name = amos.namify(item = item)
        self.kinds[name] = base
        return


@dataclasses.dataclass  # type: ignore
class Structure(object):
    """

    Args:
        settings
        configuration_suffixes
        keystones
        directors
        managers
        generics
        
    """
    settings: ClassVar[dict[Hashable, dict[Hashable, Any]]] = {
        'general': {
            'verbose': False,
            'parallelize': False,
            'conserve_memory': False},
        'files': {
            'file_encoding': 'windows-1252',
            'threads': -1}}
    suffixes: ClassVar[dict[str, tuple[str]]] = {
        'design': ('design',),
        'director': ('director', 'project'),
        'files': ('filer', 'files', 'clerk'),
        'general': ('general',),
        'managers': ('managers',),
        'parameters': ('parameters',)}
    keystones: ClassVar[amos.Catalog] = amos.Catalog()
    directors: ClassVar[Repository] = Repository()
    managers: ClassVar[Repository] = Repository()
    generics: ClassVar[Repository] = Repository()


@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[Keystone]): configuration settings for the 
            project. Defaults to None.
        filer (Optional[Keystone]): a filing filer for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        director (Optional[Keystone]): constructor and iterator for a
            chrisjen project. Defaults to None.
        structure (Optional[Structure]): base classes and other information for
            structure of a chrisjen project. Defaults to a Structure instance.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None.   
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
    
    """
    name: Optional[str] = None
    settings: Optional[Keystone] = None
    filer: Optional[Keystone] = None
    director: Optional[Keystone] = None
    structure: Optional[Structure] = Structure()
    # outline: Optional[Keystone] = None
    # workflow: Optional[Keystone] = None
    # summary: Optional[Keystone] = None
    # data: Optional[object] = None
    identification: Optional[str] = None
    automatic: Optional[bool] = True
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        project = validate_director(project = self)
 
    # """ Properties """
         
    # @property
    # def options(self) -> amos.Library:
    #     """Returns the current options of available workflow components.

    #     Returns:
    #         amos.Library: options of workflow components.
            
    #     """        
    #     return self.keystones['component'].library
  
    # @options.setter
    # def options(self, value: amos.Library) -> None:
    #     """Sets the current options of available workflow components.

    #     Arguments:
    #         value (Options): new options for workflow components.
            
    #     """        
    #     self.node.library = value
    #     return self
    
    # @functools.cached_property
    # def outline(self) -> Container:
    #     """Returns project outline based on 'settings'

    #     Returns:
    #         Outline: the outline derived from 'settings'.
            
    #     """        
    #     return workshop.create_outline(project = self)
    
    # @functools.cached_property
    # def workflow(self) -> Container:
    #     """Returns workflow based on 'settings'

    #     Returns:
    #         Workflow: the workflow derived from 'settings'.
            
    #     """        
    #     return workshop.create_workflow(project = self)
       
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        settings: Union[pathlib.Path, str, bobbie.Settings],
        **kwargs) -> Project:
        """Returns a Project instance based on 'settings' and kwargs.

        Args:
            settings (Union[pathlib.Path, str, bobbie.Settings]): a path to a 
                file containing configuration settings or a Settings instance.

        Returns:
            Project: an instance based on 'settings' and kwargs.
            
        """        
        return cls(settings = settings, **kwargs)   

    """ Dunder Methods """
    
    def __getattr__(self, item: str) -> Any:
        """Checks 'director' for attribute named 'item'.

        Args:
            item (str): name of attribute to check.

        Returns:
            Any: contents of director attribute named 'item'.
            
        """
        try:
            return getattr(self.director, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project or its director')
 
 
@dataclasses.dataclass
class Director(holden.Path, Keystone, abc.ABC):
    """Constructor and iterator for chrisjen workflows.
        
    Args:
        contents (MutableSequence[Hashable]): ordered list of stored Node 
            instances. Defaults to an empty list.
        project (Optional[Project]): linked Project instance to modify and 
            control. Defaults to None, but a Project instance must be linked
            before any Director methods can be used.
          
    """
    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)
    project: Optional[Project] = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        if self.project is not None:
            # Validates core attributes.
            self.validate()
            # Sets multiprocessing technique, if necessary.
            set_parallelization(project = self.project)
            # Extracts information from settings to create 'project.outline'
            # and 'contents'.
            self.draft()
            # Completes 'project' if 'project.automatic' is True.
            if self.project.automatic:
                self.publish()
                                 
    """ Required Subclass Methods """

    @abc.abstractmethod
    def draft(self, *args: Any, **kwargs: Any) -> None:
        """
        """
        self.project = validate_managers(self.project, *args, **kwargs)
        self.project = validate_outline(self.project, *args, **kwargs)
        self.project = create_managers(self.project, *args, **kwargs)
        return

    @abc.abstractmethod
    def publish(self, *args: Any, **kwargs: Any) -> None:
        """
        """
        for manager in self.contents:
            self.project = manager.complete(self.project, *args, **kwargs)
        return 
        
    """ Public Methods """
   
    @classmethod
    def create(cls, *args, **kwargs):
        """Creates a class instance."""
        return cls(*args, **kwargs)  
        
    def validate(self) -> None:
        """Validates or creates key portions of 'project'."""
        self.project = validate_settings(project = self.project)
        self.project = validate_name(project = self.project)
        self.project = validate_identification(project = self.project)
        self.project = validate_filer(project = self.project)
        return

""" Public Functions """
         
def set_parallelization(project: Project) -> None:
    """Sets multiprocessing method based on 'settings'.
    
    Args:
        project (Project): project containing parallelization settings
        
    """
    if ('general' in project.settings
            and 'parallelize' in project.settings['general'] 
            and project.settings['general']['parallelize']):
        if not globals()['multiprocessing']:
            import multiprocessing
        multiprocessing.set_start_method('spawn') 
    return 
        
def validate_director(project: Project) -> Project:
    """Creates or validates 'project.director'.
    
    Args:
        project (Project): project to examine and validate.
        
    Returns:
        Project: validated Project instance.
        
    """
    if project.director is None:
        project.director = Structure.keystones['director']
    elif isinstance(project.director, str):
        project.director = Structure.keystones[project.director]
    if inspect.isclass(project.director):
        project.director = project.director(project = project)
    else:
        project.director.project = project
    return project

def validate_filer(project: Project) -> Project:
    """Creates or validates 'project.filer'.
    
    The default method performs no validation but is included as a hook for
    subclasses to override if validation of the 'data' attribute is 
    required.
    
    Args:
        project (Project): project to examine and validate.
        
    Returns:
        Project: validated Project instance.
        
    """
    return project    
        
def validate_identification(project: Project) -> Project:
    """Creates unique 'project.identification' if one doesn't exist.
    
    By default, 'identification' is set to the 'name' attribute followed by
    an underscore and the date and time.

    Args:
        project (Project): project to examine and validate.
    
    Raises:
        TypeError: if the 'identification' attribute is neither a str nor
            None.
                   
    Returns:
        Project: validated Project instance.
        
    """
    if project.identification is None:
        prefix = project.name + '_'
        project.identification = miller.how_soon_is_now(prefix = prefix)
    elif not isinstance(project.identification, str):
        raise TypeError('identification must be a str or None type')
    return project
        
def validate_managers(project: Project) -> Project:
    """Creates or validates 'project.director.contents'.
    
    Args:
        project (Project): project to examine and validate.
        
    Returns:
        Project: validated Project instance.
        
    """
    if not project.outline.managers:
        managers = [Structure.keystones['manager']]
    else:
        names = project.outline.managers
        managers = []
        for name in names:
            managers.append(Structure.managers[name])
    project.director.contents = managers
    return project        
        
def validate_name(project: Project) -> Project:
    """Creates or validates 'project.name'.
    
    Args:
        project (Project): project to examine and validate.
        
    Returns:
        Project: validated Project instance.
        
    """
    if project.name is None:
        settings_name = workshop.infer_project_name(project = project)
        if settings_name is None:
            project.name = amos.namify(item = project)
        else:
            project.name = settings_name
    return project  
        
def validate_outline(project: Project) -> Project:
    """Creates or validates 'project.outline'.
    
    Args:
        project (Project): project to examine and validate.
        
    Returns:
        Project: validated Project instance.
        
    """
    if not project.outline.managers:
        managers = [Structure.keystones['manager']]
    else:
        names = project.outline.managers
        managers = []
        for name in names:
            managers.append(Structure.managers[name])
    project.director.contents = managers
    return project
    
def validate_settings(project: Project) -> Project:
    """Creates or validates 'project.settings'.
    
    Args:
        project (Project): project to examine and validate.
        
    Returns:
        Project: validated Project instance.
        
    """
    if inspect.isclass(project.settings):
        project.settings = project.settings()
    if (project.settings is None 
            or not isinstance(project.settings, project.settings)):
        project.settings = project.settings.create(
            item = project.settings,
            project = project)
    elif isinstance(project.settings, project.settings):
        project.settings.project = project
    return project


       
    # def _validate_keystones(self) -> None:
    #     """Creates or validates 'keystones'."""
    #     if inspect.isclass(self.keystones):
    #         self.keystones = self.keystones()
    #     if (not isinstance(self.keystones, Keystones)
    #         or not amos.has_attributes(
    #             item = self,
    #             attributes = [
    #                 'filer', 'component', 'director', 'settings', 'stage', 
    #                 'workflow'])):
    #         self.keystones = Keystones()
    #     return self

    
    # def _validate_workflow(self) -> None:
    #     """Creates or validates 'workflow'."""
    #     if self.workflow is None:
    #         self.workflow = self.workflow
    #     return self

    # def _validate_results(self) -> None:
    #     """Creates or validates 'results'."""
    #     if not hasattr(self, 'results'):
    #         self.results = self.results
    #     return self
    
    # def _validate_data(self) -> None:
    #     """Creates or validates 'data'.
        
    #     The default method performs no validation but is included as a hook for
    #     subclasses to override if validation of the 'data' attribute is 
    #     required.
        
    #     """
    #     return self
