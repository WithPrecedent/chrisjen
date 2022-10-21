"""
views: classes and functions related to stages of a chrisjen project
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

        
"""
from __future__ import annotations
import collections
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import dataclasses
import itertools
import pathlib
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Type, Union

import amos
import bobbie
import holden

from . import base


@dataclasses.dataclass
class Outline(base.ProjectKeystone):
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
    suffixes: ClassVar[dict[str, tuple[str]]] = {
        'design': ('design',),
        'director': ('director', 'project'),
        'files': ('filer', 'files', 'clerk'),
        'general': ('general',),
        'parameters': ('parameters',), 
        'workers': ('workers',)}
    
    """ Properties """       
              
    @property
    def clerk(self) -> dict[str, Any]:
        """Returns file settings in a chrisjen project.

        Returns:
            dict[str, Any]: dict of file settings.
            
        """
        for name in self.suffixes['files']:
            try:
                return self[name]
            except KeyError:
                return {} 
          
    @property
    def connections(self) -> dict[str, dict[str, list[str]]]:
        """Returns raw connections between nodes from 'project'.
        
        Returns:
            dict[str, dict[str, list[str]]]: keys are worker names and values 
                node connections for that worker.
            
        """
        suffixes = self.project.factory.plurals
        sections = self.workers
        sections.update({self.project.name: self.director})
        connections = {}
        for name, section in sections.items():
            keys = [k for k in section.keys() if k.endswith(suffixes)]
            if name not in connections:
                connections[name] = {}
            for key in keys:
                prefix, suffix = amos.cleave_str(key)

                values = amos.listify(section[key])
                if prefix == suffix:
                    if name in connections[name]:
                        connections[name][name].extend(values)
                    else:
                        connections[name][name] = values
                else:
                    if prefix in connections[name]:
                        connections[name][prefix].extend(values)
                    else:
                        connections[name][prefix] = values
        return connections
                     
    @property
    def designs(self) -> dict[str, str]:
        """Returns designs of nodes in a chrisjen project.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        designs = {}
        sections = self.workers
        sections.update({self.project.name: self.director})
        for key, section in sections.items():
            design_keys = [
                k for k in section.keys() 
                if k.endswith(self.suffixes['design'])]
            for design_key in design_keys:
                prefix, suffix = amos.cleave_str(design_key)
                if prefix == suffix:
                    designs[key] = section[design_key]
                else:
                    designs[prefix] = section[design_key]
        return designs
                     
    @property
    def director(self) -> dict[str, Any]:
        """Returns director settings of a chrisjen project.

        Returns:
            dict[str, Any]: director settings for a chrisjen project
            
        """
        for name, section in self.project.settings.items():
            if name.endswith(self.suffixes['director']):
                return section
        for name, section in self.project.settings.items():
            suffixes = itertools.chain_from_iterable(self.suffixes.values()) 
            if not name.endswith(suffixes):
                return section
        return {}
     
    @property
    def general(self) -> dict[str, Any]:
        """Returns general settings in a chrisjen project.

        Returns:
            dict[str, Any]: dict of general settings.
            
        """       
        for name in self.suffixes['general']:
            try:
                return self[name]
            except KeyError:
                return {}  
                                    
    @property
    def implementation(self) -> dict[str, dict[str, Any]]:
        """Returns implementation parameters for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the implementation arguments and attributes.
            
        """
        implementation = {}      
        for name, section in self.project.settings.items():
            for suffix in self.suffixes['parameters']:
                if name.endswith(suffix):
                    key = name.removesuffix('_' + suffix)
                    implementation[key] = section
        return implementation
                                                             
    @property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        initialization = {}
        all_plurals = (
            self.project.factory.plurals
            + self.suffixes['design']
            + self.suffixes['director'])
        for key, section in self.workers.items():   
            initialization[key] = {
                k: v for k, v in section.items() if not k.endswith(all_plurals)}
        return initialization
        
    @property
    def kinds(self) -> dict[str, str]:
        """Returns kinds of nodes in 'project'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        kinds = {}
        suffixes = self.project.factory.plurals
        for key, section in self.workers.items():
            new_kinds = {}
            keys = [k for k in section.keys() if k.endswith(suffixes)]
            for key in keys:
                _, suffix = amos.cleave_str(key)
                values = list(amos.iterify(section[key]))
                if values not in [['none'], ['None'], ['NONE']]:
                    if suffix.endswith('s'):
                        kind = suffix[:-1]
                    else:
                        kind = suffix            
                    new_kinds.update(dict.fromkeys(values, kind))
            kinds.update(new_kinds)  
        return kinds
    
    @property
    def labels(self) -> list[str]:
        """Returns names of nodes in 'project'.

        Returns:
            list[str]: names of all nodes that are listed in 'prsettings'.
            
        """
        labels = []    
        for key, section in self.connections.items():
            labels.append(key)
            for inner_key, inner_values in section.items():
                labels.append(inner_key)
                labels.extend(list(itertools.chain(inner_values)))
        return amos.deduplicate_list(item = labels)    
                                  
    @property
    def workers(self) -> dict[str, dict[str, Any]]:
        """Returns worker-related sections of chrisjen project settings.
        
        Any section that does not have a special suffix in 'suffixes' is deemed
        to be a worker-related section.

        Returns:
            dict[str, dict[str, Any]]: workers-related sections of settings.
            
        """
        suffixes = tuple(itertools.chain.from_iterable(self.suffixes.values()))  
        return {
            k: v for k, v in self.project.settings.items()
            if not k.endswith(suffixes)}   
    
     
