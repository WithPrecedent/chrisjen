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
    

@dataclasses.dataclass
class Proctor(components.Task, abc.ABC):
    """Base class for making multiple instances of a project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'project'
            passed to the 'execute' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty bases.Parameters instance.
            
    Attributes:
        options (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
    
    """
    name: Optional[str] = None
    contents: Optional[components.Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)   
 
    """ Public Methods """


    
    
@dataclasses.dataclass
class Judge(components.Task):
    """Base class for selecting a node or path.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (bases.Criteria]): stored criteria to be used to select from 
            several nodes or paths. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty bases.Parameters instance.
            
    Attributes:
        options (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
    
    """
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)      
    

@dataclasses.dataclass
class Test(components.Manager, abc.ABC):
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
        options (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
                          
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, components.Worker] = dataclasses.field(
        default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    proctor: Optional[Proctor] = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def test(
        self,
        project: interface.Project, 
        **kwargs) -> dict[str, interface.Project]:
        """Returns multiple instances of 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            dict[str, interface.Project]: a dict of Project isntances. 
            
        """
        pass
    
    
@dataclasses.dataclass
class Comparison(Test, abc.ABC):
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
        combiner (Optional[Combine]): node for reducing the set of Workers
            in 'contents' to a single Worker or Node.
                                   
    Attributes:
        options (ClassVar[amos.Catalog]): subclasses stored with str keys 
            derived from the 'amos.get_name' function.
                          
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, components.Worker] = dataclasses.field(
        default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    proctor: Optional[Proctor] = None
    judge: Optional[Judge] = None

    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def evaluate(
        self, 
        projects: dict[str, interface.Project], 
        **kwargs) -> interface.Project:
        """Returns one project instance among 'projects'.
        
        Args:
            projects (dict[str, interface.Project]): dict of Project instances
                from which this method should select one.

        Returns:
            interface.Project: selected project, with possible changes made. 
            
        """
        pass    


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
