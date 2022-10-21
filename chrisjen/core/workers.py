"""
workers: composite nodes
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
    Research (nodes.Worker, abc.ABC): base class for workflows that
         integrate criteria.
    Agile (Research): a dynamic workflow structure that changes direction based 
        on one or more criteria.
    Contest (Research): evaluates and selects best workflow among several based 
        on one or more criteria.
    Lean (Research): an iterative workflow that maximizes efficiency based on
        one or more criteria.
    Survey (Research): averages multiple workflows based on one or more 
        criteria.
        
To Do:

            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import Hashable, MutableMapping, MutableSequence, Set
import contextlib
import dataclasses
import itertools
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

import amos
import holden
import more_itertools

from . import base
from . import nodes
from . import tasks


@dataclasses.dataclass
class Waterfall(nodes.Worker):
    """A pre-planned, rigid workflow node.
        
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

    
@dataclasses.dataclass
class Research(holden.Paths, abc.ABC):
    """Base class for nodes that integrate criteria.
        
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
    proctor: Optional[tasks.Proctor] = None

    """ Class Methods """
    
    @classmethod
    def create(cls, name: str, project: nodes.Project) -> Research:
        """[summary]

        Args:
            item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
                [description]

        Returns:
            [type]: [description]
            
        """
        worker = cls(name = name, project = project)
        steps = project.connections[name]
        connections = project.connections[name]
        possible = [connections[s] for s in steps]
        combos = list(itertools.product(*possible))   
        for combo in combos:
            for i, task in enumerate(combo):
                step = project.factory.create(
                    name = steps[i], 
                    project = project,
                    technique = task)
                if i > 0:
                    worker.add()
                    
            recipes.append(recipe) 
        return cls(name = name, project = project)

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
        projects = self.proctor.complete(item = item)
        results = {}
        for i, (key, worker) in enumerate(self.contents.items()):
            results[key] = worker.complete(item = projects[i], **kwargs)
        return results
            

@dataclasses.dataclass
class Contest(Research):
    """Base class for tests that return one path from several.
        
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
    proctor: Optional[tasks.Proctor] = None
    judge: Optional[tasks.Judge] = None

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
        results = super().implement(item = item, **kwargs)
        project = self.judge.complete(projects = results)  
        return project
            

@dataclasses.dataclass
class Lean(Research):
    """Iterative workflow that maximizes efficiency based on criteria.
        
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
    proctor: Optional[tasks.Proctor] = None
    judge: Optional[tasks.Judge] = None
            

@dataclasses.dataclass
class Survey(Research):
    """Base class for research that averages results among several paths.
        
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
    proctor: Optional[tasks.Proctor] = None
    judge: Optional[tasks.Judge] = None



    
    

def create_researcher(
    name: str, 
    project: nodes.Project,
    **kwargs) -> Researcher:
    """[summary]

    Args:
        name (str): [description]
        project (nodes.Project): [description]

    Returns:
        Experiment: [description]
        
    """    
    design = project.settings.designs.get(name, None) 
    kind = project.settings.kinds.get(name, None) 
    lookups = _get_lookups(name = name, design = design, kind = kind)
    base = project.components.withdraw(item = lookups)
    parameters = amos.get_annotations(item = base)
    attributes, initialization = _parse_initialization(
        name = name,
        settings = project.settings,
        parameters = parameters)
    initialization['parameters'] = _get_runtime(
        lookups = lookups,
        settings = project.settings)
    component = base(name = name, **initialization)
    for key, value in attributes.items():
        setattr(component, key, value)
    return component


def implement(
    node: nodes.Component,
    project: nodes.Project, 
    **kwargs) -> nodes.Project:
    """Applies 'node' to 'project'.

    Args:
        node (nodes.Component): node in a workflow to apply to 'project'.
        project (nodes.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        nodes.Project: with possible changes made by 'node'.
        
    """
    ancestors = count_ancestors(node = node, workflow = project.workflow)
    descendants = len(project.workflow[node])
    if ancestors > descendants:
        method = closer_implement
    elif ancestors < descendants:
        method = test_implement
    elif ancestors == descendants:
        method = task_implement
    return method(node = node, project = project, **kwargs)
    
def closer_implement(
    node: nodes.Component,
    project: nodes.Project, 
    **kwargs) -> nodes.Project:
    """Applies 'node' to 'project'.

    Args:
        node (nodes.Component): node in a workflow to apply to 'project'.
        project (nodes.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        nodes.Project: with possible changes made by 'node'.
        
    """
    try:
        project = node.complete(project = project, **kwargs)
    except AttributeError:
        project = node(project, **kwargs)
    return project    

def test_implement(
    node: nodes.Component,
    project: nodes.Project, 
    **kwargs) -> nodes.Project:
    """Applies 'node' to 'project'.

    Args:
        node (nodes.Component): node in a workflow to apply to 'project'.
        project (nodes.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        nodes.Project: with possible changes made by 'node'.
        
    """
    connections = project.workflow[node]
    # Makes copies of project for each pipeline in a test.
    copies = [copy.deepcopy(project) for _ in connections]
    # if project.settings['general']['parallelize']:
    #     method = _test_implement_parallel
    # else:
    #     method = _test_implement_serial
    results = []
    for i, connection in enumerate(connections):
        results.append(implement(
            node = project.workflow[connection],
            project = copies[i], 
            **kwargs))
         
def task_implement(
    node: nodes.Component,
    project: nodes.Project, 
    **kwargs) -> nodes.Project:
    """Applies 'node' to 'project'.

    Args:
        node (nodes.Component): node in a workflow to apply to 'project'.
        project (nodes.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        nodes.Project: with possible changes made by 'node'.
        
    """
    try:
        project = node.complete(project = project, **kwargs)
    except AttributeError:
        project = node(project, **kwargs)
    return project    

def count_ancestors(node: nodes.Component, workflow: framework.Stage) -> int:
    connections = list(more_itertools.collapse(workflow.values()))
    return connections.count(node)
    
    
    