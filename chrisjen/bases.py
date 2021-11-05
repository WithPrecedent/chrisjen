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
import collections
from collections.abc import (
    Collection, Hashable, Iterable, Iterator, Mapping, MutableMapping, Sequence, 
    Set)
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


CLERK: Type[Any] = amos.Clerk
DIRECTOR: Type[Any] = globals()['ProjectDirector']
LIBRARY: Type[Any] = globals()['ProjectLibrary']
NODE: Type[Any] = globals()['ProjectComponent']
PARAMETERS: Type[Any] = globals()['ProjectParameters']
SETTINGS: Type[Any] = amos.Settings
STAGE: Type[Any] = globals()['ProjectStage']

def get_base(base_type: str) -> None:
    return globals()[base_type.upper()]

def set_base(base_type: str, base: Type[Any]) -> None:
    globals()[base_type.upper()] = base
    return


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
class LibraryFactory(abc.ABC):
    """Mixin which registers subclasses, instances, and kinds.
    
    Args:
        library (ClassVar[ProjectLibrary]): project library of classes, 
            instances, and base classes. 
            
    """
    library: ClassVar[ProjectLibrary] = dataclasses.field(
        default_factory = ProjectLibrary)
    
    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass."""
        # Because LibraryFactory is used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        key = amos.get_name(item = cls)
        cls.library.classes[key] = cls
            
    def __post_init__(self) -> None:
        try:
            super().__post_init__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        key = amos.get_name(item = self)
        self.__class__.library[key] = self 
    
    """ Public Methods """

    @classmethod
    def create(
        cls, 
        item: Union[str, Sequence[str]], 
        *args: Any, 
        **kwargs: Any) -> LibraryFactory:
        """Creates an instance of a LibraryFactory subclass from 'item'.
        
        Args:
            item (Any): any supported data structure which acts as a source for
                creating a LibraryFactory or a str which matches a key in 
                'library'.
                                
        Returns:
            LibraryFactory: a LibraryFactory subclass instance created based 
                on 'item' and any passed arguments.
                
        """
        return cls.library.instance(item, *args, **kwargs)

    
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
     
    def _from_settings(self, settings: amos.Settings) -> dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (amos.Settings): instance with possible 
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
    library: ClassVar[ProjectLibrary] = dataclasses.field(
        default_factory = ProjectLibrary)
      
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
class ProjectStage(object):
    """Base classes for project stages.
    
    Args:
        contents (Optional[Collection]): collection of data at a project stage.
            
    """
    contents: Optional[Collection] = None
    name: Optional[str] = None
    library: ClassVar[ProjectLibrary] = dataclasses.field(
        default_factory = ProjectLibrary)
     
    
@dataclasses.dataclass
class ProjectDirector(Iterator, abc.ABC):
    """Iterator for chrisjen Project instances.
    
    
    """
    project: interface.Project
    options: types.ModuleType = dir(sys.modules[__name__])
    stages: Sequence[Union[str, Type[ProjectStage]]] = dataclasses.field(
        default_factory = lambda: ['workflow', 'results'])
    library: ClassVar[ProjectLibrary] = dataclasses.field(
        default_factory = ProjectLibrary)
       
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