"""
workflows: iteration patterns
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
    Waterfall (nodes.Worker): a pre-planned, rigid workflow structure.
    Kanban (nodes.Worker): a sequential workflow with isolated stages
        that produce deliverables for the following stage.
    Scrum (nodes.Worker): flexible workflow structure that requires
        greater user control and intervention.
    Pert (nodes.Worker): workflow that focuses on efficient use of 
        parallel resources, including identifying the critical path.
    Study (nodes.Worker, abc.ABC): base class for workflows that
         integrate criteria.
        
To Do:

            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import Hashable, MutableMapping, MutableSequence, Set
import dataclasses
import itertools
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING

import amos
import holden
import more_itertools

from ..core import framework
from ..core import keystones
from ..core import nodes
from . import represent
from . import views
from . import tasks


@dataclasses.dataclass
class Waterfall(views.Workflow):
    """A pre-planned, rigid workflow.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a chrisjen project.
            Defaults to None.
        contents (MutableMapping[Hashable, set[Hashable]]): keys are names of
            nodes and values are sets of names of nodes. Defaults to a 
            defaultdict that has a set for its value format.
        project (Optional[framework.Project]): related Project instance. 
            Defaults to None.
                     
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)
    
    """ Properties """

    @property
    def graph(self) -> holden.System:
        """Returns directed graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.
            
        """        
        graph = holden.System()
        if self.name != self.project.name:
            graph.add(item = self.name)
        # section = self.project.outline.connections[self.name]
        # print('test section', section)
        # print('test connections', self.project.outline.connections.keys())
        connections = self.project.outline.connections
        top_level = connections[self.name]
        for connection in top_level:
            if connection in self.project.outline.designs:
                design = self.project.outline.designs[connection]
                node = self.project.library.view[design]
                node = node.create(name = connection, project = self.project)
                print('test node', node)
                graph.append(node.graph)
            elif connection in connections:
                for subconnection in connections[connection]:
                    node = tuple([connection, subconnection])
                    graph.append(node)
            else:
                print('test else connection', connection)
                if connection in graph.keys():
                    endpoints = graph.endpoint
                    for end in endpoints:
                        graph.connect((end, connection))
                else:
                    graph.append(connection)   
        return graph 
      
    # @property
    # def idea(self) -> MutableMapping[str, Any]:
    #     """Returns connections from an Idea that are part of this workflow. 

    #     Returns:
    #         MutableMapping[str, Any]: _description_
            
    #     """
    #     return self.project.outline.workers[self.name]
    
    # @property
    # def labels(self) -> MutableSequence[str]:
    #     """_summary_

    #     Returns:
    #         MutableSequence[str]: _description_
    #     """        
    #     names = list(self.idea.keys())
    #     names.extend(list(itertools.chain.from_iterable(self.idea.values())))
    #     return names
    
    # @property
    # def parameters(self) -> MutableMapping[Hashable, nodes.Parameters]:
    #     """_summary_

    #     Returns:
    #         MutableMapping[Hashable, nodes.Parameters]: _description_
            
    #     """        
    #     arguments = {}
    #     for name in self.labels:
    #         try:
    #             new_parameters = nodes.Parameters(
    #                 contents = self.project.outline.implementation[name])
    #             arguments.update({name: new_parameters})
    #         except KeyError:
    #             arguments.update({})
    #     return arguments
       
    
@dataclasses.dataclass
class Research(views.Workflow, abc.ABC):
    """Base class for nodes that integrate criteria.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        project (Optional[framework.Project]): related Project instance.
            
    """
    name: Optional[str] = None
    contents: Optional[MutableSequence[nodes.Worker]] = dataclasses.field(
        default_factory = list)
    project: Optional[framework.Project] = None
    superviser: Optional[tasks.Superviser] = None

    """ Properties """

    @property
    def graph(self) -> holden.System:
        """Returns direct graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.
            
        """
        graph = holden.System()
        if self.name != self.project.name:
            graph.add(item = self.name)
        recipes = represent.represent_parallel(
            name = self.name, 
            project = self.project) 
        endpoints = amos.iterify(graph.endpoint)
        for endpoint in endpoints:
            for recipe in recipes:
                serial = holden.Serial(contents = recipe)
                graph.merge(item = serial)     
                graph.connect(tuple([endpoint, serial[0]])) 
        return graph

    # """ Public Methods """
    
    # def implement(self, item: Any, **kwargs: Any) -> Any:
    #     """Applies 'contents' to 'item'.

    #     Subclasses must provide their own methods.

    #     Args:
    #         item (Any): any item or data to which 'contents' should be applied, 
    #             but most often it is an instance of 'Project'.

    #     Returns:
    #         Any: any result for applying 'contents', but most often it is an
    #             instance of 'Project'.
            
    #     """
    #     projects = self.superviser.complete(item = item)
    #     results = {}
    #     for i, (key, worker) in enumerate(self.contents.items()):
    #         results[key] = worker.complete(item = projects[i], **kwargs)
    #     return results
              

