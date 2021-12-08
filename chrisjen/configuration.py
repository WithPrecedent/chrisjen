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
from collections.abc import Hashable, Mapping, MutableMapping
import dataclasses
import pathlib
from typing import Any, ClassVar, Optional, Type

import amos
    

_DESIGN_SUFFIX: str = 'design'
_FILES_SECTIONS: tuple[str, ...] = tuple(['clerk', 'filer', 'files'])
_GENERAL_SECTIONS: tuple[str, ...] = tuple(['general'])
_PARAMETERS_SUFFIX: str = 'parameters'
_PROJECT_SUFFIX: str = 'project'
_STRUCTURE_SUFFIX: str = 'structure'


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
    sources: ClassVar[Mapping[Type[Any], str]] = {
        MutableMapping: 'dictionary', 
        pathlib.Path: 'path',  
        str: 'path'}

    """ Properties """       

    @property
    def components(self) -> dict[str, dict[Hashable, Any]]:
        """[summary]

        Returns:
            dict[str, dict[Hashable, Any]]: [description]
            
        """
        names = _GENERAL_SECTIONS + _FILES_SECTIONS
        suffixes = tuple([_PARAMETERS_SUFFIX, _PROJECT_SUFFIX]) 
        component_sections = {}       
        for name, section in self.items():
            if name not in names and not name.endswith(suffixes):
                component_sections[name] = section
        return component_sections
       
    @property
    def filer(self) -> dict[Hashable, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[Hashable, Any]: [description]
            
        """  
        for name in _FILES_SECTIONS:
            try:
                return self[name]
            except KeyError:
                pass      
        raise KeyError(
            'ProjectSettings does not contain files-related configuration '
            'options')

    @property
    def general(self) -> dict[Hashable, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[Hashable, Any]: [description]
            
        """        
        for name in _GENERAL_SECTIONS:
            try:
                return self[name]
            except KeyError:
                pass  
        raise KeyError(
            'ProjectSettings does not contain general configuration options')

    @property
    def parameters(self) -> dict[str, dict[Hashable, Any]]:
        """[summary]

        Returns:
            dict[str, dict[Hashable, Any]]: [description]
            
        """
        parameter_sections = {}      
        for name, section in self.items():
            if name.endswith(_PARAMETERS_SUFFIX):
                parameter_sections[name] = section
        return parameter_sections
        
    @property
    def structure(self) -> dict[Hashable, Any]:
        """[summary]

        Raises:
            KeyError: [description]

        Returns:
            dict[Hashable, Any]: [description]
            
        """        
        for name, section in self.items():
            if name.endswith(_PROJECT_SUFFIX):
                return section
        raise KeyError(
            'ProjectSettings does not contain structure configuration options')
                                          