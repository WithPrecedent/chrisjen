"""
nodes: core nodes in chrisjen project
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
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

import amos
import holden
import miller

from ..core import base


@dataclasses.dataclass    
class Parameters(amos.Dictionary, base.ProjectKeystone):
    """Creates and stores parameters for part of a chrisjen project.
    
    The use of Parameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the contents of the
    'contents' attribute into an ordinary set of kwargs. In this way, it can 
    serve as a drop-in replacement for a dict that would ordinarily be used for 
    accumulating keyword arguments.
    
    If a chrisjen class uses a Parameters instance, the 'finalize' method should 
    be called before that instance's 'implement' method in order for each of the 
    parameter types to be incorporated.
    
    Args:
        contents (Mapping[str, Any]): keyword parameters for use by a chrisjen
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. To properly match 
            parameters in a Settings instance, 'name' should be the prefix to 
            "_parameters" as a section name in a Settings instance. Defaults to 
            None. 
        default (Mapping[str, Any]): default parameters that will be used if 
            they are not overridden. Defaults to an empty dict.
        implementation (Mapping[str, str]): parameters with values that can only 
            be determined at runtime due to dynamic nature of chrisjen and its 
            workflows. The keys should be the names of the parameters and the 
            values should be attributes or items in 'contents' of 'project' 
            passed to the 'finalize' method. Defaults to an emtpy dict.
        selected (MutableSequence[str]): an exclusive list of parameters that 
            are allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in an Outline instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: Optional[str] = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(
        default_factory = dict)
    selected: MutableSequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, item: Any, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            item (Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting amos.
        parameters = self.default
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(item = item))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(item = item))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Adds any passed kwargs, which will override any other parameters.
        parameters.update(kwargs)
        # Limits parameters to those in 'selected'.
        if self.selected:
            parameters = {k: parameters[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_settings(self, project: base.Project) -> dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            project (base.Project): project has parameters from settings.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        try:
            parameters = project.implementation[self.name]
        except KeyError:
            try:
                parameters = item.settings[f'{self.name}_parameters']
            except KeyError:
                suffix = self.name.split('_')[-1]
                prefix = self.name[:-len(suffix) - 1]
                try:
                    parameters = item.settings[f'{prefix}_parameters']
                except KeyError:
                    try:
                        parameters = item.settings[f'{suffix}_parameters']
                    except KeyError:
                        parameters = {}
        return parameters
   
    def _at_runtime(self, item: Any) -> dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            item (Project): instance from which implementation 
                parameters can be derived.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(item, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = item.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        return self
    

@dataclasses.dataclass
class ProjectManager(holden.System, base.ProjectKeystone, abc.ABC):
    """Iterator for chrisjen workflows.
        
    Args:
        contents (MutableMapping[Hashable, Set[Hashable]]): keys are nodes and 
            values are sets of nodes (or hashable representations of nodes). 
            Defaults to a defaultdict that has a set for its value format.
        name:
                  
    """  
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    name: Optional[str] = None
    nodes: amos.Library = dataclasses.field(default_factory = amos.Library)
                                                          
    """ Required Subclass Methods """

    @abc.abstractmethod
    def complete(self, project: Project) -> Project:
        """Iterates through nodes."""
        pass

    @abc.abstractclassmethod
    def create(self, name: str, project: Project) -> ProjectManager:
        """Iterates through nodes."""
        pass


@dataclasses.dataclass
class ProjectWorker(holden.System, ProjectNode):
    """Base class for creating, managing, and iterating a workflow.
        
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (MutableMapping[Hashable, Set[Hashable]]): keys are node labels 
            and labels of nodes to which the key node is linked
            Defaults to a defaultdict that has a set for its value format.
                     
    """
    name: Optional[str] = None
    contents: MutableMapping[Hashable, Set[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    project: Optional[base.Project] = None
    
    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'worker.repository'."""
        # Calls other '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if not abc.ABC in cls.__bases__:
            base.ProjectStructure.nodes.deposit(item = cls)
        base.Structure.nodes.kindify(item = cls, kind = 'worker')
                         
    """ Required Subclass Methods """

    def complete(self, item: Any, *args: Any, **kwargs: Any) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        for node in self.walk:
            component = self.create_component(
                name = node, 
                project = self.project)
            self.project = component.complete(self.project, *args, **kwargs)
        return
  


@dataclasses.dataclass
class Worker(holden.Path, ProjectNode):
    """Iterable component of a chrisjen workflow.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
                              
    """
    name: Optional[str] = None
    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)

    """ Public Methods """  
    
    def complete(self, 
        project: base.Project, 
        **kwargs) -> base.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (base.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            base.Project: with possible changes made.
            
        """
        if self.contents not in [None, 'None', 'none']:
            self.finalize(project = project, **kwargs)
            project = self.implement(project = project, **self.parameters)
        return project
           
    def implement(
        self, 
        project: base.Project, 
        **kwargs) -> base.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (base.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            base.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)  

    """ Private Methods """
    
    def _implement_in_serial(
        self, 
        project: base.Project, 
        **kwargs) -> base.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (base.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            base.Project: with possible changes made.
            
        """
        for node in self.contents:
            project = node.complete(project = project, **kwargs)
        return project  
    
                 
@dataclasses.dataclass
class Task(ProjectNode):
    """Base class for nodes in a project workflow.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)
    
    """ Public Methods """
    
    def implement(
        self, 
        project: base.Project, 
        **kwargs) -> base.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (base.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            base.Project: with possible changes made.
            
        """
        try:
            project = self.contents.complete(project = project, **kwargs)
        except AttributeError:
            project = self.contents(project, **kwargs)
        return project   


@dataclasses.dataclass   
class Criteria(base.ProjectKeystone):
    """Evaluates paths for use by Judge.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

 
def is_component(item: Union[object, Type[Any]]) -> bool:
    """Returns whether 'item' is a component.

    Args:
        item (Union[object, Type[Any]]): instance or class to check.

    Returns:
        bool: whether 'item' is a component.
        
    """
    return (
        miller.has_attributes(item, ['name', 'contents', 'parameters'])
        and miller.has_methods(item, ['complete']))


                  
    # """ Public Methods """ 
           
    # def implement(
    #     self,
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Applies 'contents' to 'project'.
        
    #     Args:
    #         project (base.Project): instance from which data needed for 
    #             implementation should be derived and all results be added.

    #     Returns:
    #         base.Project: with possible changes made.
            
    #     """
    #     if len(self.contents) > 1 and project.settings.general['parallelize']:
    #         project = self._implement_in_parallel(project = project, **kwargs)
    #     else:
    #         project = self._implement_in_serial(project = project, **kwargs)
    #     return project      

    # """ Private Methods """
   
    # def _implement_in_parallel(
    #     self, 
    #     project: base.Project, 
    #     **kwargs) -> base.Project:
    #     """Applies 'implementation' to 'project' using multiple cores.

    #     Args:
    #         project (Project): chrisjen project to apply changes to and/or
    #             gather needed data from.
                
    #     Returns:
    #         Project: with possible alterations made.       
        
    #     """
    #     if project.parallelize:
    #         with multiprocessing.Pool() as pool:
    #             project = pool.starmap(
    #                 self._implement_in_serial, 
    #                 project, 
    #                 **kwargs)
    #     return project 
  

