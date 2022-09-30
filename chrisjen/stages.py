"""
stages: classes and functions related to stages of a chrisjen project
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

from . import base

if TYPE_CHECKING:
    from . import configuration
    from . import base
    



@dataclasses.dataclass
class Outline(Stage):
    """Provides a different view of data stored in 'project.settings'.
    
    The properties in Outline are used in the construction of a Workflow. So,
    even if you do not have any interest in using its view of the configuration
    settings, it shouldn't be cut out of a Project (unless you also replace the
    functions for creating a Workflow). 

    Args:
        project (base.Project): a related project instance which has data
            from which the properties of an Outline can be derived.

    """
    project: base.Project

    """ Properties """       

    @functools.cached_property
    def connections(self) -> dict[str, dict[str, list[str]]]:
        """Returns raw connections between nodes from 'project'.
        
        Returns:
            dict[str, dict[str, list[str]]]: keys are worker names and values 
                node connections for that worker.
            
        """
        try:
            return workshop.get_connections(project = self.project)
        except AttributeError:
            raise AttributeError(
                'ProjectSettings needs to be linked to a project to access '
                'that information.')
                        
    @functools.cached_property
    def designs(self) -> dict[str, str]:
        """Returns structural designs of nodes in 'project'.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        try:
            return workshop.get_designs(project = self.project)
        except AttributeError:
            raise AttributeError(
                'Outline needs to be linked to a project to access '
                'that information.')
                                        
    @functools.cached_property
    def implementation(self) -> dict[str, dict[str, Any]]:
        """Returns implementation arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        try:
            return workshop.get_implementation(project = self.project)
        except AttributeError:
            raise AttributeError(
                'Outline needs to be linked to a project to access '
                'that information.')    
                                                
    @functools.cached_property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        try:
            return workshop.get_initialization(project = self.project)
        except AttributeError:
            raise AttributeError(
                'Outline needs to be linked to a project to access '
                'that information.')
        
    @functools.cached_property
    def kinds(self) -> dict[str, str]:
        """Returns kinds of ndoes in 'project'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        try:
            return workshop.get_kinds(project = self.project)
        except AttributeError:
            raise AttributeError(
                'Outline needs to be linked to a project to access '
                'that information.')
    
    @functools.cached_property
    def labels(self) -> list[str]:
        """Returns names of nodes in 'project'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        try:
            return workshop.get_labels(project = self.project)
        except AttributeError:
            raise AttributeError(
                'Outline needs to be linked to a project to access '
                'that information.')

    @functools.cached_property
    def workers(self) -> dict[str, dict[Hashable, Any]]:
        """Returns sections in 'project.settings' that are related to workers.

        Returns:
            dict[str, dict[Hashable, Any]]: keys are the names of worker 
                sections and values are those sections.
            
        """
        try:            
            return workshop.get_worker_sections(project = self.project)
        except AttributeError:
            raise AttributeError(
                'Outline needs to be linked to a project to access '
                'that information.')
        
        
@dataclasses.dataclass
class Workflow(Component):
    """Project workflow composite object.
    
    Args:
        contents (MutableMapping[str, Set[str]]): keys are names of nodes and
            values are sets of names of nodes. Defaults to a defaultdict that 
            has a set for its value format.
                  
    """  
    contents: MutableMapping[str, Set[str]] = dataclasses.field(
            default_factory = lambda: collections.defaultdict(set))
    
    """ Public Methods """
    
    @classmethod
    def create(cls, project: base.Project) -> Workflow:
        """[summary]

        Args:
            project (base.Project): [description]

        Returns:
            Workflow: [description]
            
        """        
        return workshop.create_workflow(project = project, base = cls)    

    def append_depth(
        self, 
        item: MutableMapping[Hashable, MutableSequence[Hashable]]) -> None:
        """[summary]

        Args:
            item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
                [description]

        Returns:
            [type]: [description]
            
        """        
        first_key = list(item.keys())[0]
        self.append(first_key)
        for node in item[first_key]:
            self.append(item[node])
        return self   
    
    def append_product(
        self, 
        item: MutableMapping[Hashable, MutableSequence[Hashable]]) -> None:
        """[summary]

        Args:
            item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
                [description]

        Returns:
            [type]: [description]
            
        """        
        first_key = list(item.keys())[0]
        self.append(first_key)
        possible = [v for k, v in item.items() if k in item[first_key]]
        combos = list(itertools.product(*possible))
        self.append(combos)
        return self
    

@dataclasses.dataclass
class Results(ProjectBase):
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
    def create(cls, project: base.Project) -> Results:
        """[summary]

        Args:
            project (base.Project): [description]

        Returns:
            Results: [description]
            
        """        
        return workshop.create_results(project = project, base = cls)

    # def execute(
    #     self, 
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Calls the 'implement' method the number of times in 'iterations'.

    #     Args:
    #         project (base.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         base.Project: with possible changes made.
            
    #     """
    #     if self.contents not in [None, 'None', 'none']:
    #         for node in self:
    #             project = node.execute(project = project, **kwargs)
    #     return project
    
    

