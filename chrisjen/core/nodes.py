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
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING

import amos
import holden
import miller

from ..core import framework
from ..core import keystones


@dataclasses.dataclass    
class Parameters(amos.Dictionary):
    """Creates and librarys parameters for part of a chrisjen project.
    
    The use of Parameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the contents of the
    'contents' attribute into an ordinary set of kwargs. In this way, it can 
    serve as a drop-in replacement for a dict that would ordinarily be used for 
    accumulating keyword arguments.
    
    If a chrisjen class uses a Parameters instance, the 'finalize' method should 
    be called before that instance's 'implement' method in order for each of the 
    parameter types to be incorporated.
    
    Args:
        contents (Mapping[str, Any]): keyword parameters for use by a chrisjen
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. To properly match 
            parameters in a Settings instance, 'name' should be the prefix to 
            "_parameters" as a section name in a Settings instance. Defaults to 
            None. 
        default (Mapping[str, Any]): default parameters that will be used if 
            they are not overridden. Defaults to an empty dict.
        implementation (Mapping[str, str]): parameters with values that can only 
            be determined at runtime due to dynamic nature of chrisjen and its 
            workflows. The keys should be the names of the parameters and the 
            values should be attributes or items in 'contents' of 'project' 
            passed to the 'finalize' method. Defaults to an emtpy dict.
        selected (MutableSequence[str]): an exclusive list of parameters that 
            are allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in an Outline instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: Optional[str] = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(
        default_factory = dict)
    selected: MutableSequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, item: Any, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            item (Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting amos.
        parameters = self.default
        # Adds any parameters from 'outline'.
        parameters.update(self._from_outline(item = item))
        # Adds any implementation parameters.
        parameters.update(self._at_runtime(item = item))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Adds any passed kwargs, which will override any other parameters.
        parameters.update(kwargs)
        # Limits parameters to those in 'selected'.
        if self.selected:
            parameters = {k: parameters[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_outline(self, project: framework.Project) -> dict[str, Any]: 
        """Returns any applicable parameters from 'outline'.

        Args:
            project (framework.Project): project has parameters from 'outline.'

        Returns:
            dict[str, Any]: any applicable outline parameters or an empty dict.
            
        """
        keys = [self.name]
        keys.append(project.outline.kinds[self.name])
        try:
            keys.append(project.outline.designs[self.name])
        except KeyError:
            pass
        for key in keys:
            try:
                return project.outline.implementation[key]
            except KeyError:
                pass
        return {}
   
    def _at_runtime(self, item: Any) -> dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            item (Project): instance from which implementation 
                parameters can be derived.

        Returns:
            dict[str, Any]: any applicable idea parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(item, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = (
                        item.idea['general'][attribute])
                except (KeyError, AttributeError):
                    pass
        return self
    
    
@dataclasses.dataclass
class Worker(keystones.Node, holden.System):
    """Base class for an iterative node.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (MutableMapping[Hashable, set[Hashable]]): keys are names of
            nodes and values are sets of names of nodes. Defaults to a 
            defaultdict that has a set for its value format.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[framework.Project]): related Project instance.
                     
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)
    
    """ Properties """

    # @property
    # def endpoint(self) -> MutableSequence[Hashable]:
    #     """Returns the endpoints of the stored graph."""
    #     return holden.get_endpoints_adjacency(item = self.contents)
                    
    # @property
    # def root(self) -> MutableSequence[Hashable]:
    #     """Returns the roots of the stored graph."""
    #     return holden.get_roots_adjacency(item = self.contents)

    # @property
    # def parallel(self) -> Collection[Hashable]:
    #     """Returns all paths through the stored as a list of paths."""
    #     return holden.adjacency_to_parallel(item = self.contents)
    
    # @property
    # def serial(self) -> base.Path:
    #     """Returns stored graph as a path."""
    #     return holden.adjacency_to_serial(item = self.contents)     
                        
    """ Class Methods """

    @classmethod
    def create(cls, name: str, project: framework.Project) -> Worker:
        """Constructs and returns a Worker instance.

        Args:
            name (str): name of node instance to be created.
            project (Project): project with information to create a node
                instance.
                
        Returns:
            Worker: an instance based on passed arguments.
            
        """
        worker = cls(name = name, project = project)
        for key in amos.iterify(project.outline.connections[name]):
            node = project.manager.librarian.acquire(name = key) 
            worker.append(item = node)
        return worker

    @classmethod
    def graph(cls, name: str, project: framework.Project) -> keystones.View:
        """Returns a directed acyclic graph with str names of nodes.

        Args:
            name (str): name of starting node.
            project (Project): project with information to create the graph.
                
        Returns:
            keystones.View: a graph based on passed arguments.
            
        """
        graph = project.library.view['workflow']
        graph.add(item = name)
        for key in amos.iterify(project.outline.connections[name]):
            node = project.manager.librarian.acquire(name = key) 
            worker.append(item = node)
        return worker
                                          
    """ Public Methods """
    
    def append(self, item: keystones.Graph) -> None:
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
            form = holden.classify(item = item)
            if form == 'adjacency':
                other = item
            else:
                transformer = globals()[f'{form}_to_adjacency']
                other = transformer(item = item)
            self.merge(item = other)
            for endpoint in current_endpoints:
                for root in holden.get_roots_adjacency(item = other):
                    self.connect((endpoint, root))
        elif isinstance(item, keystones.Node):
            current_endpoints = self.endpoint
            if item not in self:
                self.add(item = item)
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
            node = self.project.library.withdraw(
                item = name,
                parameters = {})
            item = node.complete(item, **kwargs)
        return item
  
    def prepend(self, item: keystones.Graph) -> None:
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
        if isinstance(item, keystones.Graph):
            current_roots = self.root
            form = holden.classify(item = item)
            if form == 'adjacency':
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
    
    # def walk(self, start: Hashable, stop: Hashable) -> Worker:
    #     """Returns all paths in graph from 'start' to 'stop'.

    #     The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
    #     Args:
    #         start (Hashable): node to start paths from.
    #         stop (Hashable): node to stop paths.
            
    #     Returns:
    #         Path: a list of possible paths (each path is a list nodes) from 
    #             'start' to 'stop'.
            
    #     """
    #     return holden.walk_adjacency(
    #         item = self.contents, 
    #         start = start, 
    #         stop = stop)

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
class Task(keystones.Node):
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
        default_factory = Parameters)
    
    """ Public Methods """
       
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
class NullNode(keystones.Node):
    """Class for null nodes in a chrisjen project.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to 'none'.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty dict.
              
    """
    name: Optional[str] = 'none'
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
                                      
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        name: str, 
        project: framework.Project, 
        **kwargs) -> NullNode:
        """Creates a Node instance based on passed arguments.

        Args:
            name (str): name of node instance to be created.
            project (Project): project with information to create a node
                instance.
                
        Returns:
            Node: an instance based on passed arguments.
            
        """
        return cls()

    """ Public Methods """
    
    def complete(self, item: Any, **kwargs: Any) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        return item 
    
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
        return item
        
 
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
    #     project: framework.Project, 
    #     **kwargs) -> framework.Project:
    #     """Applies 'contents' to 'project'.
        
    #     Args:
    #         project (framework.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         framework.Project: with possible changes made.
            
    #     """
    #     if len(self.contents) > 1 and project.idea.general['parallelize']:
    #         project = self._implement_in_parallel(project = project, **kwargs)
    #     else:
    #         project = self._implement_in_serial(project = project, **kwargs)
    #     return project      

    # """ Private Methods """
   
    # def _implement_in_parallel(
    #     self, 
    #     project: framework.Project, 
    #     **kwargs) -> framework.Project:
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
  

    
# def complete_worker(
#     name: str, 
#     worker: nodes.Worker, 
#     project: Project) -> nodes.Worker:
#     """_summary_

#     Args:
#         name (str): _description_
#         worker (nodes.Worker): _description_
#         project (Project): _description_

#     Returns:
#         nodes.Worker: _description_
        
#     """
#     for name in amos.iterify(project.outline.connections[name]):
#         kind = project.outline.kinds[name]  
#         if kind in project.outline.suffixes['workers']:
#             design = find_design(name = name, project = project)
#             parameters = {'name': name, 'project': project}
#             worker = project.manager.librarian.acquire(
#                 item = (name, design),
#                 parameters = parameters)
#             node = complete_worker(
#                 name = name, 
#                 worker = worker, 
#                 project = project)
#             worker.append(node)
#         else:
#             worker.append(name) 
#     return worker