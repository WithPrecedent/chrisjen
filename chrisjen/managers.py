"""
managers: composite nodes
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
from . import components
from . import workshop

if TYPE_CHECKING:
    from . import interface
    from . import tasks
    

@dataclasses.dataclass
class Experiment(components.Manager, abc.ABC):
    """Base class for node containing branching and parallel Workers.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (MutableMapping[Hashable, components.Worker]): keys are the 
            names or other identifiers for the stored Worker instances and 
            values are Worker instances. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty bases.Parameters instance.
        proctor (Optional[Distributor]): node for copying, splitting, or
            otherwise creating multiple projects for use by the Workers 
            stored in 'contents'.
                       
    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                          
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, components.Worker] = dataclasses.field(
        default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    proctor: Optional[tasks.Proctor] = None

    """ Public Methods """
    
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> MutableMapping[Hashable, interface.Project]:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            MutableMapping[Hashable, interface.Project]: dict of project 
                instances, with possible changes made.
            
        """
        projects = self.proctor.execute(project = project)
        results = {}
        for i, (key, worker) in enumerate(self.contents.items()):
            results[key] = worker.execute(project = projects[i], **kwargs)
        return results
            

@dataclasses.dataclass
class Comparison(Experiment, abc.ABC):
    """Base class for tests that return one result from a Pipelines.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (MutableMapping[Hashable, components.Worker]): keys are the 
            names or other identifiers for the stored Worker instances and 
            values are Worker instances. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty bases.Parameters instance.
        proctor (Optional[Distributor]): node for copying, splitting, or
            otherwise creating multiple projects for use by the Workers 
            stored in 'contents'.
        judge (Optional[Judge]): node for reducing the set of Workers
            in 'contents' to a single Worker or Node.
                                   
    Attributes:
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
                          
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, components.Worker] = dataclasses.field(
        default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    proctor: Optional[tasks.Proctor] = None
    judge: Optional[tasks.Judge] = None

    """ Public Methods """
    
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        results = super().implement(project = project, **kwargs)
        project = self.judge.execute(projects = results)  
        return project


def create_experiment(
    name: str, 
    project: interface.Project,
    **kwargs) -> Experiment:
    """[summary]

    Args:
        name (str): [description]
        project (interface.Project): [description]

    Returns:
        Experiment: [description]
        
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
