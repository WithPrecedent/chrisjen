"""
bases: base classes for a chrisjen project
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
    amos.Catalog (amos.Catalog):
    amos.LibraryFactory (object):
    Parameters (amos.Dictionary):
    Component (amos.LibraryFactory, abc.ABC):
    Criteria (amos.LibraryFactory):
    Workflow (amos.System):
    Results (object):

To Do:
    Make Component a subclass of amos.Node by fixing the proxy access methods
        that currently return errors.
            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, Sequence, Set)
import copy
import dataclasses
import functools
import inspect
import itertools
import multiprocessing
import pathlib
from typing import (
    Any, ClassVar, MutableSequence, Optional, Type, TYPE_CHECKING, Union)

import amos

from . import workshop

if TYPE_CHECKING:
    from . import configuration
    from . import filing
    from . import workshop
 
   
@dataclasses.dataclass
class ProjectBases(object):
    """Base classes for a chrisjen project.
    
    Args:
        clerk (Type[Any]): base class for a project filing clerk. Defaults to
            filing.Clerk.
        settings (Type[Any]): base class for project configuration settings.
        outline 
            Defaults to amos.Settings.
        workflow
        results
        node (Type[amos.LibraryFactory]): base class for nodes in a project
            workflow. Defaults to Component.
        criteria
      
    """
    clerk: Type[Any] = filing.Clerk
    settings: Type[Any] = configuration.ProjectSettings
    outline: Type[Any] = Outline
    workflow: Type[Any] = Workflow
    results: Type[Any] = Results
    node: Type[amos.LibraryFactory] = Component
    criteria: Type[Any] = Criteria
    
       
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[amos.Settings]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[filing.Clerk]): a filing clerk for loading and saving 
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
    
    Attributes:
        library (ProjectLibrary): a library of all available node classes
            that can be used in a project workflow. By default, it is a
            property that points to 'node.library'.
        results (amos.Composite): stored results from the execution of the
            project 'workflow'. It is created when the 'complete' method is
            called.
        outline (Outline): high-level view of the project in a different
            format than 'settings'. It is a cached property that calls the 
            'create_outline' function the first time it is called and becomes an 
            attribute with an outline after that.
        workflow (amos.Composite): workflow process for executing the project.
            It is a cached property that calls the 'create_workflow' function
            the first time it is called and becomes an attribute with a 
            workflow after that.
            
    """
    name: Optional[str] = None
    settings: Optional[amos.Settings] = None
    clerk: Optional[filing.Clerk] = None
    bases: ProjectBases = ProjectBases()
    data: Optional[object] = None
    identification: Optional[str] = None
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
        self._validate_bases()
        self._validate_clerk()
        # self._validate_workflow()
        # self._validate_results()
        self._validate_data()
        # Sets multiprocessing technique, if necessary.
        self._set_parallelization()
        # Calls 'complete' if 'automatic' is True.
        if self.automatic:
            self.complete()
    
    """ Properties """
         
    @property
    def options(self) -> ProjectLibrary:
        """Returns the current options of available workflow components.

        Returns:
            ProjectLibrary: options of workflow components.
            
        """        
        return self.node.library
  
    @options.setter
    def options(self, value: ProjectLibrary) -> None:
        """Sets the current options of available workflow components.

        Arguments:
            value (ProjectLibrary): new options for workflow components.
            
        """        
        self.node.library = value
        return self
    
    @functools.cached_property
    def outline(self) -> Outline:
        """Returns project outline based on 'settings'

        Returns:
            Outline: the outline derived from 'settings'.
            
        """        
        return workshop.create_outline(project = self)
    
    @functools.cached_property
    def workflow(self) -> Workflow:
        """Returns workflow based on 'settings'

        Returns:
            Workflow: the workflow derived from 'settings'.
            
        """        
        return workshop.create_workflow(project = self)
       
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        settings: Union[pathlib.Path, str, amos.Settings],
        **kwargs) -> Project:
        """Returns a Project instance based on 'settings' and kwargs.

        Args:
            settings (Union[pathlib.Path, str, amos.Settings]): a path to a file
                containing configuration settings or a Settings instance.

        Returns:
            Project: an instance based on 'settings' and kwargs.
            
        """        
        return cls(settings = settings, **kwargs)
       
    """ Public Methods """
        
    def complete(self) -> None:
        """Iterates through all stages."""
        self.results = self.results.create(project = self)
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
                self.name = self.name or amos.get_name(item = self)
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
         
    def _validate_bases(self) -> None:
        """Creates or validates 'bases'."""
        if inspect.isclass(self.bases):
            self.bases = self.bases()
        if (not isinstance(self.bases, ProjectBases)
            or not amos.has_attributes(
                item = self,
                attributes = [
                    'clerk', 'component', 'director', 'settings', 'stage', 
                    'workflow'])):
            self.bases = ProjectBases()
        return self

    
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
   
