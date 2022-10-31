"""
research: branching workflow designs
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
    Compare (workers.Research): uses a Research workflow with parallel branches that
        applies crtieria to reduce the number of branches. 
    Observe (workers.Research): uses a Research workflow with parallel branches but
        has no reduction or criteria.  
    Agile (Compare): a dynamic workflow structure that changes direction based 
        on one or more criteria.
    Contest (Compare): evaluates and selects best workflow among several based 
        on one or more criteria.
    Lean (Compare): an iterative workflow that maximizes efficiency based on
        one or more criteria.
    Survey (Compare): averages multiple workflows based on one or more 
        criteria.
        
To Do:

            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import Hashable, MutableMapping, MutableSequence, Set
import contextlib
import dataclasses
import itertools
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING

import amos
import holden

from ..core import framework
from ..core import keystones
from ..core import nodes
from . import tasks
from . import workflows


@dataclasses.dataclass
class Compare(workflows.Research):
    """Workflow that branches and appplies criteria to eliminate branches.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[framework.Project]): related Project instance.
            
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: Optional[framework.Project] = None
    superviser: Optional[tasks.Superviser] = None

    
@dataclasses.dataclass
class Observe(workflows.Research):
    """Workflow that branches but does not reduce.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[framework.Project]): related Project instance.
            
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: Optional[framework.Project] = None
    superviser: Optional[tasks.Superviser] = None
    
    """ Public Methods """
    
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        results = super().implement(item = item, **kwargs)
        project = self.judge.complete(projects = results)  
        return project
     
     
@dataclasses.dataclass
class Compete(Compare):
    """Base class for tests that returns fewer paths from more.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[framework.Project]): related Project instance.
            
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: Optional[framework.Project] = None
    superviser: Optional[tasks.Superviser] = None
    judge: Optional[tasks.Judge] = None

    """ Properties """

    @property
    def graph(self) -> holden.System:
        """Returns direct graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.
            
        """
        graph = super().graph
        endpoints = amos.iterify(graph.endpoint)
        scorer = 'scorer'
        graph.add(scorer)
        for endpoint in endpoints:
            graph.connect(tuple([endpoint, scorer])) 
        return graph
    
    """ Public Methods """
    
    def implement(self, item: Any, **kwargs: Any) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        results = super().implement(item = item, **kwargs)
        project = self.judge.complete(projects = results)  
        return project


@dataclasses.dataclass
class Lean(Compare):
    """Iterative workflow that maximizes efficiency based on criteria.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[framework.Project]): related Project instance.
            
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: Optional[framework.Project] = None
    superviser: Optional[tasks.Superviser] = None
    judge: Optional[tasks.Judge] = None
            

@dataclasses.dataclass
class Survey(Compare):
    """Base class for research that averages results among several paths.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[framework.Project]): related Project instance.
            
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: Optional[framework.Project] = None
    superviser: Optional[tasks.Superviser] = None
    judge: Optional[tasks.Judge] = None

 
    """ Properties """

    @property
    def graph(self) -> holden.System:
        """Returns direct graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.
            
        """
        graph = super().graph
        endpoints = amos.iterify(graph.endpoint)
        averager = 'averager'
        graph.add(averager)
        for endpoint in endpoints:
            graph.connect(tuple([endpoint, averager])) 
        return graph
          