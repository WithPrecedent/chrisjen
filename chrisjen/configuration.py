"""
configuration: easy, flexible system for project configuration
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
    ProjectSettings (amos.Settings): stores configuration settings after either 
        loading them from disk or by the passed arguments.

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import dataclasses
import functools
import importlib.util
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

if TYPE_CHECKING:
    from . import interface
    

@dataclasses.dataclass
class ProjectSettings(amos.Settings):
    """Loads and stores configuration settings.

    Args:
        contents (MutableMapping[Hashable, Any]): a dict for storing 
            configuration options. Defaults to en empty dict.
        default_factory (Optional[Any]): default value to return when the 'get' 
            method is used. Defaults to an empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.
        project (interface.Project): a related project instance which has data
            that the properties can be derived.

    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = dict
    default: Mapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    project: interface.Project = None
    sources: ClassVar[Mapping[Type[Any], str]] = {
        MutableMapping: 'dictionary', 
        pathlib.Path: 'path',  
        str: 'path'}

    """ Properties """       
    
    @functools.cached_property
    def connections(self) -> dict[str, list[str]]:
        """Returns raw connections between nodes from 'settings'.

        Returns:
            dict[str, list[str]]: keys are node names and values are lists of
                nodes to which the key node is connection. These connections
                do not include any structure or design.
            
        """
        return get_connections(project = self.project)

    @functools.cached_property
    def designs(self) -> dict[str, str]:
        """Returns structural designs of nodes based on 'settings'.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        return get_designs(project = self.project)

    @functools.cached_property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        return get_initialization(project = self.project)
        
    @functools.cached_property
    def kinds(self) -> dict[str, str]:
        """Returns kinds based on 'settings'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        return get_kinds(project = self.project)
    
    @functools.cached_property
    def labels(self) -> list[str]:
        """Returns names of nodes based on 'settings'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        return get_labels(project = self.project)

    @functools.cached_property
    def runtime(self) -> dict[str, dict[str, Any]]:
        """Returns runtime parameters based on 'settings'

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of runtime parameters.
            
        """
        return get_runtime(project = self.project)    


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
            new_connections = _get_section_connections(
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
            new_designs = _get_section_designs(section = section, name = key)
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
        new_initialization = _get_section_initialization(
            section = section,
            suffixes = project.nodes.suffixes)
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
            new_kinds = _get_section_kinds(
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
    key_nodes = list(project.settings.connections.keys())
    value_nodes = list(
        itertools.chain.from_iterable(project.settings.connections.values()))
    all_nodes = key_nodes + value_nodes
    return amos.deduplicate_list(item = all_nodes)     
      
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
            new_key = amos.drop_suffix_from_str(
                item = key, 
                suffix = '_parameters')
            runtime[new_key] = section
    return runtime

def _get_section_initialization(
    section: MutableMapping[Hashable, Any],
    suffixes: Sequence[str]) -> dict[str, Any]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, Any]: [description]
        
    """
    all_suffixes = suffixes + ('design',)
    return {
        k: v for k, v in section.items() if not k.endswith(all_suffixes)}
    
def _get_section_connections(
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
      
def _get_section_designs(
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

def _get_section_kinds(    
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