# @dataclasses.dataclass
# class Workflow(holden.System, base.ProjectKeystone):
#     """Graph view of a chrisjen project workflow.
    
#     Args:
#         project (base.Project): a related project instance which has data
#             from which the properties of an Outline can be derived.
#         contents (MutableMapping[str, Set[str]]): keys are names of nodes and
#             values are sets of names of nodes. Defaults to a defaultdict that 
#             has a set for its value format.
        
#     """
#     project: Optional[Project] = None
#     contents: MutableMapping[Hashable, Set[Hashable]] = (
#         dataclasses.field(
#             default_factory = lambda: collections.defaultdict(set)))
#     nodes: base.ProjectFactory = dataclasses.field(
#         default_factory = base.ProjectFactory)

#     """ Properties """

    
#     """ Public Methods """
    
#     @classmethod
#     def create(cls, project: Project) -> Workflow:
#         """[summary]

#         Args:
#             project (base.Project): [description]

#         Returns:
#             Workflow: [description]
            
#         """        
#         return foundry.create_workflow(project = project, base = cls)    

#     def append_depth(
#         self, 
#         item: MutableMapping[Hashable, MutableSequence[Hashable]]) -> None:
#         """[summary]

#         Args:
#             item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
#                 [description]

#         Returns:
#             [type]: [description]
            
#         """        
#         first_key = list(item.keys())[0]
#         self.append(first_key)
#         for node in item[first_key]:
#             self.append(item[node])
#         return self   
    
#     def append_product(
#         self, 
#         item: MutableMapping[Hashable, MutableSequence[Hashable]]) -> None:
#         """[summary]

#         Args:
#             item (MutableMapping[Hashable, MutableSequence[Hashable]]): 
#                 [description]

#         Returns:
#             [type]: [description]
            
#         """        
#         first_key = list(item.keys())[0]
#         self.append(first_key)
#         possible = [v for k, v in item.items() if k in item[first_key]]
#         combos = list(itertools.product(*possible))
#         self.append(combos)
#         return self

 
# @dataclasses.dataclass
# class Summary(amos.Dictionary):
#     """Reports from completion of a chrisjen project.
    
#     Args:
#         contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
#             to an empty dict.
#         default_factory (Optional[Any]): default value to return or default 
                          
#     """
#     contents: MutableMapping[Hashable, Any] = dataclasses.field(
#         default_factory = dict)
#     default_factory: Optional[Any] = None
    
#     """ Public Methods """

#     @classmethod
#     def create(cls, project: base.Project) -> Summary:
#         """[summary]

#         Args:
#             project (base.Project): [description]

#         Returns:
#             Results: [description]
            
#         """        
#         return workshop.create_results(project = project, base = cls)

#     # def complete(
#     #     self, 
#     #     project: base.Project, 
#     #     **kwargs) -> base.Project:
#     #     """Calls the 'implement' method the number of times in 'iterations'.

#     #     Args:
#     #         project (base.Project): instance from which data needed for 
#     #             implementation should be derived and all results be added.

#     #     Returns:
#     #         base.Project: with possible changes made.
            
#     #     """
#     #     if self.contents not in [None, 'None', 'none']:
#     #         for node in self:
#     #             project = node.complete(project = project, **kwargs)
#     #     return project
    
      
# """ Public Functions """
