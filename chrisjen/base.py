"""
base: base classes for a chrisjen project
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
    Make Component a subclass of amos.Node by fixing the proxy access methods
        that currently return errors.
            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, Sequence, Set)
import copy
import dataclasses
import functools
import inspect
import itertools
import multiprocessing
import pathlib
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union
import warnings

import amos
import bobbie
import holden
import miller
import nagata

from . import workshop

if TYPE_CHECKING:
    from . import filing
    from . import workshop
 
   
FILER_SETTINGS: MutableMapping[str, Any] = {
    'file_encoding': 'windows-1252',
    'conserve_memory': False,
    'threads': -1}

CONFIGURATION_SUFFIXES: MutableMapping[str, tuple[str]] = {
    'design': ('design',),
    'files': ('filer', 'files'),
    'general': ('general',),
    'parameters': ('parameters',),
    'project': ('project',),
    'structure': ('structure',)}
 
""" 
Project Base Registry

Key names are str names of a subclass (snake_case by default) and values are the 
subclasses. Defaults to an empty dict.  

""" 
PROJECT_BASES: MutableMapping[str, Type[ProjectBase]] = {}


@dataclasses.dataclass
class ProjectBase(amos.Registrar, Protocol):
    """Mixin for all project base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because Registrar will often be used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        if ProjectBase in cls.__bases__:
            key = amos.namify(item = cls)
            PROJECT_BASES[key] = cls
        
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(cls, *args, **kwargs):
        pass
      
