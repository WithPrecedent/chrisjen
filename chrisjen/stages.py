"""
stages: classes related to the different stages of a chrisjen project
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
    Outline
    Workflow
    Results
    
"""
from __future__ import annotations
import collections
from collections.abc import Collection, Hashable, MutableMapping, Set
import dataclasses
import itertools
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases
from . import workshop

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass
class Outline(amos.Dictionary, bases.ProjectStage):
    """Organized chrisjen project settings with convenient accessors.

    Args:
        contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
            to an empty dict.
        default_factory (Optional[Any]): default value to return or default 
            function to call when the 'get' method is used. Defaults to None. 

    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = None
    
    """ Properties """
    
    @property
    def bases(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        bases = dict(zip(self.nodes, self.nodes))
        for section in self.values():
            bases.update(section.bases)
        return bases
    
    @property
    def connections(self) -> dict[str, list[str]]:
        """[summary]

        Returns:
            dict[str, list[str]]: [description]
            
        """
        connections = {}
        for section in self.values():
            for key, links in section.connections.items():
                if key in connections:
                    connections[key].extend(links)
                else:
                    connections[key] = links
        return connections

    @property
    def designs(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        designs = {}
        for section in self.values():
            designs.update(section.designs)
        return designs

    @property 
    def initialization(self) -> dict[str, Any]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        initialization = collections.defaultdict(dict)
        keys = [k.endswith('_parameters') for k in self.keys]
        for key in keys:
            prefix, _ = amos.cleave_str(key)
            initialization[prefix] = self[key]
        return initialization

    @property
    def nodes(self) -> list[str]:
        """[summary]

        Returns:
            list[str]: [description]
            
        """
        key_nodes = list(self.connections.keys())
        value_nodes = list(
            itertools.chain.from_iterable(self.connections.values()))
        return amos.deduplicate(item = key_nodes + value_nodes) 

    @property
    def other(self) -> dict[str, Any]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        other = {}
        for section in self.values():
            other.update(section.other)
        return other
    
    """ Public Methods """

    @classmethod
    def from_settings(cls, item: bases.SETTINGS, **kwargs) -> Outline:
        """[summary]

        Args:

        Returns:
            Outline: derived from 'settings'.
            
        """
        return settings_to_outline(item = item, **kwargs)


@dataclasses.dataclass
class Workflow(amos.System, bases.ProjectStage):
    """Project workflow implementation as a directed acyclic graph (DAG).
    
    Workflow stores its graph as an adjacency list. Despite being called an 
    "adjacency list," the typical and most efficient way to create one in python
    is using a dict. The keys of the dict are the nodes and the values are sets
    of the hashable summarys of other nodes.
    
    Args:
        contents (MutableMapping[amos.Node, Set[amos.Node]]): keys 
            are nodes and values are sets of nodes (or hashable representations 
            of nodes). Defaults to a defaultdict that has a set for its value 
            format.
                  
    """  
    contents: MutableMapping[amos.Node, Set[amos.Node]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    
    """ Properties """
    
    @property
    def cookbook(self) -> amos.Pipelines:
        """Returns stored graph as pipelines."""
        return self.pipelines
    
    """ Public Methods """

    @classmethod
    def from_outline(cls, item: Outline, **kwargs) -> Workflow:
        """[summary]

        Args:

        Returns:
            Workflow: derived from 'item'.
            
        """
        return outline_to_workflow(item = item, **kwargs)


@dataclasses.dataclass
class Results(amos.System, bases.ProjectStage):
    """Project workflow after it has been implemented.
    
    Args:
        contents (MutableMapping[amos.Node, Set[amos.Node]]): keys 
            are nodes and values are sets of nodes (or hashable representations 
            of nodes). Defaults to a defaultdict that has a set for its value 
            format.
                  
    """  
    contents: MutableMapping[amos.Node, Set[amos.Node]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))

    """ Public Methods """

    @classmethod
    def from_workflow(cls, item: Workflow, **kwargs) -> Results:
        """[summary]

        Args:

        Returns:
            Results: derived from 'item'.
            
        """
        return workflow_to_results(item = item, **kwargs)
    

def create_outline(project: interface.Project) -> Outline:
    return settings_to_outline(
        settings = project.settings,
        library = project.library)

def settings_to_outline(
    settings: bases.SETTINGS, 
    library: bases.LIBRARY, 
    base: Optional[Type[Any]] = None,
    **kwargs) -> Outline:
    """[summary]

    Args:
        settings (bases.Settings): [description]

    Returns:
        Outline: derived from 'settings'.
        
    """
    base = base or Outline
    suffixes = library.suffixes
    outline = base(**kwargs)
    for name, section in settings.items():
        if any(k.endswith(suffixes) for k in section.keys()):
            outline[name] = section
    return outline
    
def create_workflow(project: interface.Project, **kwargs) -> Workflow:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        Workflow: [description]
        
    """
    workflow = outline_to_workflow(
        outline = project.outline,
        library = project.library,
        **kwargs)
    return workflow

