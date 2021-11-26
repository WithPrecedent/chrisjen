"""
stages: classes and functions related to stages of a chrisjen project
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
    Workflow
    Results
    create_workflow
    create_results

To Do:
    Add support for parallel construction of Results in the 'create_results'
        function.
        
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Sequence, Set)
import dataclasses
import itertools
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases

if TYPE_CHECKING:
    from . import configuration
    from . import interface
    

""" Public Classes """

@dataclasses.dataclass
class Workflow(object):
    """Project workflow composite object.
    
    Args:
    Args:
        name (str): name of class used for internal referencing and logging.
            Defaults to 'worfklow'.
        contents (Optional[amos.Composite]): iterable composite data structure 
            for storing the project workflow. Defaults to None.
                  
    """  
    name: str = 'workflow'
    contents: Optional[amos.Composite] = None
    
    """ Public Methods """
    
    @classmethod
    def create(cls, project: interface.Project) -> Workflow:
        """[summary]

        Args:
            project (interface.Project): [description]

        Returns:
            Workflow: [description]
            
        """        
        return create_workflow(project = project, base = cls)    

    # def execute(
    #     self, 
    #     project: interface.Project, 
    #     **kwargs) -> interface.Project:
    #     """Calls the 'implement' method the number of times in 'iterations'.

    #     Args:
    #         project (interface.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         interface.Project: with possible changes made.
            
    #     """
    #     if self.contents not in [None, 'None', 'none']:
    #         for node in self:
    #             project = node.execute(project = project, **kwargs)
    #     return project
    
    
@dataclasses.dataclass
class Results(object):
    """Project workflow after it has been implemented.
    
    Args:
        name (str): name of class used for internal referencing and logging.
            Defaults to 'results'.
        contents (Optional[amos.Composite]): iterable composite data structure 
            for storing the project results. Defaults to None.
                  
    """  
    name: str = 'results'
    contents: Optional[amos.Composite] = None
    
    """ Public Methods """

    @classmethod
    def create(cls, project: interface.Project) -> Results:
        """[summary]

        Args:
            project (interface.Project): [description]

        Returns:
            Results: [description]
            
        """        
        return create_results(project = project, base = cls)

    
""" Public Functions """

def create_workflow(
    project: interface.Project,
    base: Optional[Type[Workflow]] = None, 
    **kwargs) -> Workflow:
    """[summary]

    Args:
        project (interface.Project): [description]
        base (Optional[Type[Workflow]]): [description]. Defaults to None.

    Returns:
        Workflow: [description]
        
    """    
    base = base or Workflow
    if 'contents' not in kwargs:
        kwargs['contents'] = _get_structure(project = project)
    elif isinstance(kwargs['contents'], str):
        kwargs['contents'] = amos.Composite.create(kwargs['contents'])
    workflow = base(**kwargs)
    return _settings_to_workflow(
        settings = project.settings,
        options = project.nodes,
        workflow = workflow)
    
def create_workflow(
    project: interface.Project,
    base: Optional[Type[Workflow]] = None, 
    **kwargs) -> Workflow:
    """[summary]

    Args:
        project (interface.Project): [description]
        base (Optional[Type[Workflow]]): [description]. Defaults to None.

    Returns:
        Workflow: [description]
        
    """    
    base = base or Workflow
    workflow = base(**kwargs)
    return _settings_to_workflow(
        settings = project.settings,
        options = project.nodes,
        workflow = workflow)

def create_results(
    project: interface.Project,
    base: Optional[Type[Results]] = None, 
    **kwargs) -> Results:
    """[summary]

    Args:
        project (interface.Project): [description]
        base (Optional[Type[Results]]): [description]. Defaults to None.

    Returns:
        Results: [description]
        
    """    
    base = base or Results
    results = base(**kwargs)
    for path in project.workflow.paths:
        results.add(_path_to_result(path = path, project = project))
    return results

""" Private Functions """

