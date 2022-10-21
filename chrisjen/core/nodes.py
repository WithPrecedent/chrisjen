"""
nodes: core nodes in chrisjen project
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
import abc
import collections
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import contextlib
import dataclasses
from typing import (
    Any, Callable, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union)

import amos
import holden
import miller

from . import base
from . import nodes


@dataclasses.dataclass
class Worker(holden.System, base.ProjectNode, abc.ABC):
    """Base class for an iterative node.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[base.Project]): related Project instance.
                     
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = base.Parameters)
    project: Optional[base.Project] = None
                         
    """ Public Methods """

    @classmethod
    def create(cls, name: str, project: nodes.Project) -> Worker:
        """Constructs and returns a Worker instance.

        Args:
            name (str): name of node instance to be created.
            project (Project): project with information to create a node
                instance.
                
        Returns:
            Worker: an instance based on passed arguments.
            
        """
        worker = cls(name = name, project = project)
        for name in amos.iterify(project.outline.connections[name]):
            node = project.library.create(name = name, project = project)
            worker.append(item = node)
        return worker
    
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        for node in self.walk:
            component = self.project.factory.create(item = node)
            self.project = component.complete(self.project, **kwargs)
        return
  
                 
@dataclasses.dataclass
class Task(base.ProjectNode):
    """Base class for non-iterable nodes in a project workflow.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = base.Parameters)
    
    """ Public Methods """
    
    @classmethod
    def create(cls, name: str, project: nodes.Project, **kwargs: Any) -> Task:
        """Creates a Task instance based on passed arguments.

        Returns:
            Task: an instance based on passed arguments.
            
        """
        return cls(name = name, **kwargs)
       
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        try:
            item = self.contents.complete(item = item, **kwargs)
        except AttributeError:
            item = self.contents(item, **kwargs)
        return item   


@dataclasses.dataclass   
class Criteria(base.ProjectKeystone):
    """Evaluates paths for use by Judge.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

 
# def is_component(item: Union[object, Type[Any]]) -> bool:
#     """Returns whether 'item' is a component.

#     Args:
#         item (Union[object, Type[Any]]): instance or class to check.

#     Returns:
#         bool: whether 'item' is a component.
        
#     """
#     return (
#         miller.has_attributes(item, ['name', 'contents', 'parameters'])
#         and miller.has_methods(item, ['complete']))


                  
    # """ Public Methods """ 
           
    # def implement(
    #     self,
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Applies 'contents' to 'project'.
        
    #     Args:
    #         project (base.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         base.Project: with possible changes made.
            
    #     """
    #     if len(self.contents) > 1 and project.settings.general['parallelize']:
    #         project = self._implement_in_parallel(project = project, **kwargs)
    #     else:
    #         project = self._implement_in_serial(project = project, **kwargs)
    #     return project      

    # """ Private Methods """
   
    # def _implement_in_parallel(
    #     self, 
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Applies 'implementation' to 'project' using multiple cores.

    #     Args:
    #         project (Project): chrisjen project to apply changes to and/or
    #             gather needed data from.
                
    #     Returns:
    #         Project: with possible alterations made.       
        
    #     """
    #     if project.parallelize:
    #         with multiprocessing.Pool() as pool:
    #             project = pool.starmap(
    #                 self._implement_in_serial, 
    #                 project, 
    #                 **kwargs)
    #     return project 
  