def outline_to_workflow(
    outline: Outline, 
    library: bases.LIBRARY, 
    base: Optional[Type[Any]] = None,
    **kwargs) -> Workflow:
    """[summary]

    Args:
        outline (Outline): [description]
        library (bases.LIBRARY): [description]

    Returns:
        Workflow: [description]
        
    """
    base = base or Workflow
    components = {}
    for name in outline.keys():
        components[name] = outline_to_component(
            name = name,
            outline = outline,
            library = library)
    workflow = outline_to_system(
        outline = outline, 
        components = components,
        **kwargs)
    return workflow 

def outline_to_component(
    name: str, 
    outline: Outline,
    library: bases.LIBRARY, 
    **kwargs) -> bases.NODE:
    """[summary]

    Args:

    Returns:
        bases.NODE: [description]
    
    """
    design = outline.designs[name] or None
    initialization = outline_to_initialization(
        name = name, 
        design = design,
        outline = outline)
    initialization.update(kwargs)
    if 'parameters' not in initialization:
        initialization['parameters'] = outline_to_implementation(
            name = name, 
            design = design,
            outline = outline)
    component = library.instance(name = [name, design], **initialization)
    return component

def outline_to_initialization(
    name: str, 
    outline: Outline,
    library: bases.LIBRARY, 
    **kwargs) -> bases.NODE:
    """Gets parameters for a specific Component from 'outline'.

    Args:

    Returns:
        dict[Hashable, Any]: [description]
        
    """
    suboutline = outline[name]
    parameters = library.parameterify(name = [name, design])
    possible = tuple(i for i in parameters if i not in ['name', 'contents'])
    parameter_keys = [k for k in suboutline.keys() if k.endswith(possible)]
    kwargs = {}
    for key in parameter_keys:
        prefix, suffix = chrisjen.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            kwargs[suffix] = suboutline[key]
    return kwargs  
       
def outline_to_parameters(
    name: str, 
    outline: Outline,
    library: bases.LIBRARY, 
    base: Optional[Type[Any]] = None,
    **kwargs) -> bases.PARAMETERS:
    """Gets parameters for a specific Component from 'outline'.

    Args:


    Returns:
        dict[Hashable, Any]: [description]
        
    """
    base = base or bases.PARAMETERS

    parameters = base(name = name)
    suboutline = outline[section]
    parameters = library.parameterify(name = [name, design])
    possible = tuple(i for i in parameters if i not in ['name', 'contents'])
    parameter_keys = [k for k in suboutline.keys() if k.endswith(possible)]
    kwargs = {}
    for key in parameter_keys:
        prefix, suffix = chrisjen.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            kwargs[suffix] = suboutline[key]
    return kwargs  

