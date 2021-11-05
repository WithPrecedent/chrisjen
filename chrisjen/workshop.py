"""
workshop: helper classes and functions for projects
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

if TYPE_CHECKING:
    from . import interface
    from . import stages


def get_connections(project: interface.Project) -> dict[str, list[str]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """
    connections = {}
    for key, section in project.settings.items():
        if any(k.endswith(project.nodes.suffixes) for k in section.keys()):
            new_connections = get_section_connections(
                section = section,
                name = key,
                suffixes = project.nodes.suffixes)
            for inner_key, inner_value in new_connections.items():
                if inner_key in connections:
                    connections[inner_key].extend(inner_value)
                else:
                    connections[inner_key] = inner_value
    return connections

def get_designs(project: interface.Project) -> dict[str, str]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    designs = {}
    for key, section in project.settings.items():
        if any(k.endswith(project.nodes.suffixes) for k in section.keys()):
            new_designs = get_section_designs(section = section, name = key)
            designs.update(new_designs)
    return designs

def get_initialization(project: interface.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    initialization = {}
    for key, section in project.settings.items():   
        new_initialization = get_section_initialization(section = section)
        initialization[key] = new_initialization
    return initialization
                          
def get_kinds(project: interface.Project) -> dict[str, str]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    kinds = {}
    for key, section in project.settings.items():
        if any(k.endswith(project.nodes.suffixes) for k in section.keys()):
            new_kinds = get_section_kinds(
                section = section,
                suffixes = project.nodes.suffixes)
            kinds.update(new_kinds)  
    return kinds

def get_labels(project: interface.Project) -> list[str]:
    """Returns names of nodes based on 'project.settings'.

    Args:
        project (interface.Project): an instance of Project with 'settings' and
            'connections'.
        
    Returns:
        list[str]: names of all nodes that are listed in 'project.settings'.
        
    """        
    key_nodes = list(project.connections.keys())
    value_nodes = list(
        itertools.chain.from_iterable(project.connections.values()))
    return amos.deduplicate(item = key_nodes + value_nodes)     
      
def get_runtime(project: interface.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    runtime = {}
    for key, section in project.settings.items():
        if key.endswith('_parameters'):
            new_key = amos.drop_suffix(item = key, suffix = '_parameters')
            runtime[new_key] = section
    return runtime

def get_section_initialization(
    section: MutableMapping[Hashable, Any],
    suffixes: Sequence[str]) -> dict[str, Any]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, Any]: [description]
        
    """
    all_suffixes = suffixes + 'design'
    return {
        k: v for k, v in section.items() if not k.endswith(all_suffixes)}
    
def get_section_connections(
    section: MutableMapping[Hashable, Any],
    name: str,
    suffixes: Sequence[str]) -> dict[str, list[str]]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        name (str): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """    
    connections = {}
    keys = [k for k in section.keys() if k.endswith(suffixes)]
    for key in keys:
        prefix, suffix = amos.cleave_str(key)
        values = list(amos.iterify(section[key]))
        if prefix == suffix:
            if prefix in connections:
                connections[name].extend(values)
            else:
                connections[name] = values
        else:
            if prefix in connections:
                connections[prefix].extend(values)
            else:
                connections[prefix] = values
    return connections
      
def get_section_designs(
    section: MutableMapping[Hashable, Any],
    name: str) -> dict[str, str]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        name (str): [description]

    Returns:
        dict[str, str]: [description]
        
    """    
    designs = {}
    design_keys = [k for k in section.keys() if k.endswith('design')]
    for key in design_keys:
        prefix, suffix = amos.cleave_str(key)
        if prefix == suffix:
            designs[name] = section[key]
        else:
            designs[prefix] = section[key]
    return designs

def get_section_kinds(    
    section: MutableMapping[Hashable, Any],
    suffixes: Sequence[str]) -> dict[str, str]: 
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, str]: [description]
        
    """         
    kinds = {}
    keys = [k for k in section.keys() if k.endswith(suffixes)]
    for key in keys:
        _, suffix = amos.cleave_str(key)
        values = amos.iterify(section[key])
        if suffix.endswith('s'):
            kind = suffix[:-1]
        else:
            kind = suffix            
        kinds.update(dict.fromkeys(values, kind))
    return kinds   
