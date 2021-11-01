"""
options: base classes for a project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
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

"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Iterable, Iterator, Mapping, MutableMapping, Sequence)
import copy
import dataclasses
import inspect
import itertools
import sys
import types
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import workshop

if TYPE_CHECKING:
    from . import interface


CLERK: Type[Any] = globals()['Clerk']
DIRECTOR: Type[Any] = globals()['Director']
LIBRARY: Type[Any] = globals()['ProjectLibrary']
NODE: Type[Any] = globals()['Component']
PARAMETERS: Type[Any] = globals()['ProjectParameters']
SETTINGS: Type[Any] = globals()['ProjectSettings']
STAGE: Type[Any] = globals()['Stage']

def get_base(base_type: str) -> None:
    return globals()[base_type.upper()]

def set_base(base_type: str, base: Type[Any]) -> None:
    globals()[base_type.upper()] = base
    return

    
@dataclasses.dataclass    
class ProjectParameters(amos.Dictionary):
    """Creates and stores parameters for a Component.
    
    The use of ProjectParameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    ProjectParameters can be unpacked with '**', which will turn the 'contents' 
    attribute an ordinary set of kwargs. In this way, it can serve as a drop-in
    replacement for a dict that would ordinarily be used for accumulating 
    keyword arguments.
    
    If a chrisjen class uses a ProjectParameters instance, the 'finalize' method 
    should be called before that instance's 'implement' method in order for each 
    of the parameter types to be incorporated.
    
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

    def finalize(self, project: interface.Project, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            project (interface.Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting amos.
        parameters = self.default
        parameters.update(kwargs)
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(settings = project.settings))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(project = project))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Limits parameters to those in 'selected'.
        if self.selected:
            self.contents = {k: self.contents[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_settings(self, settings: ProjectSettings) -> dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (ProjectSettings): instance with possible 
                parameters.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        try:
            parameters = settings[f'{self.name}_parameters']
        except KeyError:
            suffix = self.name.split('_')[-1]
            prefix = self.name[:-len(suffix) - 1]
            try:
                parameters = settings[f'{prefix}_parameters']
            except KeyError:
                try:
                    parameters = settings[f'{suffix}_parameters']
                except KeyError:
                    parameters = {}
        return parameters
   
    def _at_runtime(self, project: interface.Project) -> dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            project (interface.Project): instance from which implementation 
                parameters can be derived.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(project, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = project.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        return self


@dataclasses.dataclass
class ProjectLibrary(amos.Library):
    """Stores project classes and class instances.
    
    When searching for matches, instances are prioritized over classes.
    
    Args:
        classes (Catalog): a catalog of stored classes. Defaults to any empty
            Catalog.
        instances (Catalog): a catalog of stored class instances. Defaults to an
            empty Catalog.
        kinds (Catalog): kind types of nodes. Defaults to an empty Catalog.
                 
    """
    classes: amos.Catalog[str, Type[Any]] = dataclasses.field(
        default_factory = amos.Catalog)
    instances: amos.Catalog[str, object] = dataclasses.field(
        default_factory = amos.Catalog)
    kinds: amos.Catalog[str, Type[Any]] = dataclasses.field(
        default_factory = amos.Catalog)

    """ Public Methods """
    
    def classify(
        self,
        item: Union[str, Type[NODE], NODE]) -> str:
        """[summary]

        Args:
            item (str): [description]

        Returns:
            str: [description]
            
        """
        for name, _ in self.items():
            if self.is_kind(item = item, kind = name):
                return name
        raise KeyError('item was not found in the project library')

    def instance(
        self, 
        name: Union[str, Sequence[str]], 
        *args, 
        **kwargs) -> object:
        """Returns instance of first match of 'name' in stored catalogs.
        
        The method prioritizes the 'instances' catalog over 'classes' and any
        passed names in the order they are listed.
        
        Args:
            name (Union[str, Sequence[str]]): [description]
            
        Raises:
            KeyError: [description]
            
        Returns:
            object: [description]
            
        """
        names = amos.iterify(name)
        primary = names[0]
        item = None
        for key in names:
            for catalog in ['instances', 'classes']:
                try:
                    item = getattr(self, catalog)[key]
                    break
                except KeyError:
                    pass
            if item is not None:
                break
        if item is None:
            raise KeyError(f'No matching item for {name} was found') 
        elif inspect.isclass(item):
            instance = item(primary, *args, **kwargs)
        else:
            instance = copy.deepcopy(item)
            for key, value in kwargs.items():
                setattr(instance, key, value)  
        return instance 

    def is_kind(
        self, 
        item: Union[str, Type[NODE], NODE],
        kind: str) -> bool:
        """[summary]

        Args:
            item (Union[str, Type[NODE], NODE]): [description]
            kind (str): [description]

        Returns:
            bool: [description]
            
        """
        if isinstance(item, str):
            item = self[item]
        elif isinstance(item, NODE):
            item = item.__class__
        return issubclass(item, self.kinds[kind])        
        
    def parameterify(self, name: Union[str, Sequence[str]]) -> list[str]:
        """[summary]

        Args:
            name (Union[str, Sequence[str]]): [description]

        Returns:
            list[str]: [description]
            
        """        
        item = self.select(name = name)
        return list(item.__annotations__.keys())  

           
@dataclasses.dataclass
class ProjectComponent(amos.Node, workshop.LibraryFactory):
    """Base class for nodes in a project workflow.

    Args:
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty 'ProjectParameters' instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
  
    """
    contents: Optional[Any] = None
    name: Optional[str] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ProjectParameters)
    iterations: Union[int, str] = 1
  
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        pass

    """ Public Methods """
    
    def execute(self, 
        project: interface.Project, 
        iterations: Optional[Union[int, str]] = None, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        iterations = iterations or self.iterations
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if isinstance(self.parameters, ProjectParameters):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if iterations in ['infinite']:
                while True:
                    project = self.implement(project = project, **parameters)
            else:
                for _ in range(iterations):
                    project = self.implement(project = project, **parameters)
        return project


@dataclasses.dataclass
class Director(Iterator, abc.ABC):
    """Iterator for chrisjen Project instances.
    
    
    """
    project: interface.Project
    bases: types.ModuleType = dir(sys.modules[__name__])
    stages: Sequence[Type[str]] = dataclasses.field(default_factory = list)
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets index for iteration.
        self.index = 0
        # Validate stages
        self._validate_stages()
        
    """ Properties """
    
    @property
    def current(self) -> str:
        return list(self.stages.keys())[self.index]
    
    @property
    def previous(self) -> str:
        try:
            return list(self.stages.keys())[self.index -1]
        except IndexError:
            return None
    
    @property
    def subsequent(self) -> str:
        try:
            return list(self.stages.keys())[self.index + 1]
        except IndexError:
            return None
 
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self    

    def get_base(self, base_type: str) -> None:
        return getattr(self.options, base_type.upper())

    def set_base(self, base_type: str, base: Type[Any]) -> None:
        setattr(self.options, base_type, base)
        return
    
    """ Private Methods """
    
    def _validate_stages(self) -> None:
        new_stages = []
        for stage in self.project.stages:
            new_stages.append(self._validate_stage(stage = stage))
        self.project.stages = new_stages
        return

    def _validate_stage(self, stage: Any) -> object:
        if isinstance(stage, str):
            try:
                stage = STAGE.create(stage)
            except KeyError:
                raise KeyError(f'{stage} was not found in Stage registry')
        if inspect.isclass(stage):
            stage = stage()
        return stage
            
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'stages'.
        
        Returns:
            Iterable: of 'stages'.
            
        """
        return self
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index < len(self.stages):
            source = self.previous or 'settings'
            product = self.stages[self.current]
            converter = getattr(self.converters, f'create_{product}')
            if self.project.settings['general']['verbose']:
                print(f'Creating {product} from {source}')
            kwargs = {'project': self.project}
            setattr(self.project, product, converter(**kwargs))
            self.index += 1
            if self.project.settings['general']['verbose']:
                print(f'Completed {product}')
        else:
            raise StopIteration
        return self


@dataclasses.dataclass
class ProjectSettings(amos.Settings):
    """Loads and stores project configuration settings.

    To create settings instance, a user can pass as the 'contents' parameter a:
        1) pathlib file path of a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.

    If 'contents' is imported from a file, settings creates a dict and can 
    convert the dict values to appropriate datatypes. Currently, supported file 
    types are: ini, json, toml, yaml, and python. If you want to use toml, yaml, 
    or json, the identically named packages must be available in your python
    environment.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported). Type conversion is automatically disabled
    if the source file is a python module (assuming the user has properly set
    the types of the stored python dict).

    Because settings uses ConfigParser for .ini files, by default it stores 
    a 2-level dict. The desire for accessibility and simplicity chrisjented this 
    limitation. A greater number of levels can be achieved by having separate
    sections with names corresponding to the strings in the values of items in 
    other sections. 

    Args:
        contents (MutableMapping[Hashable, Any]): a dict for storing 
            configuration  Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.

    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = dict
    default: Mapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    project: Optional[interface.Project] = None

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        if self.project is not None:
            # Converts sections in 'contents' to ProjectSettingsSection types.
            self._sectionify()
    
    """ Properties """
    
    @property
    def kinds(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        return workshop.get_kinds(section = self, project = self.project)
    
    @property
    def connections(self) -> dict[str, list[str]]:
        """[summary]

        Returns:
            dict[str, list[str]]: [description]
            
        """
        return workshop.get_connections(section = self, project = self.project)

    @property
    def designs(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        return workshop.get_designs(section = self, project = self.project)
   
    """ Public Methods """
   
    def link(self, project: interface.Project) -> None:
        """
        """
        self.project = project
        self._sectionify()
        return self
        
    """" Private Methods """
    
    def _sectionify(self) -> None:
        """Converts node-related subsections into ProjectSettingsSections."""
        new_contents = {}
        suffixes = self.project.nodes.suffixes
        for key, value in self.contents.items():
            if any(k.endswith(suffixes) for k in value.keys()):
                section = ProjectSettingsSection(
                    contents = value, 
                    name = key, 
                    settings = self)
                new_contents[key] = section
            else:
                new_contents[key] = value
        self.contents = new_contents
        return


@dataclasses.dataclass
class ProjectSettingsSection(amos.Dictionary):
    """Section of Outline with connections.

    Args:
        contents (MutableMapping[Hashable, Any]]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Any): default value to return when the 'get' method is 
            used. Defaults to None.
                          
    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    name: Optional[str] = None
    settings: Optional[ProjectSettings] = None
    
    """ Properties """
    
    @property
    def suffixes(self) -> list[str]:
        """[summary]

        Raises:
            ValueError: [description]

        Returns:
            list[str]: [description]
            
        """
        if self.project.settings is None:
            raise ValueError(
                'suffixes requires the ProjectSettings to be linked to a '
                'Project instance')
        else:
            return self.settings.project.nodes.suffixes
    
    @property
    def kinds(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        return workshop.get_section_kinds(section = self)
    
    @property
    def connections(self) -> dict[str, list[str]]:
        """[summary]

        Returns:
            dict[str, list[str]]: [description]
            
        """
        return workshop.get_section_connections(section = self)

    @property
    def designs(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        return workshop.get_section_designs(section = self)

    @property
    def names(self) -> list[str]:
        """[summary]

        Returns:
            list[str]: [description]
            
        """
        key_nodes = list(self.connections.keys())
        value_nodes = list(
            itertools.chain.from_iterable(self.connections.values()))
        return amos.deduplicate(item = key_nodes + value_nodes) 

    @property
    def other(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        design_keys = [k for k in self.keys() if k.endswith('design')]
        connection_keys = [k for k in self.keys() if k.endswith(self.suffixes)]
        exclude = design_keys + connection_keys
        return {k: v for k, v in self.contents.items() if k not in exclude}

    """ Public Methods """

    @classmethod
    def from_settings(
        cls, 
        settings: amos.Settings,
        name: str,
        **kwargs) -> ProjectSettingsSection:
        """[summary]

        Args:
            settings (chrisjen.shared.settings): [description]
            name (str):

        Returns:
            ProjectSettingsSection: derived from 'settings'.
            
        """        
        return cls(contents = settings[name], name = name, **kwargs)    
    

@dataclasses.dataclass
class ProjectStage(object):
    """Base classes for project 

    Args:
        contents (Optional[Collection]): collection of data at a project stage.
            
    """
    contents: Optional[Collection] = None
    name: Optional[str] = None
