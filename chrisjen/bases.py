"""
bases: base classes for a chrisjen project
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
    ProjectNode (amos.Node, abc.ABC):
    ProjectComponent (ProjectOptions, ProjectNode, abc.ABC):
    ProjectStage (ProjectOptions, ProjectNode, abc.ABC):
    ProjectDirector (ProjectOptions, Iterator):

To Do:
    Make ProjectNode a subclass of amos.Node by fixing the proxy access methods
        that currently return errors.
            
"""
from __future__ import annotations
import abc
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, Sequence)
import copy
import dataclasses
import functools
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

if TYPE_CHECKING:
    from . import interface

 
# @dataclasses.dataclass
# class ProjectCatalog(amos.Catalog):
#     """[summary]

#     Args:
#         contents (Mapping[Hashable, Any]]): stored dictionary. Defaults to an 
#             empty dict.
#         default_factory (Any): default value to return when the 'get' method is 
#             used.
#         default (Sequence[Any]]): a list of keys in 'contents' which will be 
#             used to return items when 'default' is sought. If not passed, 
#             'default' will be set to all keys.
#         always_return_list (bool): whether to return a list even when the key 
#             passed is not a list or special access key (True) or to return a 
#             list only when a list or special access key is used (False). 
#             Defaults to False.
                     
#     """
#     contents: Mapping[str, Type[Any]] = dataclasses.field(
#         default_factory = dict)
#     default_factory: Optional[Any] = None
#     default: Optional[Any] = 'all'
#     always_return_list: bool = False
    
#     """ Public Methods """
 

@dataclasses.dataclass
class ProjectOptions(object):
    """Mixin which registers subclasses and provides construction methods.
    
    Args:
        catalog (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
            
    """
    catalog: ClassVar[amos.Catalog] = amos.Catalog()
    
    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass."""
        # Because ProjectOptions is used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        name = amos.get_name(item = cls)
        cls.catalog[name] = cls

    """ Properties """
    
    @property
    def plurals(self) -> tuple[str]:
        """Returns all stored names and naive plurals of those names.
        
        Returns:
            tuple[str]: all names with an 's' added in order to create simple 
                plurals combined with the stored keys.
                
        """
        return tuple([key + 's' for key in self.contents.keys()])
        
    """ Public Methods """

    @classmethod
    def instance(
        cls, 
        item: Union[str, Sequence[str]], 
        **kwargs: Any) -> ProjectOptions:
        """Creates an instance of a ProjectOptions subclass from 'item'.
        
        Args:
            item (Any): any supported data structure which acts as a source for
                creating a ProjectOptions or a str which matches a key in 
                'catalog''.
                                
        Returns:
            ProjectOptions: a ProjectOptions subclass instance created based 
                on 'item' and any passed arguments.
                
        """
        return cls.catalog[item](**kwargs)

    @classmethod
    def select(cls, item: Union[str, Sequence[str]]) -> Type[ProjectOptions]:
        """Returns a ProjectOptions subclass based on 'item'.
        
        Args:
            item (Any): any supported data structure which acts as a source for
                creating a ProjectOptions or a str which matches a key in 
                'catalog''.
                                
        Returns:
            Type[ProjectOptions]: a ProjectOptions subclass.
                
        """
        return cls.catalog[item]   
    
    
@dataclasses.dataclass    
class Parameters(amos.Dictionary):
    """Creates and stores parameters for a Component.
    
    The use of Parameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the 
    'contents' attribute an ordinary set of kwargs. In this way, it can serve as 
    a drop-in replacement for a dict that would ordinarily be used for 
    accumulating keyword arguments.
    
    If a chrisjen class uses a Parameters instance, the 'finalize' 
    method should be called before that instance's 'implement' method in order 
    for each of the parameter types to be incorporated.
    
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
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(project = project))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(project = project))
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
     
    def _from_settings(self, project: interface.Project) -> dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (amos.Settings): instance with possible 
                parameters.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        if hasattr(project, 'outline'):
            parameters = project.outline.runtime[self.name]
        else:
            try:
                parameters = project.settings[f'{self.name}_parameters']
            except KeyError:
                suffix = self.name.split('_')[-1]
                prefix = self.name[:-len(suffix) - 1]
                try:
                    parameters = project.settings[f'{prefix}_parameters']
                except KeyError:
                    try:
                        parameters = project.settings[f'{suffix}_parameters']
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
class Stage(ProjectOptions, abc.ABC):
    """Base class for stages in a chrisjen project.

    Args:
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing. Defaults to None.
        catalog (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
            
    """
    contents: Optional[Any] = None
    name: Optional[str] = None
    catalog: ClassVar[amos.Catalog] = amos.Catalog()

             
@dataclasses.dataclass
class ProjectNode(ProjectOptions, abc.ABC):
    """Base class for nodes in a chrisjen project.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        catalog (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    iterations: Union[int, str] = 1
    catalog: ClassVar[amos.Catalog] = amos.Catalog()
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as ProjectNode.
        
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
        cls.__hash__ = ProjectNode.__hash__ # type: ignore
        cls.__eq__ = ProjectNode.__eq__ # type: ignore
        cls.__ne__ = ProjectNode.__ne__ # type: ignore

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
                if hasattr(self.parameters, 'finalize'):
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
            
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return issubclass(subclass, Hashable) and hasattr(subclass, 'name')
               
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instances' is an instance of this class.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' is an instance of this class.
            
        """
        return amos.is_node(item = instance)
    
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
class Component(ProjectNode, ProjectOptions, abc.ABC):
    """Base class for nodes in a project workflow.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
  
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1
    
    """ Public Methods """

    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        try:
            project = self.contents.execute(project = project, **kwargs)
        except AttributeError:
            project = self.contents(project, **kwargs)
        return project   
    
            
@dataclasses.dataclass
class Worker(Component, abc.ABC):
    """Keystone class for parts of a chrisjen workflow.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                              
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    iterations: Union[int, str] = 1

    """ Public Methods """  
    
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    

    """ Private Methods """
    
    def _implement_in_serial(self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies stored nodes to 'project' in order.

        Args:
            project (Project): chrisjen project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        for node in self.paths[0]:
            project = node.execute(project = project, **kwargs)
        return project 
        
   
@dataclasses.dataclass   
class Criteria(ProjectOptions):
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
        catalog (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
                      
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    catalog: ClassVar[amos.Catalog] = amos.Catalog()
    