@dataclasses.dataclass
class ProjectSettings(amos.Settings):
    """Loads and stores configuration settings.

    Args:
        contents (MutableMapping[str, Any]): a dict for storing configuration 
            options. Defaults to en empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.
        sources (ClassVar[Mapping[Type[Any], str]]): keys are types for sources 
            for creating an instance and values are the suffix for the 
            classmethod to be called using the matching key type.
        suffixes (ClassVar[dict[str, tuple[str]]]): keys are the type of data
            that is contained in the section and values are the str names of
            suffixes (or complete matches) of sections that are relevant to the
            str key type. Defaults to dict with data in dataclasses field.

    """
    contents: MutableMapping[str, Any] = dataclasses.field(
        default_factory = dict)
    default: Mapping[str, Any] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    sources: ClassVar[Mapping[Type[Any], str]] = {
        MutableMapping: 'dictionary', 
        pathlib.Path: 'path',  
        str: 'path'}
    suffixes: ClassVar[dict[str, tuple[str]]] = {
        'design': ('design',),
        'files': ('clerk', 'filer', 'files'),
        'general': ('general',),
        'parameters': ('parameters',),
        'project': ('project',),
        'structure': ('structure',)}
    
    """ Properties """       

    @property
    def components(self) -> dict[str, dict[str, Any]]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        special_suffixes = itertools.chain_from_iterable(self.suffixes.values())
        component_sections = {}       
        for name, section in self.items():
            if not name.endswith(special_suffixes):
                component_sections[name] = section
        return component_sections
       
    @property
    def filer(self) -> dict[str, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[str, Any]: [description]
            
        """  
        for name in self.suffixes['files']:
            try:
                return self[name]
            except KeyError:
                pass      
        raise KeyError(
            'ProjectSettings does not contain files-related configuration '
            'options')

    @property
    def general(self) -> dict[str, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[str, Any]: [description]
            
        """        
        for name in self.suffixes['general']:
            try:
                return self[name]
            except KeyError:
                pass  
        raise KeyError(
            'ProjectSettings does not contain general configuration options')

    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        parameter_sections = {}      
        for name, section in self.items():
            if name.endswith(self.suffixes['parameters']):
                parameter_sections[name] = section
        return parameter_sections
        
    @property
    def structure(self) -> dict[str, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[str, Any]: [description]
            
        """        
        for name, section in self.items():
            if name.endswith(self.suffixes['structure']):
                return section
        raise KeyError(
            'ProjectSettings does not contain structure configuration options')

    """ Class Methods """
    
    @classmethod
    def validate(cls, project: Project) -> Project:
        """Creates or validates 'project.settings'.

        Args:
            project (Project): an instance with a 'settings' 
                attribute.

        Returns:
            Project: an instance with a validated 'settings'
                attribute.
            
        """        
        if inspect.isclass(project.settings):
            project.settings = project.settings()
        elif project.settings is None:
            project.settings = cls.create(
                item = project.settings,
                project = project)
        return project 
    



@dataclasses.dataclass  # type: ignore
class ProjectLibrary(amos.Library):
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
       
       
@dataclasses.dataclass    
class Parameters(amos.Dictionary):
    """Creates and stores parameters for a Component.
    
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
            settings (amos.Settings): instance with possible 
                parameters.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        if hasattr(item, 'outline'):
            parameters = item.outline.runtime[self.name]
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
class Component(amos.LibraryFactory, abc.ABC):
    """Base class for nodes in a chrisjen project.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'project'
            passed to the 'execute' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
            
    Attributes:
        library (ClassVar[ProjectLibrary]): subclasses and instances stored with 
            str keys derived from the 'amos.get_name' function.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)  
    library: ClassVar[ProjectLibrary] = ProjectLibrary()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as Component.
        
        This is necessary because dataclasses, by design, do not automatically 
        inherit the hash and equivalance dunder methods from their super 
        classes.
        
        """
        # Calls other '__init_subclass__' methods for parent and mixin classes.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        # Copies hashing related methods to a subclass.
        cls.__hash__ = Component.__hash__ # type: ignore
        cls.__eq__ = Component.__eq__ # type: ignore
        cls.__ne__ = Component.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or amos.get_name(item = self)
        # Calls other '__post_init__' methods for parent and mixin classes.
        try:
            super().__post_init__() # type: ignore
        except AttributeError:
            pass
        
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(self, item: Any, **kwargs) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        pass

    """ Public Methods """
    
    def execute(self, item: Any, **kwargs) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        if self.contents not in [None, 'None', 'none']:
            self.finalize(item = item, **kwargs)
            result = self.implement(item = item, **self.parameters)
        return result 
       
    def finalize(self, item: Any, **kwargs) -> None:
        """Finalizes the parameters for implementation of the node.

        Args:
            project (Project): instance from which data needed for 
                implementation should be derived for finalizing parameters.
            
        """
        if self.parameters:
            if amos.has_method(self.parameters, 'finalize'):
                self.parameters.finalize(item = item)
            parameters = self.parameters
            parameters.update(kwargs)
        else:
            parameters = kwargs
        self.parameters = parameters
        return self
           
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (
            amos.is_node(subclass) 
            and amos.has_attributes(subclass, ['name', 'contents', 'options'])
            and amos.has_method(subclass, 'execute'))
               
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instances' is an instance of this class.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' is an instance of this class.
            
        """
        return (
            issubclass(instance.__class__, cls)
            and isinstance(instance.name, str))
    
    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a composite object that uses a dict as
        its base storage type.
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Makes Node hashable so that it can be used as a key in a dict.

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


@dataclasses.dataclass   
class Criteria(amos.LibraryFactory):
    """Evaluates paths for use by Judge
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
            
    Attributes:
        library (ClassVar[ProjectLibrary]): subclasses and instances stored with 
            str keys derived from the 'amos.get_name' function.
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    library: ClassVar[ProjectLibrary] = ProjectLibrary()
