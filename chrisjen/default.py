"""
defaults: default settings for a chrisjen project
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
    Callable, Hashable, Mapping, MutableMapping, MutableSequence, Sequence, Set)
import dataclasses
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import base
 
    
FILER_SETTINGS: MutableMapping[str, Any] = {
    'file_encoding': 'windows-1252',
    'index_column': True,
    'include_header': True,
    'conserve_memory': False,
    'test_size': 1000,
    'threads': -1,
    'visual_tightness': 'tight', 
    'visual_format': 'png'}

SETTINGS_SUFFIXES: MutableMapping[str, tuple[str]] = {
    'design': ('design',),
    'files': ('clerk', 'filer', 'files'),
    'general': ('general',),
    'parameters': ('parameters',),
    'project': ('project',),
    'structure': ('structure',)}

STRUCTURE: Structure = base.Structure()


    
def set_structure(item: Structure) -> None:
    """Sets default STRUCTURE variable to 'item' if 'item' is a Structure type.

    Args:
        item (Structure): value to set STRUCTURE to.

    Raises:
        TypeError: if 'item is not a Structure type.
        
    """
    if isinstance(item, Structure):
        STRUCTURE = item
    else:
        raise TypeError('item must be a Structure type')
    