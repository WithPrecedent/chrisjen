"""
views: classes and functions related to stages of a chrisjen project
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
    Workflow
    Results
    create_workflow
    create_results

To Do:

        
"""
from __future__ import annotations
from collections.abc import Mapping, MutableMapping
import dataclasses
import itertools
import pathlib
from typing import Any, ClassVar, Type, Union

import amos
import bobbie

from . import base


@dataclasses.dataclass
class Configuration(bobbie.Settings, base.Keystone):
    """Loads and stores project configuration settings.

    Args:
        contents (MutableMapping[str, Any]): a dict for storing configuration 
            options. Defaults to en empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.
        sources (ClassVar[Mapping[Type[Any], str]]): keys are types for sources 
            for creating an instance and values are the suffix for the 
            classmethod to be called using the matching key type.
        suffixes (ClassVar[dict[str, tuple[str]]]): keys are the type of data
            that is contained in the section and values are the str names of
            suffixes (or complete matches) of sections that are relevant to the
            str key type. Defaults to dict with data in dataclasses field.

    """
    contents: MutableMapping[str, Any] = dataclasses.field(
        default_factory = dict)
    default: Mapping[str, Any] = dataclasses.field(
        default_factory = dict)
    infer_types: bool = True
    sources: ClassVar[Mapping[Type[Any], str]] = {
        MutableMapping: 'dictionary', 
        pathlib.Path: 'path',  
        str: 'path'}
    suffixes: ClassVar[dict[str, tuple[str]]] = base.Structure.suffixes
    
    """ Properties """       
                                  
    @property
    def components(self) -> dict[str, str]:
        """Returns component-related sections of chrisjen project settings.
        
        Any section that does not have a special suffix in 'suffixes' is deemed
        to be a component-related section.

        Returns:
            dict[str, dict[str, Any]]: component-related sections of settings.
            
        """
        return get_component_settings(settings = self)
                       
    @property
    def director(self) -> dict[str, Any]:
        """Returns director settings of a chrisjen project.

        Returns:
            dict[str, Any]: director settings for a chrisjen project
            
        """
        return get_director_settings(settings = self)
               
    @property
    def filer(self) -> dict[str, Any]:
        """Returns file settings in a chrisjen project.

        Returns:
            dict[str, Any]: dict of file settings.
            
        """
        return get_file_settings(settings = self)

    @property
    def general(self) -> dict[str, Any]:
        """Returns general settings in a chrisjen project.

        Returns:
            dict[str, Any]: dict of general settings.
            
        """       
        return get_general_settings(settings = self)

    
@dataclasses.dataclass
class Outline(base.Keystone):
    """Provides a different view of data stored in 'project.settings'.
    
    The properties in Outline are used in the construction of a Workflow. So,
    even if you do not have any interest in using its view of the configuration
    settings, it shouldn't be cut out of a Project (unless you also replace the
    functions for creating a Workflow). 

    Args:
        project (base.Project): a related project instance which has data
            from which the properties of an Outline can be derived.

    """
    project: base.Project

    """ Properties """       

    @property
    def connections(self) -> dict[str, dict[str, list[str]]]:
        """Returns raw connections between nodes from 'project'.
        
        Returns:
            dict[str, dict[str, list[str]]]: keys are worker names and values 
                node connections for that worker.
            
        """
        return get_connection_settings(project = self.project)
                     
    @property
    def designs(self) -> dict[str, str]:
        """Returns designs of nodes in a chrisjen project.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        return get_design_settings(project = self.project)
                                    
    @property
    def implementation(self) -> dict[str, dict[str, Any]]:
        """Returns implementation parameters for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the implementation arguments and attributes.
            
        """
        return get_implementation_settings(project = self.project)
                                                             
    @property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        return get_initialization_settings(project = self.project)
        
    @property
    def kinds(self) -> dict[str, str]:
        """Returns kinds of ndoes in 'project'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        return get_kinds_settings(project = self.project)
    
    @property
    def labels(self) -> list[str]:
        """Returns names of nodes in 'project'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        return get_label_settings(project = self.project)
    
    @property
    def managers(self) -> list[str]:
        """Returns names of nodes in 'project'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        return get_manager_settings(project = self.project)       
  
    
""" Public Functions """

def get_component_settings(
    settings: Configuration) -> dict[str, dict[str, Any]]:
    """Returns component-related sections of chrisjen project settings.
    
    Any section that does not have a special suffix in 'suffixes' is deemed
    to be a component-related section.
    
    Args:
        settings (Configuration): settings from which to derive information.

    Returns:
        dict[str, dict[str, Any]]: component-related sections of settings.
        
    """
    special_suffixes = itertools.chain_from_iterable(settings.suffixes.values())
    component_sections = {}       
    for name, section in settings.items():
        if not name.endswith(special_suffixes):
            component_sections[name] = section
    return component_sections
      
def get_connection_settings(
    project: base.Project) -> dict[str, dict[str, list[str]]]:
    """Returns raw connections between nodes from 'project'.
    
    Args:
        project (base.Project): instance from which to derive information.
    
    Returns:
        dict[str, dict[str, list[str]]]: keys are worker names and values are 
            node connections for that worker.
        
    """
    suffixes = project.options.plurals
    connections = {}
    for name, section in project.settings.components.items():
        new_connections = {}
        keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in keys:
            prefix, suffix = amos.cleave_str(key)
            values = list(amos.iterify(section[key]))
            if prefix == suffix:
                if prefix in new_connections:
                    new_connections[name].extend(values)
                else:
                    new_connections[name] = values
            else:
                if prefix in new_connections:
                    new_connections[prefix].extend(values)
                else:
                    new_connections[prefix] = values
        for inner_key, inner_value in new_connections.items():
            if inner_key in connections[key]:
                connections[key][inner_key].extend(inner_value)
            else:
                connections[key][inner_key] = inner_value
    return connections
     
