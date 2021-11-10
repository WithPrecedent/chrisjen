"""
workshop: helper classes and functions for projects
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

"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping, Sequence
import itertools

from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases

if TYPE_CHECKING:
    from . import interface
    from . import stages


def get_connections(project: interface.Project) -> dict[str, list[str]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """
    connections = {}
    for key, section in project.settings.items():
        if any(k.endswith(project.nodes.suffixes) for k in section.keys()):
            new_connections = get_section_connections(
                section = section,
                name = key,
                suffixes = project.nodes.suffixes)
            for inner_key, inner_value in new_connections.items():
                if inner_key in connections:
                    connections[inner_key].extend(inner_value)
                else:
                    connections[inner_key] = inner_value
    return connections

def get_designs(project: interface.Project) -> dict[str, str]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    designs = {}
    for key, section in project.settings.items():
        if any(k.endswith(project.nodes.suffixes) for k in section.keys()):
            new_designs = get_section_designs(section = section, name = key)
            designs.update(new_designs)
    return designs

def get_initialization(project: interface.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    initialization = {}
    for key, section in project.settings.items():   
        new_initialization = get_section_initialization(section = section)
        initialization[key] = new_initialization
    return initialization
                          
def get_kinds(project: interface.Project) -> dict[str, str]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    kinds = {}
    for key, section in project.settings.items():
        if any(k.endswith(project.nodes.suffixes) for k in section.keys()):
            new_kinds = get_section_kinds(
                section = section,
                suffixes = project.nodes.suffixes)
            kinds.update(new_kinds)  
    return kinds

def get_labels(project: interface.Project) -> list[str]:
    """Returns names of nodes based on 'project.settings'.

    Args:
        project (interface.Project): an instance of Project with 'settings' and
            'connections'.
        
    Returns:
        list[str]: names of all nodes that are listed in 'project.settings'.
        
    """        
    key_nodes = list(project.connections.keys())
    value_nodes = list(
        itertools.chain.from_iterable(project.connections.values()))
    return amos.deduplicate(item = key_nodes + value_nodes)     
      
def get_runtime(project: interface.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    runtime = {}
    for key, section in project.settings.items():
        if key.endswith('_parameters'):
            new_key = amos.drop_suffix(item = key, suffix = '_parameters')
            runtime[new_key] = section
    return runtime

def get_section_initialization(
    section: MutableMapping[Hashable, Any],
    suffixes: Sequence[str]) -> dict[str, Any]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, Any]: [description]
        
    """
    all_suffixes = suffixes + 'design'
    return {
        k: v for k, v in section.items() if not k.endswith(all_suffixes)}
    
def get_section_connections(
    section: MutableMapping[Hashable, Any],
    name: str,
    suffixes: Sequence[str]) -> dict[str, list[str]]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        name (str): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """    
    connections = {}
    keys = [k for k in section.keys() if k.endswith(suffixes)]
    for key in keys:
        prefix, suffix = amos.cleave_str(key)
        values = list(amos.iterify(section[key]))
        if prefix == suffix:
            if prefix in connections:
                connections[name].extend(values)
            else:
                connections[name] = values
        else:
            if prefix in connections:
                connections[prefix].extend(values)
            else:
                connections[prefix] = values
    return connections
      
def get_section_designs(
    section: MutableMapping[Hashable, Any],
    name: str) -> dict[str, str]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        name (str): [description]

    Returns:
        dict[str, str]: [description]
        
    """    
    designs = {}
    design_keys = [k for k in section.keys() if k.endswith('design')]
    for key in design_keys:
        prefix, suffix = amos.cleave_str(key)
        if prefix == suffix:
            designs[name] = section[key]
        else:
            designs[prefix] = section[key]
    return designs

def get_section_kinds(    
    section: MutableMapping[Hashable, Any],
    suffixes: Sequence[str]) -> dict[str, str]: 
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (Sequence[str]): [description]

    Returns:
        dict[str, str]: [description]
        
    """         
    kinds = {}
    keys = [k for k in section.keys() if k.endswith(suffixes)]
    for key in keys:
        _, suffix = amos.cleave_str(key)
        values = amos.iterify(section[key])
        if suffix.endswith('s'):
            kind = suffix[:-1]
        else:
            kind = suffix            
        kinds.update(dict.fromkeys(values, kind))
    return kinds    

def create_outline(
    project: interface.Project,
    base: Optional[Type[stages.Outline]] = None, 
    **kwargs) -> stages.Outline:
    """[summary]

    Args:
        project (interface.Project): [description]
        base (Optional[Type[stages.Outline]]): [description]. Defaults to None.

    Returns:
        stages.Outline: [description]
        
    """    
    base = base or project.stages.withdraw(item = 'outline')
    outline = base(project = project, **kwargs)
    return _settings_to_outline(
        settings = project.settings,
        suffixes = project.components.suffixes,
        outline = outline)
    
def create_workflow(
    project: interface.Project,
    base: Optional[Type[stages.Workflow]] = None, 
    **kwargs) -> stages.Workflow:
    """[summary]

    Args:
        project (interface.Project): [description]
        base (Optional[Type[stages.Workflow]]): [description]. Defaults to None.

    Returns:
        stages.Workflow: [description]
        
    """    
    base = base or project.stages.withdraw(item = 'workflow')
    workflow = base(project = project, **kwargs)
    return _outline_to_workflow(
        outline = project.outline,
        library = project.components,
        workflow = workflow)

def create_pipeline(
    name: str,
    project: interface.Project,
    base: Optional[Type[amos.Pipeline]] = None, 
    **kwargs) -> amos.Pipeline:
    """[summary]

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[amos.Pipeline]]): [description]. Defaults to None.

    Returns:
        amos.Pipeline: [description]
          
    """    
    base = base or amos.Pipeline
    return base(contents = project.outline.connections[name], **kwargs)

def create_pipelines(
    name: str,
    project: interface.Project,
    base: Optional[Type[amos.Pipelines]] = None, 
    pipeline_base: Optional[Type[amos.Pipeline]] = None, 
    **kwargs) -> amos.Pipelines:
    """[summary]

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[amos.Pipelines]]): [description]. Defaults to None.

    Returns:
        amos.Pipelines: [description]
          
    """    
    base = base or amos.Pipelines
    pipeline_base = pipeline_base or amos.Pipeline
    pipelines = []
    for connection in project.outline.connections[name]:
        pipelines.append(create_pipeline(
            name = connection, 
            project = project,
            base = pipeline_base))  
    permutations = itertools.product(pipelines)
    return base(contents = permutations, **kwargs)
   
def create_results(
    project: interface.Project,
    base: Optional[Type[stages.Results]] = None, 
    **kwargs) -> stages.Results:
    """[summary]

    Args:
        project (interface.Project): [description]
        base (Optional[Type[stages.Results]]): [description]. Defaults to None.

    Returns:
        stages.Results: [description]
        
    """    
    base = base or project.stages.withdraw(item = 'results')
    results = base(project = project, **kwargs)
    return _workflow_to_results(
        worfklow = project.workflow,
        library = project.components,
        results = results)

""" Private Functions """

def _settings_to_outline(
    settings: amos.Settings,
    suffixes: list[str]) -> dict[Hashable, dict[Hashable, Any]]:
    """[summary]

    Args:
        settings (amos.Settings): [description]
        suffixes (list[str]): [description]

    Returns:
        dict[Hashable, dict[Hashable, Any]]: [description]
    """
    all_suffixes = suffixes + 'parameters'
    return {
        key: value for key, value in settings.items() 
        if any(k.endswith(all_suffixes) for k in value.keys())}

def _outline_to_workflow(
    outline: stages.Outline, 
    library: bases.ProjectLibrary, 
    workflow: stages.Workflow) -> stages.Workflow:
    """[summary]

    Args:
        outline (stages.Outline): [description]
        library (bases.LIBRARY): [description]

    Returns:
        stages.Workflow: [description]
        
    """
    
    components = {}
    for name in outline.labels:
        components[name] = _outline_to_component(
            name = name,
            outline = outline,
            library = library)
    workflow = _outline_to_system(
        outline = outline, 
        components = components,
        system = workflow)
    return workflow 

def _outline_to_component(
    name: str, 
    outline: stages.Outline,
    library: bases.ProjectLibrary) -> bases.ProjectComponent:
    """[summary]

    Args:
        name (str): [description]
        outline (stages.Outline): [description]
        library (bases.ProjectLibrary): [description]

    Returns:
        bases.ProjectComponent: [description]
        
    """    
    design = outline.designs.get(name, None) 
    kind = outline.kinds.get(name, None) 
    lookups = _get_lookups(name = name, design = design, kind = kind)
    base = library.withdraw(item = lookups)
    parameters = amos.get_annotations(item = base)
    attributes, initialization = _parse_initialization(
        outline = outline,
        parameters = parameters)
    initialization['parameters'] = _get_runtime(
        lookups = lookups,
        outline = outline)
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

def _get_runtime(
    lookups: list[str], 
    outline: stages.Outline) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        outline (stages.Outline): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """    
    runtime = {}
    for key in lookups:
        try:
            match = outline.runtime[key]
            runtime[lookups[0]] = match
            break
        except KeyError:
            pass
    return runtime

def _parse_initialization(
    name: str,
    outline: stages.Outline, 
    parameters: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    """[summary]

    Args:
        name (str): [description]
        outline (stages.Outline): [description]
        parameters (list[str]): [description]

    Returns:
        tuple[dict[str, Any], dict[str, Any]]: [description]
        
    """
    if name in outline.initialization:
        attributes = {}
        initialization = {}
        for key, value in outline.initialization[name]: 
            if key in parameters:
                initialization[key] = value
            else:
                attributes[key] = value
        return attributes, initialization
    else:
        return {}, {}  

def _outline_to_system(
    outline: stages.Outline, 
    components: dict[str, bases.ProjectComponent],
    system: stages.Workflow) -> amos.Pipeline:
    """[summary]

    Args:
        outline (stages.Outline): [description]
        components (dict[str, bases.ProjectComponent]): [description]
        system (stages.Workflow): [description]

    Returns:
        stages.Workflow: [description]
        
    """    
    for node in outline.connections.keys():
        component = components[node]
        system = component.integrate(workflow = system)    
    return system

def _workflow_to_results(
    path: Sequence[str],
    project: interface.Project,
    data: Any = None,
    library: bases.ProjectLibrary = None,
    result: stages.Results = None,
    **kwargs) -> object:
    """[summary]

    Args:
        name (str): [description]
        path (Sequence[str]): [description]
        project (interface.Project): [description]
        data (Any, optional): [description]. Defaults to None.
        library (nodes.Library, optional): [description]. Defaults to None.
        result (core.Result, optional): [description]. Defaults to None.

    Returns:
        object: [description]
        
    """    
    library = library or amos.LIBRARY
    result = result or amos.RESULT
    data = data or project.data
    result = result()
    for node in path:
        print('test node in path', node)
        try:
            component = library.instance(name = node)
            result.add(component.execute(project = project, **kwargs))
        except (KeyError, AttributeError):
            pass
    return result
