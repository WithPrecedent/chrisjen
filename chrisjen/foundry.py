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
import copy
import itertools
from typing import Any, Optional, Type, TYPE_CHECKING, Union

import amos

from . import nodes

if TYPE_CHECKING:
    from . import base
    from . import components
    from . import base
    

""" Public Functions """

def create_node(
    name: str,
    project: base.Project,
    **kwargs) -> nodes.Component:
    """Creates node based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    design = project.outline.designs.get(name, 'component')
    builder = locals()[f'create_{design}']
    return builder(name = name, project = project, **kwargs)

def create_workflow(
    project: base.Project,
    base: Optional[Type[base.Workflow]] = None, 
    **kwargs) -> base.Workflow:
    """Creates workflow based on 'project' and 'kwargs'.

    Args:
        project (base.Project): [description]
        base (Optional[Type[base.Workflow]]): [description]. Defaults to None.

    Returns:
        base.Workflow: [description]
        
    """    
    base = base or project.base.workflow
    workflow = base(**kwargs)
    worker_names = _get_worker_names(project = project)
    for name in worker_names:
        worker = create_worker(name = name, project = project)
        workflow.append(worker)  
    return workflow    

def create_component(
    name: str,
    project: base.Project,
    base: Optional[str] = None,  
    **kwargs) -> nodes.Component:
    """Creates component based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
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

def create_worker(
    name: str,
    project: base.Project,
    base: Optional[str] = None,  
    **kwargs) -> components.Worker:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
        base (Optional[Type[components.Worker]]): [description]. Defaults to 
            None.

    Returns:
        components.Worker: [description]
        
    """  
    worker = create_component(
        name = name, 
        project = project, 
        base = base,
        **kwargs)
    connections = project.outline.connections[name]
    starting = connections[list[connections.keys()[0]]]
    worker = _finalize_worker(worker = worker, project = project)
    for node in starting:
        component = create_component(name = name)
    return

def create_manager(
    name: str,
    project: base.Project,
    base: Optional[Type[components.Manager]] = None,  
    **kwargs) -> components.Manager:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
        base (Optional[Type[components.Manager]]): [description]. Defaults to 
            None.

    Returns:
        components.Manager: [description]
        
    """ 
    base = base or project.base.node.library['manager']
    return

def create_researcher(
    name: str,
    project: base.Project,
    base: Optional[Type[components.Researcher]] = None,  
    **kwargs) -> components.Researcher:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
        base (Optional[Type[components.Researcher]]): [description]. Defaults to 
            None.

    Returns:
        components.Researcher: [description]
        
    """ 
    base = base or project.base.node.library['researcher']
    section = project.settings[name]
    first_key = list(item.keys())[0]
    self.append(first_key)
    possible = [v for k, v in item.items() if k in item[first_key]]
    combos = list(itertools.product(*possible))
    self.append(combos)
    return components.Experiment

def create_judge(
    name: str,
    project: base.Project,
    base: Optional[Type[components.Judge]] = None,  
    **kwargs) -> components.Judge:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
        base (Optional[Type[components.Judge]]): [description]. Defaults to 
            None.

    Returns:
        components.Judge: [description]
        
    """ 
    base = base or project.base.node.library['judge']
    return

def create_step(
    name: str,
    project: base.Project,
    base: Optional[Type[components.Step]] = None,  
    **kwargs) -> components.Step:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
        base (Optional[Type[components.Step]]): [description]. Defaults to 
            None.

    Returns:
        components.Step: [description]
        
    """ 
    base = base or project.base.node.library['step']
    return   

def create_technique(
    name: str,
    project: base.Project,
    base: Optional[Type[components.Technique]] = None,  
    **kwargs) -> components.Technique:
    """Creates worker based on 'name', 'project', and 'kwargs'.

    Args:
        name (str):
        project (base.Project): [description]
        base (Optional[Type[components.Technique]]): [description]. Defaults to 
            None.

    Returns:
        components.Technique: [description]
        
    """ 
    base = base or project.base.node.library['technique']
    return  
        
def _settings_to_workflow(
    settings: base.Configuration, 
    options: amos.Catalog, 
    workflow: base.Workflow) -> base.Workflow:
    """[summary]

    Args:
        settings (base.Configuration): [description]
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
    settings: base.Configuration,
    options: amos.Catalog) -> base.Projectnodes.Component:
    """[summary]

    Args:
        name (str): [description]
        settings (base.Configuration): [description]
        options (amos.Catalog): [description]

    Returns:
        base.Projectnodes.Component: [description]
        
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
    project: base.Project,
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
    project: base.Project) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        project (base.Project): [description]

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
    project: base.Project,
    **kwargs) -> dict[Hashable, Any]:
    """[summary]

    Args:
        lookups (list[str]): [description]
        project (base.Project): [description]

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
    project: base.Project) -> components.Worker:
    """[summary]

    Args:
        worker (components.Worker): [description]
        project (base.Project): [description]

    Returns:
        components.Worker: [description]
        
    """    
    connections = project.outline.connections[worker.name]
    starting = connections[list[connections.keys()[0]]]
    for node in starting:
        component = create_node(name = node, project = project)
        worker.append(component)
    return worker

def _get_component(
    lookups: list[str], 
    project: base.Project) -> nodes.Component:
    """[summary]

    Args:
        lookups (list[str]): [description]
        project (base.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """    
    return project.base.node.library.withdraw(item = lookups)

def _settings_to_adjacency(
    settings: base.Configuration, 
    components: dict[str, base.Projectnodes.Component],
    system: base.Workflow) -> amos.Pipeline:
    """[summary]

    Args:
        settings (base.Configuration): [description]
        components (dict[str, base.Projectnodes.Component]): [description]
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

# def _get_workflow_structure(project: base.Project) -> amos.Composite:
#     """[summary]

#     Args:
#         project (base.Project): [description]

#     Returns:
#         amos.Composite: [description]
        
#     """
#     try:
#         structure = project.settings[project.name][f'{project.name}_structure']
#     except KeyError:
#         try:
#             structure = project.settings[project.name]['structure']
#         except KeyError:
#             structure = project.base.workflow_structure
#     return amos.Composite.create(structure)