"""
base: base classes for a chrisjen project
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


To Do:

            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import contextlib
import dataclasses
from email.policy import default
import inspect
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union
import warnings

import amos
import bobbie
import holden
import miller


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
        'parameters': ('parameters',)}
    
    """ Properties """       

    @property
    def connections(self) -> dict[str, dict[str, list[str]]]:
        """Returns raw connections between nodes from 'project'.
        
        Returns:
            dict[str, dict[str, list[str]]]: keys are worker names and values 
                node connections for that worker.
            
        """
        suffixes = self.project.library.plurals
        connections = {}
        for name, section in self.workers.items():
            new_connections = {}
            keys = [k for k in section.keys() if k.endswith(suffixes)]
            for key in keys:
                prefix, suffix = amos.cleave_str(key)
                values = list(amos.iterify(section[key]))
                if prefix == suffix:
                    if prefix in new_connections:
                        new_connections[name].extend(values)
                    else:
                        new_connections[name] = values
                else:
                    if prefix in new_connections:
                        new_connections[prefix].extend(values)
                    else:
                        new_connections[prefix] = values
            for inner_key, inner_value in new_connections.items():
                if inner_key in connections[key]:
                    connections[key][inner_key].extend(inner_value)
                else:
                    connections[key][inner_key] = inner_value
        return connections
                     
    @property
    def designs(self) -> dict[str, str]:
        """Returns designs of nodes in a chrisjen project.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        designs = {}
        for key, section in self.workers.items():
            new_designs = {}
            design_keys = [
                k for k in section.keys() 
                if k.endswith(self.suffixes['design'])]
            for key in design_keys:
                prefix, suffix = amos.cleave_str(key)
                if prefix == suffix:
                    new_designs[key] = section[key]
                else:
                    new_designs[prefix] = section[key]
            designs.update(new_designs)
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
        return {}
              
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
            self.project.library.plurals
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
        suffixes = self.project.library.plurals
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
            dict[str, dict[str, Any]]: node-related sections of settings.
            
        """
        suffixes = itertools.chain_from_iterable(self.suffixes.values())
        worker_sections = {}       
        for name, section in self.project.settings.items():
            if not name.endswith(suffixes):
                worker_sections[name] = section
        return worker_sections   
    
     
@dataclasses.dataclass
class Workflow(holden.System, base.ProjectKeystone):
    """Graph view of a chrisjen project workflow.
    
    Args:
        project (base.Project): a related project instance which has data
            from which the properties of an Outline can be derived.
        contents (MutableMapping[str, Set[str]]): keys are names of nodes and
            values are sets of names of nodes. Defaults to a defaultdict that 
            has a set for its value format.
        
    """
    project: base.Project
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    nodes: base.ProjectLibrary = dataclasses.field(
        default_factory = base.ProjectLibrary)

    """ Properties """

    
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
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[ProjectKeystone]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[ProjectKeystone]): a filing clerk for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        director (Optional[ProjectKeystone]): constructor for a chrisjen 
            project. Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None.   
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
        library (ClassVar[ProjectLibrary]): library of nodes for executing a
            chrisjen project. 
    
    """
    name: Optional[str] = None
    settings: Optional[bobbie.Settings] = None
    clerk: Optional[base.ProjectKeystone] = None
    director: Optional[ProjectKeystone] = None
    identification: Optional[str] = None
    automatic: Optional[bool] = True
    library: ClassVar[ProjectLibrary] = ProjectLibrary()
        
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self._validate_director()
       
    """ Public Class Methods """

    @classmethod
    def create(
        cls, 
        settings: Union[pathlib.Path, str, bobbie.Settings],
        **kwargs) -> Project:
        """Returns a Project instance based on 'settings' and kwargs.

        Args:
            settings (Union[pathlib.Path, str, bobbie.Settings]): a path to a 
                file containing configuration settings or a Settings instance.

        Returns:
            Project: an instance based on 'settings' and kwargs.
            
        """        
        return cls(settings = settings, **kwargs)   
    
    """ Private Methods """
    
    def _validate_director(self) -> None:
        """Creates or validates 'self.director'."""
        if self.director is None:
            self.director = ProjectKeystone.keystones['director']
        elif isinstance(self.director, str):
            self.director = ProjectKeystone.keystones[self.director]
        if inspect.isclass(self.director):
            self.director = self.director(project = self)
        else:
            self.director.project = self
        return
    
    """ Dunder Methods """
    
    def __getattr__(self, item: str) -> Any:
        """Checks 'director' for attribute named 'item'.

        Args:
            item (str): name of attribute to check.

        Returns:
            Any: contents of director attribute named 'item'.
            
        """
        try:
            return getattr(self.director, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project or its manager')
 