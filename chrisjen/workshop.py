"""
workshop: helper classes for projects
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
    Hashable, Iterable, Iterator, Mapping, MutableMapping, Sequence)
import copy
import dataclasses
import inspect
import itertools
import pathlib
import types
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases

if TYPE_CHECKING:
    from . import interface


def get_kinds(
    settings: amos.Settings, 
    name: Optional[str] = None,
    project: Optional[interface.Project] = None) -> dict[str, str]:
    """[summary]

    Args:
        section (Section): [description]

    Returns:
        dict[str, str]: [description]
    """
    if name is None and project is not None:
        kinds = {}
        suffixes = project.nodes.suffixes
        for key, section in settings.items():
            if any(k.endswith(suffixes) for k in section.keys()):
                new_kinds = get_section_kinds(section = settings[key])
                for inner_key, inner_value in new_kinds.items():
                    if inner_key in kinds:
                        kinds[inner_key].append(inner_value)
                    else:
                        kinds[inner_key] = inner_value  
        return kinds
    else:
        try:
            return get_section_kinds(section = settings[name])
        except KeyError:
            return get_kinds(settings = settings, name = None)

def get_section_kinds(section: MutableMapping[Hashable, Any]) -> dict[str, str]: 
    """
    """       
    kinds = {}
    for key in section.connections.keys():
        _, suffix = amos.cleave_str(key)
        values = amos.iterify(section[key])
        if suffix.endswith('s'):
            kind = suffix[:-1]
        else:
            kind = suffix            
        kinds.update(dict.fromkeys(values, kind))
    return kinds   

def get_connections(
    settings: amos.Settings, 
    name: Optional[str] = None,
    project: Optional[interface.Project] = None) -> dict[str, str]:
    """[summary]

    Args:
        section (Section): [description]

    Returns:
        dict[str, str]: [description]
    """
    if name is None and project is not None:
        connections = {}
        suffixes = project.nodes.suffixes
        for key, section in settings.items():
            if any(k.endswith(suffixes) for k in section.keys()):
                connections.update(
                    get_section_connections(section = settings[key]))
        return connections
    else:
        try:
            return get_section_connections(section = settings[name])
        except KeyError:
            return get_connections(settings = settings, name = None)
            
def get_section_connections(
    section: MutableMapping[Hashable, Any]) -> dict[str, list[str]]:
    """[summary]

    Args:
        section (MutableMapping[str, Any]): [description]
        suffixes (list[str]): [description]

    Returns:
        dict[str, list[str]]: [description]
    """    
    connections = {}
    keys = [k for k in section.keys() if k.endswith(section.suffixes)]
    for key in keys:
        prefix, suffix = amos.cleave_str(key)
        values = amos.iterify(section[key])
        if prefix == suffix:
            if prefix in connections:
                connections[section.name].extend(values)
            else:
                connections[section.name] = values
        else:
            if prefix in connections:
                connections[prefix].extend(values)
            else:
                connections[prefix] = values
    return connections

def get_designs(
    settings: amos.Settings, 
    name: Optional[str] = None,
    project: Optional[interface.Project] = None) -> dict[str, str]:
    """[summary]

    Args:
        section (Section): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    if name is None and project is not None:
        designs = {}
        suffixes = project.nodes.suffixes
        for key, section in settings.items():
            if any(k.endswith(suffixes) for k in section.keys()):
                designs.update(get_section_designs(section = settings[key]))
        return designs
    else:
        try:
            return get_section_designs(section = settings[name])
        except KeyError:
            return get_designs(settings = settings, name = None)
            
def get_section_designs(
    section: MutableMapping[Hashable, Any]) -> dict[str, str]:
    """[summary]

    Returns:
        dict[str, str]: [description]
        
    """
    designs = {}
    design_keys = [k for k in section.keys() if k.endswith('design')]
    for key in design_keys:
        prefix, suffix = amos.cleave_str(key)
        if prefix == suffix:
            designs[section.name] = section[key]
        else:
            designs[prefix] = section[key]
    return designs
      
      
@dataclasses.dataclass
class LibraryFactory(abc.ABC):
    """Mixin which registers subclasses, instances, and kinds.
    
    Args:
        library (ClassVar[ProjectLibrary]): project library of classes, 
            instances, and base classes. 
            
    """
    library: ClassVar[bases.ProjectLibrary] = dataclasses.field(
        default_factory = bases.ProjectLibrary)
    
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
        if abc.ABC in cls.__bases__:
            cls.library.bases[key] = cls
        else:
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
        # if isinstance(item, str):
        #     try:
        #         return cls.library[item](*args, **kwargs)
        #     except KeyError:
        #         pass
        # try:
        #     name = amos.get_name(item = item)
        #     return cls.library[name](item, *args, **kwargs)
        # except KeyError:
        #     for name, kind in cls.library.items():
        #         if (
        #             abc.ABC not in kind.__bases__ 
        #             and kind.__instancecheck__(instance = item)):
        #             method = getattr(cls, f'from_{name}')
        #             return method(item, *args, **kwargs)       
        #     raise ValueError(
        #         f'Could not create {cls.__name__} from item because it '
        #         f'is not one of these supported types: '
        #         f'{str(list(cls.library.keys()))}')
            