def outline_to_system(outline: Outline) -> Workflow:
    """[summary]

    Args:
        outline (Outline): [description]
        library (nodes.Library, optional): [description]. Defaults to None.
        connections (dict[str, list[str]], optional): [description]. Defaults 
            to None.

    Returns:
        chrisjen.structures.Graph: [description]
        
    """    
    connections = connections or outline_to_connections(
        outline = outline, 
        library = library)
    graph = chrisjen.structures.Graph()
    for node in connections.keys():
        kind = library.classify(component = node)
        method = locals()[f'finalize_{kind}']
        graph = method(
            node = node, 
            connections = connections,
            library = library, 
            graph = graph)     
    return graph

def outline_to_initialization(
    name: str, 
    section: str,
    design: str,
    outline: Outline,
    library: nodes.Library) -> dict[Hashable, Any]:
    """Gets parameters for a specific Component from 'outline'.

    Args:
        name (str): [description]
        section (str): [description]
        design (str): [description]
        outline (Outline): [description]
        library (nodes.Library): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """
    suboutline = outline[section]
    parameters = library.parameterify(name = [name, design])
    possible = tuple(i for i in parameters if i not in ['name', 'contents'])
    parameter_keys = [k for k in suboutline.keys() if k.endswith(possible)]
    kwargs = {}
    for key in parameter_keys:
        prefix, suffix = chrisjen.tools.divide_string(key)
        if key.startswith(name) or (name == section and prefix == suffix):
            kwargs[suffix] = suboutline[key]
    return kwargs  
        
def outline_to_implementation(
    name: str, 
    design: str,
    outline: Outline) -> dict[Hashable, Any]:
    """[summary]

    Args:
        name (str): [description]
        design (str): [description]
        outline (Outline): [description]

    Returns:
        dict[Hashable, Any]: [description]
        
    """
    try:
        parameters = outline[f'{name}_parameters']
    except KeyError:
        try:
            parameters = outline[f'{design}_parameters']
        except KeyError:
            parameters = {}
    return parameters

def finalize_serial(
    node: str,
    connections: dict[str, list[str]],
    library: nodes.Library,
    graph: chrisjen.structures.Graph) -> chrisjen.structures.Graph:
    """[summary]

    Args:
        node (str): [description]
        connections (dict[str, list[str]]): [description]
        library (nodes.Library): [description]
        graph (chrisjen.structures.Graph): [description]

    Returns:
        chrisjen.structures.Graph: [description]
        
    """    
    connections = _serial_order(
        name = node, 
        connections = connections)
    nodes = list(more_itertools.collapse(connections))
    if nodes:
        amos.extend(nodes = nodes)
    return graph      

def _serial_order(
    name: str,
    connections: dict[str, list[str]]) -> list[Hashable]:
    """[summary]

    Args:
        name (str): [description]
        directive (core.Directive): [description]

    Returns:
        list[Hashable]: [description]
        
    """   
    organized = []
    components = connections[name]
    for item in components:
        organized.append(item)
        if item in connections:
            organized_connections = []
            connections = _serial_order(
                name = item, 
                connections = connections)
            organized_connections.append(connections)
            if len(organized_connections) == 1:
                organized.append(organized_connections[0])
            else:
                organized.append(organized_connections)
    return organized   


""" Workflow Executing Functions """

def workflow_to_summary(project: interface.Project, **kwargs) -> interface.Project:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        nodes.Component: [description]
        
    """
    # summary = None
    # print('test workflow', project.workflow)
    # print('test paths', project.workflow.paths)
    # print('test parser contents', library.instances['parser'].contents)
    # print('test parser paths', library.instances['parser'].paths)
    summary = amos.SUMMARY()
    print('test project paths', project.workflow.paths)
    # for path in enumerate(project.workflow.paths):
    #     name = f'{summary.prefix}_{i + 1}'
    #     summary.add({name: workflow_to_result(
    #         path = path,
    #         project = project,
    #         data = project.data)})
    return summary
        
def workflow_to_result(
    path: Sequence[str],
    project: interface.Project,
    data: Any = None,
    library: nodes.Library = None,
    result: core.Result = None,
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
