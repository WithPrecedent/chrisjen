"""
workshop: functions for creating and modifying project-related classes
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
    create_workflow
    create_worker
    create_manager
    create_judge
    create_step
    create_technique
    create_results

To Do:
    Add support for parallel construction of Results in the 'create_results'
        function.
        
"""
from __future__ import annotations
from collections.abc import Hashable, MutableMapping, Sequence
import itertools
from typing import Any, Optional, Type, TYPE_CHECKING, Union

import amos

from . import configuration

if TYPE_CHECKING:
    from . import bases
    from . import components
    from . import interface
    

""" Public Functions """

def create_putline(
    project: interface.Project,
    base: Optional[Type[bases.Outline]] = None, 
    **kwargs) -> bases.Outline:
    """Creates workflow based on 'project' and 'kwargs'.

    Args:
        project (interface.Project): [description]
        base (Optional[Type[bases.Outline]]): [description]. Defaults to None.

    Returns:
        bases.Outline: [description]
        
    """    
    base = base or project.bases.outline
    return base(project = project, **kwargs)
    
def create_workflow(
    project: interface.Project,
    base: Optional[Type[bases.Workflow]] = None, 
    **kwargs) -> bases.Workflow:
    """Creates workflow based on 'project' and 'kwargs'.

    Args:
        project (interface.Project): [description]
        base (Optional[Type[bases.Workflow]]): [description]. Defaults to None.

    Returns:
        bases.Workflow: [description]
        
    """    
    base = base or project.bases.workflow
    workflow = base(**kwargs)
    return _settings_to_workflow(
        settings = project.settings,
        options = project.options,
        workflow = workflow)

def create_worker(
    name: str,
    project: interface.Project,
    base: Optional[Type[components.Worker]] = None,  
    **kwargs) -> components.Worker:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[components.Worker]]): [description]. Defaults to 
            None.

    Returns:
        components.Worker: [description]
        
    """  
    base = base or project.bases.node.options['worker']
    return

def create_manager(
    name: str,
    project: interface.Project,
    base: Optional[Type[components.Manager]] = None,  
    **kwargs) -> components.Manager:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[components.Manager]]): [description]. Defaults to 
            None.

    Returns:
        components.Manager: [description]
        
    """ 
    base = base or project.bases.node.options['manager']
    return

def create_judge(
    name: str,
    project: interface.Project,
    base: Optional[Type[components.Judge]] = None,  
    **kwargs) -> components.Judge:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[components.Judge]]): [description]. Defaults to 
            None.

    Returns:
        components.Judge: [description]
        
    """ 
    base = base or project.bases.node.options['judge']
    return

def create_step(
    name: str,
    project: interface.Project,
    base: Optional[Type[components.Step]] = None,  
    **kwargs) -> components.Step:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[components.Step]]): [description]. Defaults to 
            None.

    Returns:
        components.Step: [description]
        
    """ 
    base = base or project.bases.node.options['step']
    return   

def create_technique(
    name: str,
    project: interface.Project,
    base: Optional[Type[components.Technique]] = None,  
    **kwargs) -> components.Technique:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (interface.Project): [description]
        base (Optional[Type[components.Technique]]): [description]. Defaults to 
            None.

    Returns:
        components.Technique: [description]
        
    """ 
    base = base or project.bases.node.options['technique']
    return  

def get_connections(project: interface.Project) -> dict[str, list[str]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """
    suffixes = project.options.plurals
    connections = {}
    for key, section in project.settings.workers.items():
        new_connections = _get_section_connections(
            section = section,
            name = key,
            plurals = suffixes)
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
    for key, section in project.settings.components.items():
        new_designs = _get_section_designs(section = section, name = key)
        designs.update(new_designs)
    return designs
         
