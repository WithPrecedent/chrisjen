"""
nodes: base classes for nodes in a chrisjen workflow
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
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, Sequence, Set)
import contextlib
import dataclasses
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

import amos
import holden
import miller

from . import base
 
  
@dataclasses.dataclass
class Component(amos.LibraryFactory, holden.Labeled, base.ProjectBase, abc.ABC):
    """Base class for nodes in a chrisjen project.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'execute' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    manager: ClassVar[Type[base.Manager]] = base.Manager  
    
    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'manager.repository'."""
        # Calls other '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if Component in cls.__bases__:
            cls.manager.repository.add_base(item = cls)
        key = amos.namify(item = cls)
        cls.manager.repository.deposit(item = cls, name = key)   
            
    def __post_init__(self) -> None:
        """Initializes an instance."""
        # Calls other '__post_init__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__post_init__(*args, **kwargs) # type: ignore
        key = amos.namify(item = self)
        self.manager.repository.deposit(item = self, name = key)
                       
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(self, item: Any, *args: Any, **kwargs: Any) -> Any:
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
    
    def execute(self, item: Any, *args: Any, **kwargs: Any) -> Any:
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
       
    def finalize(self, item: Any, *args: Any, **kwargs: Any) -> None:
        """Finalizes the parameters for implementation of the node.

        Args:
            project (Project): instance from which data needed for 
                implementation should be derived for finalizing parameters.
            
        """
        with contextlib.suppress(AttributeError):
            self.parameters.finalize(item = item)
        parameters = self.parameters
        parameters.update(**kwargs)
        self.parameters = parameters
        return self
           
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


@dataclasses.dataclass   
class Criteria(base.ProjectBase):
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
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)


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
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

   
def is_component(item: Union[object, Type[Any]]) -> bool:
    """Returns whether 'item' is a component.

    Args:
        item (Union[object, Type[Any]]): instance or class to check.

    Returns:
        bool: whether 'item' is a component.
        
    """
    return (
        miller.has_attributes(item, ['name', 'contents', 'parameters'])
        and miller.has_methods(item, ['execute']))
    