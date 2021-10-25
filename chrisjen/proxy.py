"""
proxy: wrapper classes and relted functions
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
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
    Node (base.Proxy)
    nodify (Callable)

ToDo:
    Add support for ordinary python classes to 'nodify'.
        
"""
from __future__ import annotations
import abc
from collections.abc import Collection, Hashable
import dataclasses
import inspect
from typing import Any, Optional, Type, Union

from . import base
from . import check
from . import utilities

   
@dataclasses.dataclass
class Node(base.Proxy):
    """Vertex wrapper to provide hashability to any object.
    
    Node acts a basic wrapper for any item stored in a composite structure.
    
    By inheriting from Proxy, a Node will act as a pass-through class for access
    methods seeking attributes not in a Node instance but rather stored in 
    'contents'.
    
    Args:
        contents (Optional[Any]): any stored item(s). Defaults to None.
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            
    """
    contents: Optional[Any] = None
    name: Optional[str] = None

    """ Initialization Methods """
    
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as Node.
        
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
        cls.__hash__ = Node.__hash__ # type: ignore
        cls.__eq__ = Node.__eq__ # type: ignore
        cls.__ne__ = Node.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or utilities.get_name(item = self)
                
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
        return check.is_node(item = instance)
    
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

 
@dataclasses.dataclass
class Nodes(base.Bunch, abc.ABC):
    """Collection of nodes.
    
    Nodes are not guaranteed to be in order. 

    Args:
        contents (Optional[Any]): any stored item(s). Defaults to None.
            
    """
    contents: Optional[Collection[Node]] = None
    
    """ Dunder Methods """ 
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return check.is_nodes(item = instance)
    

def nodify(item: Union[Type[Any], object]) -> Union[Type[Node], Node]:
    """Converts a class or object into a node for a composite data structure.
    
    Currently, the method supports any object but only python dataclass types 
    for classes. And those dataclasses should not have a '__post_init__' 
    method - it will be overwritten by 'nodify'.

    Args:
        item (Union[Type[Any], object]): class or instance to transform into a  
            node.

    Returns:
        Union[Type[Node], Node]: a node class or instance.
        
    """
    item.__hash__ = Node.__hash__ # type: ignore
    item.__eq__ = Node.__eq__ # type: ignore
    item.__ne__ = Node.__ne__ # type: ignore
    if inspect.isclass(item):
        item.__post_init__ = Node.__post_init__ # type: ignore
    else:
        if not hasattr(item, 'name') or not item.name:
            item.name = utilities.get_name(item = item)
    return item
