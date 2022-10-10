"""
settings: stores configuration settings for a chrisjen project
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

from collections.abc import Mapping, MutableMapping
import dataclasses
import inspect
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

import bobbie

from . import base

if TYPE_CHECKING:
    from . import interface
    

@dataclasses.dataclass
class Configuration(bobbie.Settings, base.ProjectBase):
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
    suffixes: ClassVar[dict[str, tuple[str]]] = base.CONFIGURATION_SUFFIXES
    
    """ Properties """       

    @property
    def components(self) -> dict[str, dict[str, Any]]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        special_suffixes = itertools.chain_from_iterable(self.suffixes.values())
        component_sections = {}       
        for name, section in self.items():
            if not name.endswith(special_suffixes):
                component_sections[name] = section
        return component_sections
       
    @property
    def filer(self) -> dict[str, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[str, Any]: [description]
            
        """  
        for name in self.suffixes['files']:
            try:
                return self[name]
            except KeyError:
                pass      
        raise KeyError(
            'Configuration does not contain files-related configuration '
            'options')

    @property
    def general(self) -> dict[str, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[str, Any]: [description]
            
        """        
        for name in self.suffixes['general']:
            try:
                return self[name]
            except KeyError:
                pass  
        raise KeyError(
            'Configuration does not contain general configuration options')

    @property
    def parameters(self) -> dict[str, dict[str, Any]]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        parameter_sections = {}      
        for name, section in self.items():
            if name.endswith(self.suffixes['parameters']):
                parameter_sections[name] = section
        return parameter_sections
        
    @property
    def structure(self) -> dict[str, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[str, Any]: [description]
            
        """        
        for name, section in self.items():
            if name.endswith(self.suffixes['structure']):
                return section
        raise KeyError(
            'Configuration does not contain structure configuration options')

    """ Public Methods """
    
    @classmethod
    def validate(cls, project: interface.Project) -> interface.Project:
        """Creates or validates 'project.settings'.

        Args:
            project (Project): an instance with a 'settings' 
                attribute.

        Returns:
            Project: an instance with a validated 'settings'
                attribute.
            
        """        
        if inspect.isclass(project.settings):
            project.settings = project.settings()
        elif project.settings is None:
            project.settings = cls.create(
                item = project.settings,
                project = project)
        return project 
 