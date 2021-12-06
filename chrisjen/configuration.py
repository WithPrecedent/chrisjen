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
    ProjectSettings (amos.Settings): stores configuration settings from a file,
        passed arguments, or manual user addition. 

ToDo:
       
       
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping, Sequence
import dataclasses
import functools
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

if TYPE_CHECKING:
    from . import interface
    

_DESIGN_SUFFIXES: tuple[str, ...] = tuple(['design'])
_FILES_SECTIONS: tuple[str, ...] = tuple(['clerk', 'filer', 'files'])
_GENERAL_SECTIONS: tuple[str, ...] = tuple(['general'])
_PARAMETERS_SUFFIXES: tuple[str, ...] = tuple(['_parameters'])


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
            from which the properties of ProjectSettings can be derived.
        sources (ClassVar[Mapping[Type[Any], str]]): keys are types for sources 
            for creating an instance and values are the suffix for the 
            classmethod to be called using the matching key type.

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
        try:
            return get_connections(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')
            
    @functools.cached_property
    def designs(self) -> dict[str, str]:
        """Returns structural designs of nodes of 'contents'.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        try:
            return get_designs(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')

    @property
    def files(self) -> MutableMapping[Hashable, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            MutableMapping[Hashable, Any]: [description]
            
        """  
        for name in _FILES_SECTIONS:
            try:
                return self[name]
            except KeyError:
                pass      
        raise KeyError(
            'ProjectSettings does not contain files-related '
            'configuration options')

    @property
    def general(self) -> MutableMapping[Hashable, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            MutableMapping[Hashable, Any]: [description]
            
        """        
        for name in _GENERAL_SECTIONS:
            try:
                return self[name]
            except KeyError:
                pass  
        raise KeyError(
            'ProjectSettings does not contain general configuration '
            'options')
                                        
    @functools.cached_property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        try:
            return get_initialization(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')
        
    @functools.cached_property
    def kinds(self) -> dict[str, str]:
        """Returns kinds of ndoes in 'contents'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        try:
            return get_kinds(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')
    
    @functools.cached_property
    def labels(self) -> list[str]:
        """Returns names of nodes of 'contents'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        try:
            return get_labels(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')

    @functools.cached_property
    def runtime(self) -> dict[str, dict[str, Any]]:
        """Returns runtime parameters of 'contents'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of runtime parameters.
            
        """
        try:
            return get_runtime(project = self.project)    
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')

    @functools.cached_property
    def workers(self) -> dict[str, dict[Hashable, Any]]:
        """Returns sections in 'contents' that are for workers.

        Returns:
            dict[str, dict[Hashable, Any]]: keys are the names of worker 
                sections and values are those sections.
            
        """
        try:            
            return get_workers(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')
        
""" Public Functions """

def get_connections(project: interface.Project) -> dict[str, list[str]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """
    suffixes = project.options.plurals
    connections = {}
    for key, section in project.settings.workers.items():
        new_connections = _get_section_connections(
            section = section,
            name = key,
            plurals = suffixes)
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
    for key, section in project.settings.workers.items():
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
            plurals = project.options.plurals)
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
        if any(k.endswith(project.options.plurals) for k in section.keys()):
            new_kinds = _get_section_kinds(
                section = section,
                plurals = project.options.plurals)
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
        if key.endswith(_PARAMETERS_SUFFIXES):
            new_key = amos.drop_suffix_from_str(
                item = key, 
                suffix = _PARAMETERS_SUFFIXES)
            runtime[new_key] = section
    return runtime
   
def get_workers(project: interface.Project) -> dict[str, dict[Hashable, Any]]: 
    """Returns names of sections containing data for worker creation.

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[Hashable, Any]]: [description]
        
    """
    suffixes = project.options.plurals
    return {
        k: v for k, v in project.settings.items() 
        if is_worker_section(section = v, suffixes = suffixes)}

def is_worker_section(
    section: MutableMapping[Hashable, Any], 
    suffixes: tuple[str, ...]) -> bool:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (tuple[str, ...]): [description]

    Returns:
        bool: [description]
        
    """ 
    return any(
        is_connections(key = k, suffixes = suffixes) for k in section.keys())

def is_connections(key: str, suffixes: tuple[str, ...]) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (tuple[str, ...]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith(suffixes)

def is_design(key: str) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (list[str]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith(_DESIGN_SUFFIXES)

def is_parameters(key: str) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (list[str]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith(_PARAMETERS_SUFFIXES)

""" Private Functions """   
 
def _get_section_connections(
    section: MutableMapping[Hashable, Any],
    name: str,
    plurals: Sequence[str]) -> dict[str, list[str]]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        name (str): [description]
        plurals (Sequence[str]): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """    
    connections = {}
    keys = [
        k for k in section.keys() 
        if is_connections(key = k, suffixes = plurals)]
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
      
def _get_section_initialization(
    section: MutableMapping[Hashable, Any],
    plurals: Sequence[str]) -> dict[str, Any]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        plurals (Sequence[str]): [description]

    Returns:
        dict[str, Any]: [description]
        
    """
    all_plurals = plurals + _DESIGN_SUFFIXES
    return {
        k: v for k, v in section.items() if not k.endswith(all_plurals)}

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
    design_keys = [k for k in section.keys() if k.endswith(_DESIGN_SUFFIXES)]
    for key in design_keys:
        prefix, suffix = amos.cleave_str(key)
        if prefix == suffix:
            designs[name] = section[key]
        else:
            designs[prefix] = section[key]
    return designs

def _get_section_kinds(    
    section: MutableMapping[Hashable, Any],
    plurals: Sequence[str]) -> dict[str, str]: 
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        plurals (Sequence[str]): [description]

    Returns:
        dict[str, str]: [description]
        
    """         
    kinds = {}
    keys = [k for k in section.keys() if k.endswith(plurals)]
    for key in keys:
        _, suffix = amos.cleave_str(key)
        values = amos.iterify(section[key])
        if suffix.endswith('s'):
            kind = suffix[:-1]
        else:
            kind = suffix            
        kinds.update(dict.fromkeys(values, kind))
    return kinds  

def infer_project_name(project: interface.Project) -> Optional[str]:
    """Tries to infer project name from settings contents.
    
    Args:
        project (interface.Project): an instance of Project with 'settings'.
        
    Returns:
        Optional[str]: project name or None, if none is found.
                
    """
    suffixes = project.options.plurals
    name = None    
    for key, section in project.settings.items():
        if (
            key not in ['general', 'files', 'filer', 'clerk'] 
                and any(k.endswith(suffixes) for k in section.keys())):
            name = key
            break
    return name
