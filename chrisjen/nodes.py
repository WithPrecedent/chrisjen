"""
nodes: base classes for nodes in a chrisjen project
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
    Make Component a subclass of amos.Node by fixing the proxy access methods
        that currently return errors.
            
"""
from __future__ import annotations
import abc
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, Sequence, Set)
import dataclasses
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

import amos

from . import base
 

@dataclasses.dataclass  # type: ignore
class ProjectLibrary(amos.Library, base.ProjectBase):
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
class Parameters(amos.Dictionary, base.ProjectBase):
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
            settings (bobbie.Settings): instance with possible 
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
class Component(amos.LibraryFactory, base.ProjectBase, abc.ABC):
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
            str keys derived from the 'amos.namify' function.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)  
    library: ClassVar[ProjectLibrary] = base.PROJECT_BASES['library']()
    
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
class Criteria(amos.LibraryFactory, base.ProjectBase):
    """Evaluates paths for use by Judge.
    
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
            str keys derived from the 'amos.namify' function.
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    library: ClassVar[ProjectLibrary] = base.PROJECT_BASES['library']()


@dataclasses.dataclass   
class Stage(amos.LibraryFactory, base.ProjectBase):
    """A stage in a chrisjen project development process.
    
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
            str keys derived from the 'amos.namify' function.
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    library: ClassVar[ProjectLibrary] = base.PROJECT_BASES['library']()