def get_design_settings(project: base.Project) -> dict[str, str]:
    """Returns designs of nodes in a chrisjen project.
    
    Args:
        project (base.Project): project from which to derive information.

    Returns:
        dict[str, str]: keys are node names and values are design names.
        
    """
    designs = {}
    for key, section in project.settings.components.items():
        new_designs = {}
        design_keys = [
            k for k in section.keys() 
            if k.endswith(project.settings.suffixes['design'])]
        for key in design_keys:
            prefix, suffix = amos.cleave_str(key)
            if prefix == suffix:
                new_designs[key] = section[key]
            else:
                new_designs[prefix] = section[key]
        designs.update(new_designs)
    return designs

def get_director_settings(settings: Configuration) -> dict[str, Any]:
    """Returns director settings of a chrisjen project.
    
    Args:
        settings (Configuration): settings from which to derive information.

    Returns:
        dict[str, Any]: director settings for a chrisjen project
        
    """
    director = {}
    for name, section in settings.items():
        if name.endswith(settings.suffixes['director']):
            director = section
            break
    return director

def get_file_settings(settings: Configuration) -> dict[str, Any]:
    """Returns file settings in a chrisjen project.
    
    Args:
        settings (Configuration): settings from which to derive information.

    Returns:
        dict[str, Any]: dict of file settings.
        
    """
    for name in settings.suffixes['files']:
        try:
            return settings[name]
        except KeyError:
            return {}      
            
def get_general_settings(settings: Configuration) -> dict[str, Any]:
    """Returns general settings in a chrisjen project.
    
    Args:
        settings (Configuration): settings from which to derive information.

    Returns:
        dict[str, Any]: dict of general settings.
        
    """
    for name in settings.suffixes['general']:
        try:
            return settings[name]
        except KeyError:
            return {}  
     
def get_implementation_settings(
    project: base.Project) -> dict[str, dict[str, Any]]:
    """Returns implementation parameters for nodes.
    
    These values will be parsed into arguments and attributes once the nodes
    are instanced.
    
    Args:
        project (base.Project): project from which to derive information.

    Returns:
        dict[str, dict[str, Any]]: keys are node names and values are dicts
            of the implementation arguments and attributes.
        
    """
    implementation = {}      
    for name, section in project.settings.items():
        for suffix in project.settings.suffixes['parameters']:
            if name.endswith(suffix):
                key = name.removesuffix('_' + suffix)
                implementation[key] = section
    return implementation
   
def get_initialization_settings(
    project: base.Project) -> dict[str, dict[str, Any]]:
    """Returns initialization arguments and attributes for nodes.
    
    These values will be parsed into arguments and attributes once the nodes
    are instanced. They are derived from 'settings'.
    
    Args:
        project (base.Project): instance from which to derive information.

    Returns:
        dict[str, dict[str, Any]]: keys are node names and values are dicts
            of the initialization arguments and attributes.
        
    """
    initialization = {}
    for key, section in project.settings.components.items():   
        all_plurals = (
            project.options.plurals 
            + project.settings.suffixes['design']
            + project.settings.suffixes['director'])
        initialization[key] = {
            k: v for k, v in section.items() if not k.endswith(all_plurals)}
    return initialization
                     
def get_kinds_settings(project: base.Project) -> dict[str, str]:
    """Returns kinds of nodes in 'project'.
    
    Args:
        project (base.Project): instance from which to derive information.

    Returns:
        dict[str, str]: keys are names of nodes and values are names of the
            associated base kind types.
        
    """
    kinds = {}
    suffixes = project.options.plurals
    for key, section in project.settings.components.items():
        new_kinds = {}
        keys = [k for k in section.keys() if k.endswith(suffixes)]
        for key in keys:
            _, suffix = amos.cleave_str(key)
            values = list(amos.iterify(section[key]))
            if values not in [['none'], ['None'], ['NONE']]:
                if suffix.endswith('s'):
                    kind = suffix[:-1]
                else:
                    kind = suffix            
                new_kinds.update(dict.fromkeys(values, kind))
        kinds.update(new_kinds)  
    return kinds

def get_label_settings(project: base.Project) -> list[str]:
    """Returns names of nodes in 'project'.
    
    Args:
        project (base.Project): instance from which to derive information.

    Returns:
        list[str]: names of all nodes that are listed in 'settings'.
        
    """
    labels = []    
    for key, section in project.outline.connections.items():
        labels.append(key)
        for inner_key, inner_values in section.items():
            labels.append(inner_key)
            labels.extend(list(itertools.chain(inner_values)))
    return amos.deduplicate_list(item = labels)    
     
def get_manager_settings(project: base.Project) -> list[str]:
    """Returns manager names for a chrisjen project.
    
    Args:
        project (base.Project): project from which to derive information.

    Returns:
        list[str]: names of managers.
        
    """
    managers = []
    for _, section in project.settings.items():
        manager_keys = [
            k for k in section.keys() 
            if k.endswith(project.settings.suffixes['manager'])]
        for inner_key in manager_keys:
            managers.extend(amos.listify(section[inner_key]))  
    return managers

# def infer_project_name(project: base.Project) -> Optional[str]:
#     """Tries to infer project name from settings contents.
    
#     Args:
#         project (base.Project): an instance of Project with 'settings'.
        
#     Returns:
#         Optional[str]: project name or None, if none is found.
                
#     """
#     suffixes = project.options.plurals
#     name = None    
#     for key, section in project.settings.items():
#         if (
#             key not in ['general', 'files', 'filer', 'filer'] 
#                 and any(k.endswith(suffixes) for k in section.keys())):
#             name = key
#             break
#     return name
