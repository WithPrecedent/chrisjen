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
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases
from . import workshop

if TYPE_CHECKING:
    from . import interface

 
@dataclasses.dataclass
class Outline(amos.Dictionary):
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
        return workshop.create_outline(project = project, base = cls)

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
