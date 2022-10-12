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
import collections
from collections.abc import (
    Callable, Container, Hashable, Mapping, MutableMapping, Sequence, Set)
import copy
import dataclasses
import functools
import inspect
import itertools
import multiprocessing
import pathlib
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union
import warnings

import amos
import bobbie
import holden
import nagata

if TYPE_CHECKING:
    from . import workshop
 

CONFIGURATION_SUFFIXES: MutableMapping[str, tuple[str]] = {
    'design': ('design',),
    'files': ('filer', 'files'),
    'general': ('general',),
    'parameters': ('parameters',),
    'structure': ('project',)}
    
FILER_SETTINGS: MutableMapping[str, Any] = {
    'file_encoding': 'windows-1252',
    'conserve_memory': False,
    'threads': -1}

""" 
Project Base Registry

Key names are str names of a subclass (snake_case by default) and values are the 
subclasses. Defaults to an empty dict.  

""" 
PROJECT_BASES: MutableMapping[str, Type[ProjectBase]] = {}

    
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
    classes: amos.Catalog[str, Type[Any]] = dataclasses.field(
        default_factory = amos.Catalog)
    instances: amos.Catalog[str, object] = dataclasses.field(
        default_factory = amos.Catalog)
    bases: MutableMapping[str, Type[Any]] = dataclasses.field(
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
        
    def add_base(self, item: Type[Any]) -> None:
        """Adds 'item' as a base kind in the 'bases' dict.

        Args:
            item (Type[Any]): item to add to the 'bases' dict.
            
        """
        name = amos.namify(item = item)
        self.bases[name] = item
        return
        
    def add_kind(self, item: Union[object, Type[Any]]) -> None:
        """Adds 'item' as a base kind in the 'bases' dict.

        Args:
            item (Type[Any]): item to add to the 'bases' dict.
            
        """
        base = self.classify(item = item)
        name = amos.namify(item = item)
        self.kinds[name] = base
        return
                
    def classify(self, item: Union[object, Type[Any]]) -> str:
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
        for name, kind in self.bases.items():
            if issubclass(item, kind):
                return name
        raise TypeError(f'{item} does not match a known type')
   
    @classmethod
    def create(cls, *args, **kwargs):
        """Creates a class instance."""
        return cls(*args, **kwargs)  
        
    def deposit(
        self, 
        item: Union[Type[Any], object],
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
        self.add_kind(item = item)
        super().deposit(item = item, name = name)
        return


GENERICS: Repository = Repository()
    
          
@dataclasses.dataclass
class ProjectBase(amos.Registrar, abc.ABC):
    """Mixin for all project base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because Registrar will often be used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        if ProjectBase in cls.__bases__:
            key = amos.namify(item = cls)
            PROJECT_BASES[key] = cls
        
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(cls, *args, **kwargs):
        """Creates a class instance."""
        pass
  
         
@dataclasses.dataclass    
class Parameters(amos.Dictionary):
    """Creates and stores parameters for part of a chrisjen project.
    
    The use of Parameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the contents of the
    'contents' attribute into an ordinary set of kwargs. In this way, it can 
    serve as a drop-in replacement for a dict that would ordinarily be used for 
    accumulating keyword arguments.
    
    If a chrisjen class uses a Parameters instance, the 'finalize' method should 
    be called before that instance's 'implement' method in order for each of the 
    parameter types to be incorporated.
    
    Args:
        contents (Mapping[str, Any]): keyword parameters for use by a chrisjen
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. To properly match 
            parameters in a Settings instance, 'name' should be the prefix to 
            "_parameters" as a section name in a Settings instance. Defaults to 
            None. 
        default (Mapping[str, Any]): default parameters that will be used if 
            they are not overridden. Defaults to an empty dict.
        implementation (Mapping[str, str]): parameters with values that can only 
            be determined at runtime due to dynamic nature of chrisjen and its 
            workflows. The keys should be the names of the parameters and the 
            values should be attributes or items in 'contents' of 'project' 
            passed to the 'finalize' method. Defaults to an emtpy dict.
        selected (Sequence[str]): an exclusive list of parameters that are 
            allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in an Outline instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: Optional[str] = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(
        default_factory = dict)
    selected: Sequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, item: Any, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            item (Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting amos.
        parameters = self.default
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(item = item))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(item = item))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Adds any passed kwargs, which will override any other parameters.
        parameters.update(kwargs)
        # Limits parameters to those in 'selected'.
        if self.selected:
            parameters = {k: parameters[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_settings(self, item: Any) -> dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (bobbie.Settings): instance with possible 
                parameters.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        if hasattr(item, 'outline'):
            parameters = item.outline.implementation[self.name]
        else:
            try:
                parameters = item.settings[f'{self.name}_parameters']
            except KeyError:
                suffix = self.name.split('_')[-1]
                prefix = self.name[:-len(suffix) - 1]
                try:
                    parameters = item.settings[f'{prefix}_parameters']
                except KeyError:
                    try:
                        parameters = item.settings[f'{suffix}_parameters']
                    except KeyError:
                        parameters = {}
        return parameters
   
    def _at_runtime(self, item: Any) -> dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            item (Project): instance from which implementation 
                parameters can be derived.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(item, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = item.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        return self

    
@dataclasses.dataclass
class Manager(holden.System):
    """Base class for creating, managing, and iterating a workflow.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (MutableMapping[Hashable, Worker]): keys are the name or 
            other identifier for the stored Worker instances and values are 
            Worker instances. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a nodes.Component in 
            'options' to use. Defaults to None.
            
                          
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    repository: ClassVar[Repository] = Repository()
    
    # """ Properties """
    
    # @property
    # def workers(self) -> MutableMapping[Hashable, Worker]:
    #     return {self._name_worker: i for i in self.contents}
           
    # """ Public Methods """ 
           
    # def implement(
    #     self,
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Applies 'contents' to 'project'.
        
    #     Args:
    #         project (base.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         base.Project: with possible changes made.
            
    #     """
    #     if len(self.contents) > 1 and project.settings.general['parallelize']:
    #         project = self._implement_in_parallel(project = project, **kwargs)
    #     else:
    #         project = self._implement_in_serial(project = project, **kwargs)
    #     return project      

    # """ Private Methods """
   
    # def _implement_in_parallel(
    #     self, 
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Applies 'implementation' to 'project' using multiple cores.

    #     Args:
    #         project (Project): chrisjen project to apply changes to and/or
    #             gather needed data from.
                
    #     Returns:
    #         Project: with possible alterations made.       
        
    #     """
    #     if project.parallelize:
    #         with multiprocessing.Pool() as pool:
    #             project = pool.starmap(
    #                 self._implement_in_serial, 
    #                 project, 
    #                 **kwargs)
    #     return project 

    # """ Private Methods """
    
    # def _name_worker(self) -> str:
    #     """[summary]

    #     Returns:
    #         str: [description]
            
    #     """
    #     return amos.uniqify(
    #         key = self._worker_prefix, 
    #         dictionary = self.contents)
    
    
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[bobbie.Settings]): configuration settings for the 
            project. Defaults to None.
        filer (Optional[filing.Filer]): a filing filer for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        bases (ProjectBases): base classes for a project. Users can set
            different bases that will automatically be used by the Project
            framework. Defaults to a ProjectBases instance with the default 
            base classes.
        data (Optional[object]): any data object for the project to be applied. 
            If it is None, an instance will still execute its workflow, but it 
            won't apply it to any external data. Defaults to None.
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
    settings: Optional[bobbie.Settings] = None
    filer: Optional[nagata.FileManager] = None
    bases: MutableMapping[str, Type[Any]] = dataclasses.field(
        default_factory = lambda: PROJECT_BASES)
    data: Optional[object] = None
    identification: Optional[str] = None
    outline: Optional[object] = None
    workflow: Optional[object] = None
    summary: Optional[object] = None
    automatic: bool = True
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates core attributes.
        self._validate_settings()
        self._validate_name()
        self._validate_identification()
        # self._validate_bases()
        self._validate_filer()
        # self._validate_workflow()
        # self._validate_results()
        self._validate_data()
        # Sets multiprocessing technique, if necessary.
        self._set_parallelization()
        # Calls 'complete' if 'automatic' is True.
        if self.automatic:
            self.complete()
    
    """ Properties """
         
    # @property
    # def options(self) -> amos.Library:
    #     """Returns the current options of available workflow components.

    #     Returns:
    #         amos.Library: options of workflow components.
            
    #     """        
    #     return self.bases['component'].library
  
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
       
    """ Public Methods """
        
    def complete(self) -> None:
        """Iterates through all stages."""
        if self.outline is None:
            self.outline = workshop.create_outline(project = self)
        if self.workflow is None:
            self.workflow = workshop.create_workflow(project = self)
        if self.result is None:
            self.results = workshop.create_results(project = self)
        return self
     
    # def draft(self) -> None:
    #     """Creates a workflow instance based on 'settings'."""
    #     self.workflow = self.workflow.create(project = self)
    #     return self
        
    # def execute(self) -> None:
    #     """Creates a results instance based on 'workflow'."""
    #     self.results = self.results.create(project = self)
    #     return self
          
    """ Private Methods """
            
    def _validate_settings(self) -> None:
        """Creates or validates 'settings'."""
        if inspect.isclass(self.settings):
            self.settings = self.settings(project = self)
        if (self.settings is None 
                or not isinstance(self.settings, self.settings)):
            self.settings = self.settings.create(
                item = self.settings,
                project = self)
        elif isinstance(self.settings, self.settings):
            self.settings.project = self
        return self
              
    def _validate_name(self) -> None:
        """Creates or validates 'name'."""
        if self.name is None:
            settings_name = workshop.infer_project_name(project = self)
            if settings_name is None:
                self.name = self.name or amos.namify(item = self)
            else:
                self.name = settings_name
        return self  
         
    def _validate_identification(self) -> None:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        Raises:
            TypeError: if the 'identification' attribute is neither a str nor
                None.
                
        """
        if self.identification is None:
            prefix = self.name + '_'
            self.identification = amos.datetime_string(prefix = prefix)
        elif not isinstance(self.identification, str):
            raise TypeError('identification must be a str or None type')
        return self
    
    def _validate_filer(self) -> None:
        """Creates or validates 'filer'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        return self
       
    # def _validate_bases(self) -> None:
    #     """Creates or validates 'bases'."""
    #     if inspect.isclass(self.bases):
    #         self.bases = self.bases()
    #     if (not isinstance(self.bases, ProjectBases)
    #         or not amos.has_attributes(
    #             item = self,
    #             attributes = [
    #                 'filer', 'component', 'director', 'settings', 'stage', 
    #                 'workflow'])):
    #         self.bases = ProjectBases()
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
    
    def _validate_data(self) -> None:
        """Creates or validates 'data'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        return self
    
    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'settings'."""
        if ('general' in self.settings
                and 'parallelize' in self.settings['general'] 
                and self.settings['general']['parallelize']):
            if not globals()['multiprocessing']:
                import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return self  
   
    