# @dataclasses.dataclass
# class Superviser(views.Workflow):
#     """Base class for making multiple instances of a project.
    
#     Args:
#         name (Optional[str]): designates the name of a class instance that is 
#             used for internal and external referencing in a project workflow.
#             Defaults to None.
#         contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
#             to the 'complete' method. Defaults to None.
#         parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
#             'contents' when the 'implement' method is called. Defaults to an
#             empty Parameters instance.
              
#     """
#     name: Optional[str] = None
#     contents: Optional[Any] = None
#     parameters: MutableMapping[Hashable, Any] = dataclasses.field(
#         default_factory = nodes.Parameters)
    
#     """ Public Methods """
     
#     def implement(self, item: Any, **kwargs: Any) -> Any:
#         """Applies 'contents' to 'item'.

#         Subclasses must provide their own methods.

#         Args:
#             item (Any): any item or data to which 'contents' should be applied, 
#                 but most often it is an instance of 'Project'.

#         Returns:
#             Any: any result for applying 'contents', but most often it is an
#                 instance of 'Project'.
            
#         """
#         pass
     


# def represent_research(
#     name: str, 
#     project: nodes.Project,
#     **kwargs) -> Studyer:
#     """[summary]

#     Args:
#         name (str): [description]
#         project (nodes.Project): [description]

#     Returns:
#         Experiment: [description]
        
#     """    
#     design = project.idea.designs.get(name, None) 
#     kind = project.idea.kinds.get(name, None) 
#     lookups = _get_lookups(name = name, design = design, kind = kind)
#     base = project.components.withdraw(item = lookups)
#     parameters = amos.get_annotations(item = base)
#     attributes, initialization = _parse_initialization(
#         name = name,
#         settings = project.idea,
#         parameters = parameters)
#     initialization['parameters'] = _get_runtime(
#         lookups = lookups,
#         settings = project.idea)
#     component = base(name = name, **initialization)
#     for key, value in attributes.items():
#         setattr(component, key, value)
#     return component


# def implement(
#     node: nodes.Component,
#     project: nodes.Project, 
#     **kwargs) -> nodes.Project:
#     """Applies 'node' to 'project'.

#     Args:
#         node (nodes.Component): node in a workflow to apply to 'project'.
#         project (nodes.Project): instance from which data needed for 
#             implementation should be derived and all results be added.

#     Returns:
#         nodes.Project: with possible changes made by 'node'.
        
#     """
#     ancestors = count_ancestors(node = node, workflow = project.workflow)
#     descendants = len(project.workflow[node])
#     if ancestors > descendants:
#         method = closer_implement
#     elif ancestors < descendants:
#         method = test_implement
#     elif ancestors == descendants:
#         method = task_implement
#     return method(node = node, project = project, **kwargs)
    
# def closer_implement(
#     node: nodes.Component,
#     project: nodes.Project, 
#     **kwargs) -> nodes.Project:
#     """Applies 'node' to 'project'.

#     Args:
#         node (nodes.Component): node in a workflow to apply to 'project'.
#         project (nodes.Project): instance from which data needed for 
#             implementation should be derived and all results be added.

#     Returns:
#         nodes.Project: with possible changes made by 'node'.
        
#     """
#     try:
#         project = node.complete(project = project, **kwargs)
#     except AttributeError:
#         project = node(project, **kwargs)
#     return project    

# def test_implement(
#     node: nodes.Component,
#     project: nodes.Project, 
#     **kwargs) -> nodes.Project:
#     """Applies 'node' to 'project'.

#     Args:
#         node (nodes.Component): node in a workflow to apply to 'project'.
#         project (nodes.Project): instance from which data needed for 
#             implementation should be derived and all results be added.

#     Returns:
#         nodes.Project: with possible changes made by 'node'.
        
#     """
#     connections = project.workflow[node]
#     # Makes copies of project for each pipeline in a test.
#     copies = [copy.deepcopy(project) for _ in connections]
#     # if project.idea['general']['parallelize']:
#     #     method = _test_implement_parallel
#     # else:
#     #     method = _test_implement_serial
#     results = []
#     for i, connection in enumerate(connections):
#         results.append(implement(
#             node = project.workflow[connection],
#             project = copies[i], 
#             **kwargs))
         
# def task_implement(
#     node: nodes.Component,
#     project: nodes.Project, 
#     **kwargs) -> nodes.Project:
#     """Applies 'node' to 'project'.

#     Args:
#         node (nodes.Component): node in a workflow to apply to 'project'.
#         project (nodes.Project): instance from which data needed for 
#             implementation should be derived and all results be added.

#     Returns:
#         nodes.Project: with possible changes made by 'node'.
        
#     """
#     try:
#         project = node.complete(project = project, **kwargs)
#     except AttributeError:
#         project = node(project, **kwargs)
#     return project    

# def count_ancestors(node: nodes.Component, workflow: defaults.Stage) -> int:
#     connections = list(more_itertools.collapse(workflow.values()))
#     return connections.count(node)
    
    
    