"""
workshop: functions for creating and modifying project-related classes
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
    represent_workflow
    represent_worker
    represent_worker
    represent_judge
    represent_step
    represent_technique
    represent_results

To Do:
    Add support for parallel construction of Results in the 'represent_results'
        function.
        
"""
from __future__ import annotations
from collections.abc import Hashable, MutableMapping, Sequence
import copy
import itertools
from typing import Any, Optional, Type, TYPE_CHECKING, Union

import amos

if TYPE_CHECKING:
    from ..core import keystones
    

""" Public Functions """
         

def represent_node(
    name: str,
    project: framework.Project,
    **kwargs) -> defaults.Component:
    """Creates node based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    design = project.outline.designs.get(name, 'component')
    builder = globals()[f'represent_{design}']
    return builder(name = name, project = project, **kwargs)

def represent_workflow(
    project: framework.Project,
    base: Optional[Type[defaults.Workflow]] = None, 
    **kwargs) -> defaults.Workflow:
    """Creates workflow based on 'project' and 'kwargs'.

    Args:
        project (framework.Project): [description]
        base (Optional[Type[base.Workflow]]): [description]. Defaults to None.

    Returns:
        base.Workflow: [description]
        
    """    
    base = base or project.repository.keystones['workflow']
    workflow = base(project = project, **kwargs)
    worker_names = _get_worker_names(project = project)
    for name in worker_names:
        worker = represent_worker(name = name, project = project)
        workflow.append(worker)  
    return workflow    

def represent_component(
    name: str,
    project: framework.Project,
    base: Optional[str] = None,  
    **kwargs) -> defaults.Component:
    """Creates component based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[components.Worker]]): [description]. Defaults to 
            None.

    Returns:
        nodes.Component: [description]
        
    """  
    # Determines the str names of the class to instance for the component.
    lookups = _get_lookups(name = name, project = project, base = base)
    # Gets the class for the component based on 'lookups'.
    component = _get_component(lookups = lookups, project = project)
    # This check allows users to manually override implementation parameters 
    # from the project settings.
    if 'parameters' in kwargs:
        implementation = kwargs.pop('parameters')
    else:
        implementation = {}
    # Divides initialization parameters in 'project' into those that can be 
    # passed to the new component ('initialization') and those that must be 
    # added as attributes after initialization ('attributes').
    attributes, initialization = _finalize_initializaton(
        lookups = lookups,
        project = project,
        **kwargs)
    if not implementation:
        # If 'parameters' wasn't in kwargs, this tries to find them in 
        # 'project' (and adds them to 'initialization' if found).
        implementation = _finalize_implementation(
            lookups = lookups, 
            project = project)
        if implementation:
            initialization['parameters'] = implementation
    instance = component(**initialization)
    # Adds any attributes found in the project settings to 'instance'.
    for key, value in attributes.items():
        setattr(instance, key, value)
    return instance

def represent_worker(
    name: str,
    project: framework.Project,
    base: Optional[str] = None,  
    **kwargs) -> components.Worker:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[components.Worker]]): [description]. Defaults to 
            None.

    Returns:
        components.Worker: [description]
        
    """  
    worker = represent_component(
        name = name, 
        project = project, 
        base = base,
        **kwargs)
    connections = project.outline.connections[name]
    starting = connections[list[connections.keys()[0]]]
    worker = _finalize_worker(worker = worker, project = project)
    for node in starting:
        component = represent_component(name = name)
    return

def represent_worker(
    name: str,
    project: framework.Project,
    base: Optional[Type[framework.ProjectWorker]] = None,  
    **kwargs) -> framework.ProjectWorker:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[framework.ProjectWorker]]): [description]. Defaults to 
            None.

    Returns:
        framework.ProjectWorker: [description]
        
    """ 
    base = base or project.base.node.library['worker']
    return

def represent_researcher(
    name: str,
    project: framework.Project,
    base: Optional[Type[components.Researcher]] = None,  
    **kwargs) -> components.Researcher:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[components.Researcher]]): [description]. Defaults to 
            None.

    Returns:
        components.Researcher: [description]
        
    """ 
    base = base or project.base.node.library['researcher']
    section = project.idea[name]
    first_key = list(item.keys())[0]
    self.append(first_key)
    possible = [v for k, v in item.items() if k in item[first_key]]
    combos = list(itertools.product(*possible))
    self.append(combos)
    return components.Experiment

def represent_judge(
    name: str,
    project: framework.Project,
    base: Optional[Type[components.Judge]] = None,  
    **kwargs) -> components.Judge:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[components.Judge]]): [description]. Defaults to 
            None.

    Returns:
        components.Judge: [description]
        
    """ 
    base = base or project.base.node.library['judge']
    return

def represent_step(
    name: str,
    project: framework.Project,
    base: Optional[Type[components.Step]] = None,  
    **kwargs) -> components.Step:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[components.Step]]): [description]. Defaults to 
            None.

    Returns:
        components.Step: [description]
        
    """ 
    base = base or project.base.node.library['step']
    return   

