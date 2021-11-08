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
    Outline
    Workflow
    Results
    
"""
from __future__ import annotations
import collections
from collections.abc import (
    Collection, Hashable, Mapping, MutableMapping, Sequence, Set)
import dataclasses
import functools
import itertools
import types
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos
import more_itertools

from . import bases
from . import workshop

if TYPE_CHECKING:
    from . import interface

 
@dataclasses.dataclass
class Outline(amos.Settings, amos.Dictionary):
    """Project workflow implementation as a directed acyclic graph (DAG).
    
    Workflow stores its graph as an adjacency list. Despite being called an 
    "adjacency list," the typical and most efficient way to create one in python
    is using a dict. The keys of the dict are the nodes and the values are sets
    of the hashable summarys of other nodes.
    
    Args:
        contents (MutableMapping[Hashable, Any]): a dict for storing 
            configuration options. Defaults to en empty dict.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty dict.
        default (Mapping[str, Mapping[str]]): any default options that should
            be used when a user does not provide the corresponding options in 
            their configuration settings. Defaults to an empty dict.
        infer_types (bool): whether values in 'contents' are converted to other 
            datatypes (True) or left alone (False). If 'contents' was imported 
            from an .ini file, all values will be strings. Defaults to True.

    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = dict
    project: interface.Project = None

    """ Properties """       
    
    @functools.cached_property
    def connections(self) -> dict[str, list[str]]:
        """Returns raw connections between nodes from 'settings'.

        Returns:
            dict[str, list[str]]: keys are node names and values are lists of
                nodes to which the key node is connection. These connections
                do not include any structure or design.
            
        """
        return workshop.get_connections(project = self.project)

    @functools.cached_property
    def designs(self) -> dict[str, str]:
        """Returns structural designs of nodes based on 'settings'.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        return workshop.get_designs(project = self.project)

    @functools.cached_property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        return workshop.get_initialization(project = self.project)
        
    @functools.cached_property
    def kinds(self) -> dict[str, str]:
        """Returns kinds based on 'settings'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        return workshop.get_kinds(project = self.project)
    
    @functools.cached_property
    def labels(self) -> list[str]:
        """Returns names of nodes based on 'settings'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        return workshop.get_labels(project = self.project)

    @functools.cached_property
    def runtime(self) -> dict[str, dict[str, Any]]:
        """Returns runtime parameters based on 'settings'

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of runtime parameters.
            
        """
        return workshop.get_runtime(project = self.project)
    
    """ Public Methods """
    
    @classmethod
    def create(cls, project: interface.Project) -> Workflow:
        """[summary]

        Args:
            project (interface.Project): [description]

        Returns:
            interface.Project: [description]
            
        """        
        return workshop.create_outline(project = project)

    """ Dunder Methods """

    def __setitem__(self, key: str, value: Mapping[str, Any]) -> None:
        """Creates new key/value pair(s) in a section of the active dictionary.

        Args:
            key (str): name of a section in the active dictionary.
            value (Mapping[str, Any]): the dictionary to be placed in that 
                section.

        Raises:
            TypeError if 'key' isn't a str or 'value' isn't a dict.

        """
        try:
            self.contents[key].update(value)
        except KeyError:
            try:
                self.contents[key] = value
            except TypeError:
                raise TypeError(
                    'key must be a str and value must be a dict type')
        return


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

    """ Public Methods """
    
    @classmethod
    def create(cls, project: interface.Project) -> Workflow:
        """[summary]

        Args:
            project (interface.Project): [description]

        Returns:
            interface.Project: [description]
            
        """        
        return workshop.create_workflow(project = project)

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
    def create(cls, project: interface.Project) -> Results:
        """[summary]

        Args:

        Returns:
            Results: derived from 'item'.
            
        """
        return workshop.create_results(project = project)


def create_outline(
    project: interface.Project,
    base: Optional[Type[Outline]] = None, 
    **kwargs) -> Outline:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        Outline: [description]
        
    """
    base = base or Outline
    return base(project = project, **kwargs)

def create_workflow(
    project: interface.Project,
    base: Optional[Type[Workflow]] = None, 
    **kwargs) -> Workflow:
    """[summary]

    Args:
        project (interface.Project): [description]

    Returns:
        Workflow: [description]
        
    """
    base = base or Workflow
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
        prefix, suffix = amos.divide_string(key)
        if key.startswith(name) or (name == name and prefix == suffix):
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
        prefix, suffix = amos.divide_string(key)
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
        prefix, suffix = amos.divide_string(key)
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
    graph: amos.Graph) -> amos.Graph:
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
           
           
@dataclasses.dataclass
class Outline(amos.Settings, bases.ProjectStage):
    """Organized chrisjen project settings with convenient accessors.

    Args:
        project (Optional[interface.Project]): linked Project which contains
            'settings' and 'nodes' attributes. Defaults to None.

    """
    project: Optional[interface.Project] = None
    
    """ Properties """

    @functools.cached_property
    def attributes(self) -> dict[str, Any]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            other = {}
            for section in self.values():
                other.update(section.other)
            return other
        
    @functools.cached_property
    def connections(self) -> dict[str, list[str]]:
        """[summary]

        Returns:
            dict[str, list[str]]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            return workshop.get_connections(project = self.project)

    @functools.cached_property
    def designs(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            designs = {}
            for section in self.values():
                designs.update(section.designs)
            return designs

    @functools.cached_property 
    def initialization(self) -> dict[str, Any]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            initialization = collections.defaultdict(dict)
            keys = [k.endswith('_parameters') for k in self.keys]
            for key in keys:
                prefix, _ = amos.cleave_str(key)
                initialization[prefix] = self[key]
            return initialization
    
    @functools.cached_property
    def kinds(self) -> dict[str, str]:
        """[summary]

        Returns:
            dict[str, str]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            kinds = dict(zip(self.nodes, self.nodes))
            for section in self.values():
                bases.update(section.bases)
            return bases
    
    @functools.cached_property
    def nodes(self) -> list[str]:
        """[summary]

        Returns:
            list[str]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            key_nodes = list(self.connections.keys())
            value_nodes = list(
                itertools.chain.from_iterable(self.connections.values()))
            return amos.deduplicate(item = key_nodes + value_nodes) 

    @functools.cached_property
    def runtime(self) -> dict[str, Any]:
        """[summary]

        Returns:
            dict[str, dict[str, Any]]: [description]
            
        """
        if self.project is None:
            raise ValueError(
                'Outline must be linked to a project before values can be '
                'returned')
        else:
            return
            
    """ Public Methods """

    def link(self, project: interface.Project) -> None:
        """
        """
        self.project = project
        return self


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
        return create_workflow(item = item, **kwargs)


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
        return create_results(item = item, **kwargs)
    
