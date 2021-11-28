"""
tasks: primitive task nodes for chrisjen workflows
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
    Step
    Technique
    
"""
from __future__ import annotations
from collections.abc import Callable, Hashable, MutableMapping
import dataclasses
from typing import Any, Optional, TYPE_CHECKING, Union

from . import bases
from . import components

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass   
class Contest(components.Judge):
    """Primitive node for single task execution.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                                                 
    """
    """Reduces paths by selecting the best path based on a criteria score."""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)


   
@dataclasses.dataclass   
class Survey(components.Judge):
    """Primitive node for single task execution.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                                                 
    """
    """Reduces paths by averaging the results of a criteria score."""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)


@dataclasses.dataclass   
class Validation(components.Judge):
    """Primitive node for single task execution.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                                                 
    """
    """Reduces paths based on each test meeting a minimum criteria score."""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)


@dataclasses.dataclass
class Step(components.Task):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when creating branching, parallel workflows which test a variety of 
    strategies with similar or identical parameters and/or methods.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                                                 
    """
    name: Optional[str] = None
    contents: Optional[Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
                    
    """ Properties """
    
    @property
    def technique(self) -> Optional[Technique]:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def execute(self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method of 'contents'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if hasattr(self.parameters, 'finalize'):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if self.technique.parameters:
                if hasattr(self.technique.parameters, 'finalize'):
                    self.technique.parameters.finalize(project = project)
                technique_parameters = self.technique.parameters
                parameters.update(technique_parameters)  
            self.technique.implement(project = project, **parameters)
        return project
        
                                                  
@dataclasses.dataclass
class Technique(components.Task):
    """Primitive node for single task execution.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                                                 
    """
    name: Optional[str] = None
    contents: Optional[Callable[..., Optional[Any]]] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    step: Optional[Union[str, Step]] = None
        
    """ Properties """
    
    @property
    def algorithm(self) -> Optional[Callable[..., Optional[Any]]]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Callable[..., Optional[Any]]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self