def represent_technique(
    name: str,
    project: framework.Project,
    base: Optional[Type[components.Technique]] = None,  
    **kwargs) -> components.Technique:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (framework.Project): [description]
        base (Optional[Type[components.Technique]]): [description]. Defaults to 
            None.

    Returns:
        components.Technique: [description]
        
    """ 
    base = base or project.base.node.library['technique']
    return  

def get_connections(
    project: framework.Project) -> dict[str, dict[str, list[str]]]:
    """[summary]

    Args:
        project (framework.Project): [description]

    Returns:
        dict[str, dict[str, list[str]]]: [description]
        
    """
    suffixes = project.library.plurals
    connections = {}
    for key, section in project.idea.components.items():
        connections[key] = {}
        new_connections = _get_section_connections(
            section = section,
            name = key,
            plurals = suffixes)
        for inner_key, inner_value in new_connections.items():
            if inner_key in connections[key]:
                connections[key][inner_key].extend(inner_value)
            else:
                connections[key][inner_key] = inner_value
    return connections

def get_designs(project: framework.Project) -> dict[str, str]:
    """[summary]

    Args:
        project (framework.Project): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    designs = {}
    for key, section in project.idea.components.items():
        new_designs = _get_section_designs(section = section, name = key)
        designs.update(new_designs)
    return designs
         
def get_implementation(project: framework.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (framework.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    implementation = {}
    for key, section in project.idea.parameters.items():
        new_key = key.removesuffix('_' + defaults._PARAMETERS_SUFFIX)
        implementation[new_key] = section
    return implementation
   
def get_initialization(project: framework.Project) -> dict[str, dict[str, Any]]:
    """[summary]

    Args:
        project (framework.Project): [description]

    Returns:
        dict[str, dict[str, Any]]: [description]
        
    """
    initialization = {}
    for key, section in project.idea.components.items():   
        new_initialization = _get_section_initialization(
            section = section,
            plurals = project.library.plurals)
        initialization[key] = new_initialization
    return initialization
                          
def get_kinds(project: framework.Project) -> dict[str, str]:
    """[summary]

    Args:
        project (framework.Project): [description]

    Returns:
        dict[str, str]: [description]
        
    """
    kinds = {}
    for key, section in project.idea.components.items():
        new_kinds = _get_section_kinds(
            section = section,
            plurals = project.library.plurals)
        kinds.update(new_kinds)  
    return kinds

def get_labels(project: framework.Project) -> list[str]:
    """Returns names of nodes based on 'project.idea'.

    Args:
        project (framework.Project): an instance of Project with 'settings' and
            'connections'.
        
    Returns:
        list[str]: names of all nodes that are listed in 'project.idea'.
        
    """ 
    labels = []
    connections = get_connections(project = project)       
    for key, section in connections.items():
        labels.append(key)
        for inner_key, inner_values in section.items():
            labels.append(inner_key)
            labels.extend(list(itertools.chain(inner_values)))
    return amos.deduplicate_list(item = labels)     

def get_worker_sections(
    project: framework.Project) -> dict[str, dict[Hashable, Any]]: 
    """Returns names of sections containing data for worker creation.

    Args:
        project (framework.Project): [description]

    Returns:
        dict[str, dict[Hashable, Any]]: [description]
        
    """
    suffixes = project.library.plurals
    return {
        k: v for k, v in project.idea.items() 
        if is_worker_section(section = v, suffixes = suffixes)}

def infer_project_name(project: framework.Project) -> Optional[str]:
    """Tries to infer project name from settings contents.
    
    Args:
        project (framework.Project): an instance of Project with 'settings'.
        
    Returns:
        Optional[str]: project name or None, if none is found.
                
    """
    suffixes = project.library.plurals
    name = None    
    for key, section in project.idea.items():
        if (
            key not in ['general', 'files', 'clerk', 'clerk'] 
                and any(k.endswith(suffixes) for k in section.keys())):
            name = key
            break
    return name

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
    return key.endswith('_' + defaults._DESIGN_Library)

def is_parameters(key: str) -> bool:
    """[summary]

    Args:
        key (str): [description]
        suffixes (list[str]): [description]

    Returns:
        bool: [description]
        
    """    
    return key.endswith('_' + defaults._PARAMETERS_Library)
 
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
        k for k in section.keys() 
        if k.endswith(defaults._DESIGN_SUFFIX)]
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
    all_plurals = plurals + tuple([defaults._DESIGN_SUFFIX])
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
        values = list(amos.iterify(section[key]))
        if values not in [['none'], ['None'], ['NONE']]:
            if suffix.endswith('s'):
                kind = suffix[:-1]
            else:
                kind = suffix            
            kinds.update(dict.fromkeys(values, kind))
    return kinds  

def _get_worker_names(project: framework.Project) -> list[str]: 
    """[summary]

    Args:
        project (framework.Project): [description]

    Returns:
        list[str]: [description]
        
    """            
    try:
        return project.outline.workers.pop(project.name)
    except KeyError:
        try:
            return project.outline.workers.pop(project.name + '_workers')
        except KeyError:
            raise KeyError(
                f'Could not find workers for {project.name} in the project '
                f'outline')
        
def _settings_to_workflow(
    settings: defaults.ProjectSettings, 
    options: amos.Catalog, 
    workflow: defaults.Workflow) -> defaults.Workflow:
    """[summary]

    Args:
        settings (framework.ProjectSettings): [description]
        options (amos.Catalog): [description]
        workflow (base.Workflow): [description]

    Returns:
        base.Workflow: [description]
        
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
    settings: defaults.ProjectSettings,
    options: amos.Catalog) -> framework.Projectnodes.Component:
    """[summary]

    Args:
        name (str): [description]
        settings (framework.ProjectSettings): [description]
        options (amos.Catalog): [description]

    Returns:
        framework.Projectnodes.Component: [description]
        
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
    project: framework.Project,
    base: Optional[str] = None) -> list[str]:
    """[summary]

    Args:
        name (str): [description]
        design (Optional[str]): [description]
        kind (Optional[str]): [description]

    Returns:
        list[str]: [description]
        
    """    
    lookups = [name]
    if name in project.outline.designs:
        lookups.append(project.outline.designs[name])
    if name in project.outline.kinds:
        lookups.append(project.outline.kinds[name])
    if base is not None:
        lookups.append(base)
    return lookups

