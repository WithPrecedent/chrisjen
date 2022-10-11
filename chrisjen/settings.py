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
    Configuration (amos.Settings, base.ProjectBase):
    get_component_settings
    get_design_settings
    get_filer_settings
    get_general_settings
    get_implementation_settings
    get_structure_settings
    

To Do:
    Add support for enviornment settings that change dotenv settings.
            
"""
from __future__ import annotations

from collections.abc import Hashable, Mapping, MutableMapping
import dataclasses
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

import amos
import bobbie

from . import base
    

 
    # """ Public Methods """
    
    # @classmethod
    # def validate(cls, project: interface.Project) -> interface.Project:
    #     """Creates or validates 'project.settings'.

    #     Args:
    #         project (Project): an instance with a 'settings' 
    #             attribute.

    #     Returns:
    #         Project: an instance with a validated 'settings'
    #             attribute.
            
    #     """        
    #     if inspect.isclass(project.settings):
    #         project.settings = project.settings()
    #     elif project.settings is None:
    #         project.settings = cls.create(
    #             item = project.settings,
    #             project = project)
    #     return project 

""" Public Methods """