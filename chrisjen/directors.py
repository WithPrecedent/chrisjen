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

from . import options
from . import validate

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass
class Director(Iterator):
    """Iterator for chrisjen Project instances.
    
    
    """
    project: interface.Project = None
    options: types.ModuleType = options
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets index for iteration.
        self.index = 0
        # Validate stages
        self._validate_stages()
        
    """ Properties """
    
    @property
    def current(self) -> str:
        return list(self.stages.keys())[self.index]
    
    @property
    def previous(self) -> str:
        try:
            return list(self.stages.keys())[self.index -1]
        except IndexError:
            return None
          
    @property
    def stages(self) -> (
        Sequence[Union[str, Type[options.STAGE], options.STAGE]]):
        return self.project.stages
    
    @property
    def subsequent(self) -> str:
        try:
            return list(self.stages.keys())[self.index + 1]
        except IndexError:
            return None
    
    @property
    def clerk(self) -> Type[Any]:
        """Returns base class for a filing clerk.

        Returns:
            Type[Any]: appropriate base class.
        
        """
        return self.options.CLERK
    
    @clerk.setter
    def clerk(self, value: Type[Any]) -> None:
        """Sets the base class for a filing clerk.

        Args:
            value (Type[Any]): an chrisjen-compatible base class.

        Raises:
            ValueError: if 'value' is not compatible with chrisjen.
            
        """
        if validate.is_clerk(item = value):
            self.options.CLERK = value
        else:
            raise ValueError(f'{__name__} is not compatiable with chrisjen')
    
    @property
    def library(self) -> Type[Any]:
        """Returns base class for a project library.

        Returns:
            Type[Any]: appropriate base class.
        
        """
        return self.options.CONVERTERS
    
    @converters.setter
    def converters(self, value: Type[Any]) -> None:
        """Sets the base class for a filing clerk.

        Args:
            value (Type[Any]): an chrisjen-compatible base class.

        Raises:
            ValueError: if 'value' is not compatible with chrisjen.
            
        """
        if validate.is_clerk(item = value):
            self.options.CLERK = value
        else:
            raise ValueError(f'{__name__} is not compatiable with chrisjen')
           
    CONVERTERS: types.ModuleType = stages
    DIRECTOR: Type[Any] = workshop.Director
    LIBRARY: Type[Any] = nodes.ProjectLibrary
    NODE: Type[Any] = nodes.Component
    PARAMETERS: Type[Any] = nodes.Parameters
    SETTINGS: Type[Any] = workshop.ProjectSettings
    STAGE: Type[Any] = stages.Stage
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for stage in self.stages:
            self.advance()
        return self    

    def get_base(self, base_type: str) -> None:
        return getattr(self.options, base_type.upper())

    def set_base(self, base_type: str, base: Type[Any]) -> None:
        setattr(self.options, base_type, base)
        return
    
    """ Private Methods """
    
    def _validate_stages(self) -> None:
        new_stages = []
        for stage in self.project.stages:
            new_stages.append(self._validate_stage(stage = stage))
        self.project.stages = new_stages
        return

    def _validate_stage(self, stage: Any) -> object:
        if isinstance(stage, str):
            try:
                stage = options.STAGE.create(stage)
            except KeyError:
                raise KeyError(f'{stage} was not found in Stage registry')
        if inspect.isclass(stage):
            stage = stage()
        return stage
            
        
    """ Dunder Methods """
    
    def __iter__(self) -> Iterable:
        """Returns iterable of 'stages'.
        
        Returns:
            Iterable: of 'stages'.
            
        """
        return self
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index < len(self.stages):
            source = self.previous or 'settings'
            product = self.stages[self.current]
            converter = getattr(self.converters, f'create_{product}')
            if self.project.settings['general']['verbose']:
                print(f'Creating {product} from {source}')
            kwargs = {'project': self.project}
            setattr(self.project, product, converter(**kwargs))
            self.index += 1
            if self.project.settings['general']['verbose']:
                print(f'Completed {product}')
        else:
            raise StopIteration
        return self

