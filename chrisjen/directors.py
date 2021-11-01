"""
directors: helper classes for projects
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
import dataclasses
import inspect
import types
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

from . import bases
from . import validate

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass
class OutlineWorkflowResults(Director):
    """Project Director for an Outline, Workflow, Results process.
    
    
    """
    project: interface.Project = None
    options: types.ModuleType = bases

    """ Properties """
        
    @property
    def clerk(self) -> Type[Any]:
        """Returns base class for a filing clerk.

        Returns:
            Type[Any]: appropriate base class.
        
        """
        return self.bases.CLERK
    
    @clerk.setter
    def clerk(self, value: Type[Any]) -> None:
        """Sets the base class for a filing clerk.

        Args:
            value (Type[Any]): a chrisjen-compatible base class.

        Raises:
            ValueError: if 'value' is not compatible with chrisjen.
            
        """
        if validate.is_clerk(item = value):
            self.bases.CLERK = value
        else:
            raise ValueError(f'{__name__} is not compatiable with chrisjen')
    
    @property
    def library(self) -> Type[Any]:
        """Returns base class for a project library.

        Returns:
            Type[Any]: appropriate base class.
        
        """
        return self.bases.CONVERTERS
    
    @library.setter
    def converters(self, value: Type[Any]) -> None:
        """Sets the base class for a filing clerk.

        Args:
            value (Type[Any]): a chrisjen-compatible base class.

        Raises:
            ValueError: if 'value' is not compatible with chrisjen.
            
        """
        if validate.is_clerk(item = value):
            self.bases.CLERK = value
        else:
            raise ValueError(f'{__name__} is not compatiable with chrisjen')
           
    CONVERTERS: types.ModuleType = stages
    DIRECTOR: Type[Any] = workshop.Director
    LIBRARY: Type[Any] = nodes.ProjectLibrary
    NODE: Type[Any] = nodes.Component
    PARAMETERS: Type[Any] = nodes.Parameters
    SETTINGS: Type[Any] = workshop.ProjectSettings
    STAGE: Type[Any] = stages.Stage