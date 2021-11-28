"""
types: base types of workflow nodes
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
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, MutableSequence, Sequence)
import copy
import dataclasses
import itertools
import multiprocessing
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

from . import bases

if TYPE_CHECKING:
    from . import interface
    

"""
 
Test:
    Distributor (Splitter/Repeater)
    Manager
    
Comparison (Test):
    Distributor (Splitter/Repeater)
    Manager
    Judge

Manager:
    Workers    

"""

@dataclasses.dataclass
class Distributor(bases.Component):
    """Divides or copies passed data for use by later nodes."""
    name: Optional[str] = None
    contents: amos.Pipelines = dataclasses.field(
        default_factory = amos.Pipelines)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)   
 
@dataclasses.dataclass
class Converger(bases.Component):
    """Divides or copies passed data for use by later nodes."""
    name: Optional[str] = None
    contents: amos.Pipelines = dataclasses.field(
        default_factory = amos.Pipelines)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)      
    

@dataclasses.dataclass   
class Test(bases.Component):
    """Same data, different nodes"""
    name: Optional[str] = None
    contents: amos.Pipelines = dataclasses.field(
        default_factory = amos.Pipelines)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)

    @classmethod
    def create(cls, name: str, project: interface.Project) -> Test:
        pass

 
@dataclasses.dataclass   
class Comparison(Test):
    """Same data, different nodes"""
    name: Optional[str] = None
    contents: amos.Pipelines = dataclasses.field(
        default_factory = amos.Pipelines)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)


""" Single Nodes """

@dataclasses.dataclass   
class Judge(object):
    """Reduces paths"""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)

   
@dataclasses.dataclass   
class Contest(Judge):
    """Reduces paths by selecting the best path based on a criteria score."""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)

   
@dataclasses.dataclass   
class Survey(Judge):
    """Reduces paths by averaging the results of a criteria score."""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)


@dataclasses.dataclass   
class Validation(Judge):
    """Reduces paths based on each test meeting a minimum criteria score."""
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)




def create_test(
    name: str, 
    project: interface.Project,
    **kwargs) -> Test:
    """[summary]

    Args:
        name (str): [description]
        project (interface.Project): [description]

    Returns:
        Test: [description]
        
    """    
    design = project.settings.designs.get(name, None) 
    kind = project.settings.kinds.get(name, None) 
    lookups = _get_lookups(name = name, design = design, kind = kind)
    base = project.components.withdraw(item = lookups)
    parameters = amos.get_annotations(item = base)
    attributes, initialization = _parse_initialization(
        name = name,
        settings = project.settings,
        parameters = parameters)
    initialization['parameters'] = _get_runtime(
        lookups = lookups,
        settings = project.settings)
    component = base(name = name, **initialization)
    for key, value in attributes.items():
        setattr(component, key, value)
    return component
