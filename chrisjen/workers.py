"""
components: project workflow nodes and related classes
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
    amos.Library
    Parameters
    Worker
    Laborer
    Manager
    Contest
    Study
    Survey
    Task
    Step
    Technique
    
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
import more_itertools

from . import bases

if TYPE_CHECKING:
    from . import interface

  
@dataclasses.dataclass   
class Test(bases.Manager):
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

@dataclasses.dataclass
class Contest(bases.Manager):
    """Resolves a parallel workflow by selecting the best option.

    It resolves a parallel workflow based upon criteria in 'contents'
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a bases.Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of bases.Component. 
                          
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None
 
    
@dataclasses.dataclass
class Study(bases.Manager):
    """Allows parallel workflow to continue

    A Study might be wholly passive or implement some reporting or alterations
    to all parallel workflows.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a bases.Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of bases.Component. 
                        
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None
  
    
@dataclasses.dataclass
class Survey(bases.Manager):
    """Resolves a parallel workflow by averaging.

    It resolves a parallel workflow based upon the averaging criteria in 
    'contents'
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        criteria (Union[Callable, str]): algorithm to use to resolve the 
            parallel branches of the workflow or the name of a bases.Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of bases.Component. 
                            
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None


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
    return base(contents = project.settings.connections[name], **kwargs)

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
    for connection in project.settings.connections[name]:
        pipelines.append(create_pipeline(
            name = connection, 
            project = project,
            base = pipeline_base))  
    permutations = itertools.product(pipelines)
    return base(contents = permutations, **kwargs)


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
