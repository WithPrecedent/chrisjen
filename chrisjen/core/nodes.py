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
    Collection, Hashable, Mapping, MutableMapping, MutableSequence, Set)
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
class Worker(holden.Adjacency, holden.Directed, base.ProjectNode):
    """Base class for an iterative node.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (MutableMapping[Hashable, Set[Hashable]]): keys are names of
            nodes and values are sets of names of nodes. Defaults to a 
            defaultdict that has a set for its value format.
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
    
    """ Properties """

    @property
    def endpoint(self) -> MutableSequence[Hashable]:
        """Returns the endpoints of the stored graph."""
        return holden.get_endpoints_adjacency(item = self.contents)
                    
    @property
    def root(self) -> MutableSequence[Hashable]:
        """Returns the roots of the stored graph."""
        return holden.get_roots_adjacency(item = self.contents)

    @property
    def parallel(self) -> Collection[Hashable]:
        """Returns all paths through the stored as a list of paths."""
        return holden.adjacency_to_parallel(item = self.contents)
    
    @property
    def serial(self) -> base.Path:
        """Returns stored graph as a path."""
        return holden.adjacency_to_serial(item = self.contents)     
                        
    """ Class Methods """

    @classmethod
    def create(cls, name: str, project: base.Project) -> Worker:
        """Constructs and returns a Worker instance.

        Args:
            name (str): name of node instance to be created.
            project (Project): project with information to create a node
                instance.
                
        Returns:
            Worker: an instance based on passed arguments.
            
        """
        worker = cls(name = name, project = project)
        for node in amos.iterify(project.outline.connections[name]):
            project.factory.create(name = node)
            worker.append(item = node)
        return worker
                         
    """ Public Methods """
    
    def append(self, item: base.Graph) -> None:
        """Appends 'item' to the endpoints of the stored graph.

        Appending creates an edge between every endpoint of this instance's
        stored graph and the every root of 'item'.

        Args:
            item (base.Graph): another Graph, 
                an adjacency list, an edge list, an adjacency matrix, or one or
                more nodes.
            
        Raises:
            TypeError: if 'item' is neither a Graph, Adjacency, Edges, Matrix,
                or Collection[Hashable] type.
                
        """
        if isinstance(item, holden.Graph):
            current_endpoints = self.endpoint
            form = holden.what_form(item = item)
            if form is 'adjacency':
                other = item
            else:
                transformer = globals()[f'{form}_to_adjacency']
                other = transformer(item = item)
            self.merge(item = other)
            for endpoint in current_endpoints:
                for root in holden.get_roots_adjacency(item = other):
                    self.connect((endpoint, root))
        elif holden.is_node(item = item):
            current_endpoints = self.endpoint
            for endpoint in current_endpoints:
                self.connect((endpoint, item))            
        else:
            raise TypeError('item is not a recognized graph type')
        return
        
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        for name in self.walk:
            node = self.project.factory.library.withdraw(
                item = name,
                parameters = {})
            item = node.complete(item, **kwargs)
        return item
  
    def prepend(self, item: base.Graph) -> None:
        """Prepends 'item' to the roots of the stored graph.

        Prepending creates an edge between every endpoint of 'item' and every
        root of this instance;s stored graph.

        Args:
            item (base.Graph): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, Adjacency, Edges, Matrix, 
                or Collection[Hashable] type.
                
        """
        if isinstance(item, base.Graph):
            current_roots = self.root
            form = holden.what_form(item = item)
            if form is 'adjacency':
                other = item
            else:
                transformer = globals()[f'{form}_to_adjacency']
                other = transformer(item = item)
            self.merge(item = other)
            for root in current_roots:
                for endpoint in other.endpoint:
                    self.connect((endpoint, root))
        elif holden.is_node(item = item):
            current_roots = self.root
            for root in current_roots:
                self.connect((item, root))     
        else:
            raise TypeError('item is not a recognized graph type')
        return
    
    def walk(self, start: Hashable, stop: Hashable) -> Worker:
        """Returns all paths in graph from 'start' to 'stop'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (Hashable): node to start paths from.
            stop (Hashable): node to stop paths.
            
        Returns:
            Path: a list of possible paths (each path is a list nodes) from 
                'start' to 'stop'.
            
        """
        return holden.walk_adjacency(
            item = self.contents, 
            start = start, 
            stop = stop)

    """ Private Methods """
    
    def _add(self, item: Hashable) -> None:
        """Adds node to the stored graph.
                   
        Args:
            item (Hashable): node to add to the stored graph.
            
        Raises:
            TypeError: if 'item' is not a compatible type.
                
        """
        if not holden.is_node(item = item):
            name = item.name
            self.nodes.deposit(item = item, name = name)
        elif isinstance(item, Hashable):
            name = item
        else:
            raise TypeError(f'{item} is not a compatible type')
        self.contents[name] = set()
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
  

