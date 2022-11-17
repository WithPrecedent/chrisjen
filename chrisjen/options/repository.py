"""
repository: classes to library project assets
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
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import camina

if TYPE_CHECKING:
    from ..core import keystones

     
# @dataclasses.dataclass  # type: ignore
# class ProjectLibrary(camina.Library):
#     """Stores classes instances and classes in a chained mapping.
    
#     When searching for matches, instances are prioritized over classes.
    
#     Args:
#         classes (camina.Catalog): a catalog of stored classes. Defaults to any 
#             empty Catalog.
#         instances (camina.Catalog): a catalog of stored class instances. Defaults 
#             to an empty Catalog.
                 
#     """
#     classes: camina.Catalog[str, Type[framework.Keystone]] = dataclasses.field(
#         default_factory = camina.Catalog)
#     instances: camina.Catalog[str, framework.Keystone] = dataclasses.field(
#         default_factory = camina.Catalog)

#     """ Properties """
    
#     @property
#     def plurals(self) -> tuple[str]:
#         """Returns all stored subclass names as naive plurals of those names.
        
#         Returns:
#             tuple[str]: all names with an 's' added in order to create simple 
#                 plurals combined with the stored keys.
                
#         """
#         suffixes = []
#         for catalog in ['classes', 'instances']:
#             plurals = [k + 's' for k in getattr(self, catalog).keys()]
#             suffixes.extend(plurals)
#         return tuple(suffixes)

 
# @dataclasses.dataclass  # type: ignore
# class ProjectRegistry(object):
#     """Stores classes and instances for a chrisjen project.
    
#     The registry facilitates flexibility and extensibility of the basic
#     defaults used in chrisjen. Users can design different project structures
#     while still taking advantage of chrisjen's accessibility and base classes.

#     Args:
#         keystones
#         managers
#         managers
#         nodes
#         subtypes
#         categories
        
#     """
#     keystones: ClassVar[camina.Catalog] = camina.Catalog()
#     managers: ClassVar[camina.Catalog] = camina.Catalog()
#     managers: ClassVar[camina.Catalog] = camina.Catalog()
#     nodes: ClassVar[ProjectLibrary] = ProjectLibrary()
#     subtypes: ClassVar[camina.Catalog] = camina.Catalog()
#     categories: ClassVar[MutableMapping[str, str]] = dataclasses.field(
#         default_factory = dict)
    
#     """ Public Methods """
    
#     @classmethod           
#     def classify(
#         cls, 
#         item: Union[framework.Keystone, Type[framework.Keystone]]) -> str:
#         """Returns name of kind that 'item' is an instance or subclass of.

#         Args:
#             item (Union[object, Type[Any]]): item to test for matching kind.

#         Raises:
#             TypeError: if no matching base kind is found.

#         Returns:
#             str: name of matching base kind.
            
#         """
#         if not inspect.isclass(item):
#             item = item.__class__
#         for name, subtype in cls.subtypes.items():
#             if issubclass(item, subtype):
#                 return name
#         raise TypeError(f'{item} does not match a known generic type')
   
#     @classmethod
#     def register(
#         cls, 
#         item: Union[framework.Keystone, Type[framework.Keystone]]) -> None:
#         """Registers 'item' in the appropriate class attributes.

#         Args:
#             item (Union[framework.Keystone, Type[framework.Keystone]]): item to
#                 test and register.
            
#         """
#         key = camina.namify(item = item)
#         # Removes 'project_' prefix if it exists.
#         if key.startswith('project_'):
#             key = key[8:]
#         if issubclass(item, Node):
#             cls.nodes.deposit(item = item, name = key)
#         if Node in item.__bases__:
#             cls.subtypes[key] = item
#         if framework.Keystone in item.__bases__:
#             cls.keystones[key] = item
#         if issubclass(item, Manager):
#             cls.managers[key] = item
#         if issubclass(item, Manager):
#             cls.managers[key] = item
#         kind = cls.classify(item = item)
#         cls.categories[key] = kind
#         return