def get_implementation(project: interface.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    implementation = {}
    for key, section in project.settings.parameters.items():
        new_key = amos.drop_suffix_from_str(
            item = key, 
            suffix = configuration._PARAMETERS_SUFFIX)
        implementation[new_key] = section
    return implementation
   
def get_initialization(project: interface.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    initialization = {}
    for key, section in project.settings.components.items():   
        new_initialization = _get_section_initialization(
            section = section,
            plurals = project.options.plurals)
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
    for key, section in project.settings.components.items():
        new_kinds = _get_section_kinds(
            section = section,
            plurals = project.options.plurals)
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
    connections = get_connections(project = project)       
    key_nodes = list(connections.keys())
    value_nodes = list(itertools.chain.from_iterable(connections.values()))
    all_nodes = key_nodes + value_nodes
    return amos.deduplicate_list(item = all_nodes)     

def get_worker_sections(
    project: interface.Project) -> dict[str, dict[Hashable, Any]]: 
    """Returns names of sections containing data for worker creation.

    Args:
        project (interface.Project): [description]

    Returns:
        dict[str, dict[Hashable, Any]]: [description]
        
    """
    suffixes = project.options.plurals
    return {
        k: v for k, v in project.settings.items() 
        if is_worker_section(section = v, suffixes = suffixes)}

def is_worker_section(
    section: MutableMapping[Hashable, Any], 
    suffixes: tuple[str, ...]) -> bool:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        suffixes (tuple[str, ...]): [description]

    Returns:
        bool: [description]
        
    """ 
    return any(
        is_connections(key = k, suffixes = suffixes) for k in section.keys())

def is_connections(key: str, suffixes: tuple[str, ...]) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (tuple[str, ...]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith(suffixes)

def is_design(key: str) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (list[str]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith(configuration._DESIGN_SUFFIX)

def is_parameters(key: str) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (list[str]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith(configuration._PARAMETERS_SUFFIX)
 
""" Private Functions """
 
def _get_section_connections(
    section: MutableMapping[Hashable, Any],
    name: str,
    plurals: Sequence[str]) -> dict[str, list[str]]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        name (str): [description]
        plurals (Sequence[str]): [description]

    Returns:
        dict[str, list[str]]: [description]
        
    """    
    connections = {}
    keys = [
        k for k in section.keys() 
        if is_connections(key = k, suffixes = plurals)]
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

def _get_section_designs(
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
    design_keys = [
        k for k in section.keys() if k.endswith(configuration._DESIGN_SUFFIX)]
    for key in design_keys:
        prefix, suffix = amos.cleave_str(key)
        if prefix == suffix:
            designs[name] = section[key]
        else:
            designs[prefix] = section[key]
    return designs
     
def _get_section_initialization(
    section: MutableMapping[Hashable, Any],
    plurals: Sequence[str]) -> dict[str, Any]:
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        plurals (Sequence[str]): [description]

    Returns:
        dict[str, Any]: [description]
        
    """
    all_plurals = plurals + tuple(configuration._DESIGN_SUFFIX, )
    return {
        k: v for k, v in section.items() if not k.endswith(all_plurals)}

def _get_section_kinds(    
    section: MutableMapping[Hashable, Any],
    plurals: Sequence[str]) -> dict[str, str]: 
    """[summary]

    Args:
        section (MutableMapping[Hashable, Any]): [description]
        plurals (Sequence[str]): [description]

    Returns:
        dict[str, str]: [description]
        
    """         
    kinds = {}
    keys = [k for k in section.keys() if k.endswith(plurals)]
    for key in keys:
        _, suffix = amos.cleave_str(key)
        values = amos.iterify(section[key])
        if suffix.endswith('s'):
            kind = suffix[:-1]
        else:
            kind = suffix            
        kinds.update(dict.fromkeys(values, kind))
    return kinds  

def _infer_project_name(project: interface.Project) -> Optional[str]:
    """Tries to infer project name from settings contents.
    
    Args:
        project (interface.Project): an instance of Project with 'settings'.
        
    Returns:
        Optional[str]: project name or None, if none is found.
                
    """
    suffixes = project.options.plurals
    name = None    
    for key, section in project.settings.items():
        if (
            key not in ['general', 'files', 'filer', 'clerk'] 
                and any(k.endswith(suffixes) for k in section.keys())):
            name = key
            break
    return name

def _settings_to_workflow(
    settings: configuration.ProjectSettings, 
    options: amos.Catalog, 
    workflow: bases.Workflow) -> bases.Workflow:
    """[summary]

    Args:
        settings (configuration.ProjectSettings): [description]
        options (amos.Catalog): [description]
        workflow (bases.Workflow): [description]

    Returns:
        bases.Workflow: [description]
        
    """    
    composites = {}
    for name in settings.composites:
        composites[name] = _settings_to_composite(
            name = name,
            settings = settings,
            options = options)
    workflow = _settings_to_adjacency(
        settings = settings, 
        components = components,
        system = workflow)
    return workflow 

def _settings_to_composite(
    name: str, 
    settings: configuration.ProjectSettings,
    options: amos.Catalog) -> bases.Projectbases.Component:
    """[summary]

    Args:
        name (str): [description]
        settings (configuration.ProjectSettings): [description]
        options (amos.Catalog): [description]

    Returns:
        bases.Projectbases.Component: [description]
        
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
    initialization['parameters'] = _get_implementation(
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

def _get_implementation(
    lookups: list[str], 
    settings: configuration.ProjectSettings) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        settings (configuration.ProjectSettings): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """    
    implementation = {}
    for key in lookups:
        try:
            match = settings.implementation[key]
            implementation[lookups[0]] = match
            break
        except KeyError:
            pass
    return implementation

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
    components: dict[str, bases.Projectbases.Component],
    system: bases.Workflow) -> amos.Pipeline:
    """[summary]

    Args:
        settings (configuration.ProjectSettings): [description]
        components (dict[str, bases.Projectbases.Component]): [description]
        system (bases.Workflow): [description]

    Returns:
        bases.Workflow: [description]
        
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

# def _get_workflow_structure(project: interface.Project) -> amos.Composite:
#     """[summary]

#     Args:
#         project (interface.Project): [description]

#     Returns:
#         amos.Composite: [description]
        
#     """
#     try:
#         structure = project.settings[project.name][f'{project.name}_structure']
#     except KeyError:
#         try:
#             structure = project.settings[project.name]['structure']
#         except KeyError:
#             structure = project.bases.workflow_structure
#     return amos.Composite.create(structure)