def _finalize_implementation(
    lookups: list[str], 
    project: framework.Project) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        project (framework.Project): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """        
    parameters = {}
    for key in lookups:
        try:
            parameters = copy.deepcopy(project.outline.implementation[key])
            break
        except KeyError:
            pass
    return parameters

def _finalize_initializaton(
    lookups: list[str], 
    project: framework.Project,
    **kwargs) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        project (framework.Project): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """  
    parameters = {}
    for key in lookups:
        try:
            parameters = copy.deepcopy(project.outline.initialization[key])
            break
        except KeyError:
            pass 
    if parameters:
        kwargs_added = parameters
        kwargs_added.update(**kwargs)
    else:
        kwargs_added = kwargs
    component = _get_component(lookups = lookups, project = project)
    needed = amos.get_annotations(item = component)
    attributes = {}
    initialization = {}
    for key, value in kwargs_added.items():
        if key in needed:
            initialization[key] = value
        else:
            attributes[key] = value
    return attributes, initialization 

def _finalize_worker(
    worker: components.Worker,
    project: framework.Project) -> components.Worker:
    """[summary]

    Args:
        worker (components.Worker): [description]
        project (framework.Project): [description]

    Returns:
        components.Worker: [description]
        
    """    
    connections = project.outline.connections[worker.name]
    starting = connections[list[connections.keys()[0]]]
    for node in starting:
        component = represent_node(name = node, project = project)
        worker.append(component)
    return worker

def _get_component(
    lookups: list[str], 
    project: framework.Project) -> defaults.Component:
    """[summary]

    Args:
        lookups (list[str]): [description]
        project (framework.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """    
    return project.base.node.library.withdraw(item = lookups)

def _settings_to_adjacency(
    settings: defaults.ProjectSettings, 
    components: dict[str, framework.Projectnodes.Component],
    system: defaults.Workflow) -> amos.Pipeline:
    """[summary]

    Args:
        settings (framework.ProjectSettings): [description]
        components (dict[str, framework.Projectnodes.Component]): [description]
        system (base.Workflow): [description]

    Returns:
        base.Workflow: [description]
        
    """    
    for node, connects in settings.connections.items():
        component = components[node]
        system = component.integrate(item = system)    
    return system

def _path_to_result(
    path: amos.Pipeline,
    project: framework.Project,
    **kwargs) -> amos.Pipeline:
    """[summary]

    Args:
        path (amos.Pipeline): [description]
        project (framework.Project): [description]

    Returns:
        object: [description]
        
    """
    result = amos.Pipeline()
    for path in project.workflow.paths:
        for node in path:
            result.append(node.complete(project = project, *kwargs))
    return result

# def _get_workflow_structure(project: framework.Project) -> amos.Composite:
#     """[summary]

#     Args:
#         project (framework.Project): [description]

#     Returns:
#         amos.Composite: [description]
        
#     """
#     try:
#         structure = project.idea[project.name][f'{project.name}_structure']
#     except KeyError:
#         try:
#             structure = project.idea[project.name]['structure']
#         except KeyError:
#             structure = project.base.workflow_structure
#     return amos.Composite.create(structure)