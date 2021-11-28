"""
nodes: core node types for project workflows
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
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.

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
    iterations: Union[int, str] = 1

    """ Public Methods """  
    
    def execute(self, 
        project: interface.Project, 
        iterations: Optional[Union[int, str]] = None, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        iterations = iterations or self.iterations
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if hasattr(self.parameters, 'finalize'):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if iterations in ['infinite']:
                while True:
                    project = self.implement(project = project, **parameters)
            else:
                for _ in range(iterations):
                    project = self.implement(project = project, **parameters)
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
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
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
    iterations: Union[int, str] = 1
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
class Judge(bases.Task):
    """Selects one or more Worker instances from a Manager.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[bases.Criteria]): technique for selecting one or more
            Worker instances. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                                                 
    """
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    