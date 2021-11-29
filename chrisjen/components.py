"""
components: core node types for project workflows
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
    Worker
    Manager
    Task
    Judge
    Step 
    Technique
    
"""
from __future__ import annotations
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, MutableSequence, Sequence)
import dataclasses
import multiprocessing
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass
class Worker(bases.Component, amos.Pipeline):
    """Iterable component of a chrisjen workflow.

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
        registry (ClassVar[MutableMapping[str, Type[Any]]]): key names are str
            names of a subclass (snake_case by default) and values are the 
            subclasses. Defaults to an empty dict.  
                              
    """
    name: Optional[str] = None
    contents: MutableSequence[bases.Component] = dataclasses.field(
        default_factory = list)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)

    """ Public Methods """  
    
    def execute(self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        if self.contents not in [None, 'None', 'none']:
            self.finalize(project = project, **kwargs)
            project = self.implement(project = project, **self.parameters)
        return project
           
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)  

    """ Private Methods """
    
    def _implement_in_serial(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        for node in self.contents:
            project = node.execute(project = project, **kwargs)
        return project  
    
    
@dataclasses.dataclass
class Manager(Worker, amos.Pipelines):
    """Base class for branching and parallel Workers.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (MutableMapping[Hashable, Worker]): keys are the name or 
            other identifier for the stored Worker instances and values are 
            Worker instances. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a bases.Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        registry (ClassVar[MutableMapping[str, Type[Any]]]): key names are str
            names of a subclass (snake_case by default) and values are the 
            subclasses. Defaults to an empty dict.  
                          
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Worker] = dataclasses.field(
        default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    critera: Union[Callable, str] = None
              
    """ Public Methods """ 
           
    def implement(
        self,
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        if len(self.contents) > 1 and project.settings.general['parallelize']:
            project = self._implement_in_parallel(project = project, **kwargs)
        else:
            project = self._implement_in_serial(project = project, **kwargs)
        return project      

    """ Private Methods """
   
    def _implement_in_parallel(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'implementation' to 'project' using multiple cores.

        Args:
            project (Project): chrisjen project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if project.parallelize:
            with multiprocessing.Pool() as pool:
                project = pool.starmap(
                    self._implement_in_serial, 
                    project, 
                    **kwargs)
        return project 

               
@dataclasses.dataclass
class Task(bases.Component):
    """Base class for nodes in a project workflow.

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
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    
    """ Public Methods """
    
    def execute(self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

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
            self.implement(project = project, **parameters)
        return project
    
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        try:
            project = self.contents.execute(project = project, **kwargs)
        except AttributeError:
            project = self.contents(project, **kwargs)
        return project   


@dataclasses.dataclass
class Step(Task):
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
class Technique(Task):
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
   