@dataclasses.dataclass
class Workflow(object):
    """Project workflow composite object.
    
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
    def create(cls, project: base.Project) -> Workflow:
        """[summary]

        Args:
            project (base.Project): [description]

        Returns:
            Workflow: [description]
            
        """        
        return create_workflow(project = project, base = cls)    

    # def execute(
    #     self, 
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Calls the 'implement' method the number of times in 'iterations'.

    #     Args:
    #         project (base.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         base.Project: with possible changes made.
            
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
    def create(cls, project: base.Project) -> Results:
        """[summary]

        Args:
            project (base.Project): [description]

        Returns:
            Results: [description]
            
        """        
        return create_results(project = project, base = cls)

    
""" Public Functions """

def create_workflow(
    project: base.Project,
    base: Optional[Type[Workflow]] = None, 
    **kwargs) -> Workflow:
    """[summary]

    Args:
        project (base.Project): [description]
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
        options = project.options,
        workflow = workflow)
    
def create_workflow(
    project: base.Project,
    base: Optional[Type[Workflow]] = None, 
    **kwargs) -> Workflow:
    """[summary]

    Args:
        project (base.Project): [description]
        base (Optional[Type[Workflow]]): [description]. Defaults to None.

    Returns:
        Workflow: [description]
        
    """    
    print('test settings kinds', project.settings.kinds) 
    base = base or Workflow
    workflow = base(**kwargs)
    return _settings_to_workflow(
        settings = project.settings,
        options = project.options,
        workflow = workflow)

def create_results(
    project: base.Project,
    base: Optional[Type[Results]] = None, 
    **kwargs) -> Results:
    """[summary]

    Args:
        project (base.Project): [description]
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

def _get_structure(project: base.Project) -> amos.Composite:
    """[summary]

    Args:
        project (base.Project): [description]

    Returns:
        amos.Composite: [description]
        
    """
    try:
        structure = project.settings[project.name][f'{project.name}_structure']
    except KeyError:
        try:
            structure = project.settings[project.name]['structure']
        except KeyError:
            structure = project.base.default_workflow
    return amos.Composite.create(structure)
    
def _settings_to_workflow(
    settings: configuration.ProjectSettings, 
    options: amos.Catalog, 
    workflow: Workflow) -> Workflow:
    """[summary]

    Args:
        settings (configuration.ProjectSettings): [description]
        options (base.LIBRARY): [description]

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
    options: amos.Catalog) -> base.Projectbase.Component:
    """[summary]

    Args:
        name (str): [description]
        settings (configuration.ProjectSettings): [description]
        options (amos.Catalog): [description]

    Returns:
        base.Projectbase.Component: [description]
        
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
    options: amos.Catalog) -> base.Component:
    """[summary]

    Args:
        lookups (Sequence[str]): [description]
        options (amos.Catalog): [description]

    Raises:
        KeyError: [description]

    Returns:
        base.Component: [description]
        
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
    components: dict[str, base.Projectbase.Component],
    system: Workflow) -> amos.Pipeline:
    """[summary]

    Args:
        settings (configuration.ProjectSettings): [description]
        components (dict[str, base.Projectbase.Component]): [description]
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
    project: base.Project,
    **kwargs) -> amos.Pipeline:
    """[summary]

    Args:
        path (amos.Pipeline): [description]
        project (base.Project): [description]

    Returns:
        object: [description]
        
    """
    result = amos.Pipeline()
    for path in project.workflow.paths:
        for node in path:
            result.append(node.execute(project = project, *kwargs))
    return result