def _get_structure(project: interface.Project) -> amos.Composite:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        amos.Composite: [description]
        
    """
    try:
        structure = project.settings[project.name][f'{project.name}_structure']
    except KeyError:
        try:
            structure = project.settings[project.name]['structure']
        except KeyError:
            structure = project.bases.default_workflow
    return amos.Composite.create(structure)
    
def _settings_to_workflow(
    settings: configuration.ProjectSettings, 
    options: amos.Catalog, 
    workflow: Workflow) -> Workflow:
    """[summary]

    Args:
        settings (configuration.ProjectSettings): [description]
        options (bases.LIBRARY): [description]

    Returns:
        Workflow: [description]
        
    """
    components = {}
    for name in settings.labels:
        components[name] = _settings_to_component(
            name = name,
            settings = settings,
            options = options)
    workflow = _settings_to_adjacency(
        settings = settings, 
        components = components,
        system = workflow)
    return workflow 

def _settings_to_component(
    name: str, 
    settings: configuration.ProjectSettings,
    options: amos.Catalog) -> bases.Projectbases.ProjectNode:
    """[summary]

    Args:
        name (str): [description]
        settings (configuration.ProjectSettings): [description]
        options (amos.Catalog): [description]

    Returns:
        bases.Projectbases.ProjectNode: [description]
        
    """    
    design = settings.designs.get(name, None) 
    kind = settings.kinds.get(name, None) 
    lookups = _get_lookups(name = name, design = design, kind = kind)
    base = _get_base(lookups = lookups, options = options)
    parameters = amos.get_annotations(item = base)
    attributes, initialization = _parse_initialization(
        name = name,
        settings = settings,
        parameters = parameters)
    initialization['parameters'] = _get_runtime(
        lookups = lookups,
        settings = settings)
    component = base(name = name, **initialization)
    for key, value in attributes.items():
        setattr(component, key, value)
    return component

def _get_lookups(
    name: str, 
    design: Optional[str], 
    kind: Optional[str]) -> list[str]:
    """[summary]

    Args:
        name (str): [description]
        design (Optional[str]): [description]
        kind (Optional[str]): [description]

    Returns:
        list[str]: [description]
        
    """    
    lookups = [name]
    if design:
        lookups.append(design)
    if kind:
        lookups.append(kind)
    return lookups

def _get_base(
    lookups: Sequence[str],
    options: amos.Catalog) -> bases.Component:
    """[summary]

    Args:
        lookups (Sequence[str]): [description]
        options (amos.Catalog): [description]

    Raises:
        KeyError: [description]

    Returns:
        bases.Component: [description]
        
    """
    for lookup in lookups:
        try:
            return options[lookup]
        except KeyError:
            pass
    raise KeyError(f'No matches in the node options found for {lookups}')

def _get_runtime(
    lookups: list[str], 
    settings: configuration.ProjectSettings) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        settings (configuration.ProjectSettings): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """    
    runtime = {}
    for key in lookups:
        try:
            match = settings.runtime[key]
            runtime[lookups[0]] = match
            break
        except KeyError:
            pass
    return runtime

def _parse_initialization(
    name: str,
    settings: configuration.ProjectSettings, 
    parameters: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    """[summary]

    Args:
        name (str): [description]
        settings (configuration.ProjectSettings): [description]
        parameters (list[str]): [description]

    Returns:
        tuple[dict[str, Any], dict[str, Any]]: [description]
        
    """
    if name in settings.initialization:
        attributes = {}
        initialization = {}
        for key, value in settings.initialization[name].items(): 
            if key in parameters:
                initialization[key] = value
            else:
                attributes[key] = value
        return attributes, initialization
    else:
        return {}, {}  

def _settings_to_adjacency(
    settings: configuration.ProjectSettings, 
    components: dict[str, bases.Projectbases.ProjectNode],
    system: Workflow) -> amos.Pipeline:
    """[summary]

    Args:
        settings (configuration.ProjectSettings): [description]
        components (dict[str, bases.Projectbases.ProjectNode]): [description]
        system (Workflow): [description]

    Returns:
        Workflow: [description]
        
    """    
    for node, connects in settings.connections.items():
        component = components[node]
        system = component.integrate(item = system)    
    return system

def _path_to_result(
    path: amos.Pipeline,
    project: interface.Project,
    **kwargs) -> amos.Pipeline:
    """[summary]

    Args:
        path (amos.Pipeline): [description]
        project (interface.Project): [description]

    Returns:
        object: [description]
        
    """
    result = amos.Pipeline()
    for path in project.workflow.paths:
        for node in path:
            result.append(node.execute(project = project, *kwargs))
    return result
