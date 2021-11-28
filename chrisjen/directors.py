"""
directors: iterators for project workflows
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
import more_itertools

from . import bases

if TYPE_CHECKING:
    from . import interface


def implement(
    node: bases.Component,
    project: interface.Project, 
    **kwargs) -> interface.Project:
    """Applies 'node' to 'project'.

    Args:
        node (bases.Component): node in a workflow to apply to 'project'.
        project (interface.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        interface.Project: with possible changes made by 'node'.
        
    """
    ancestors = count_ancestors(node = node, workflow = project.workflow)
    descendants = len(project.workflow[node])
    if ancestors > descendants:
        method = closer_implement
    elif ancestors < descendants:
        method = test_implement
    elif ancestors == descendants:
        method = task_implement
    return method(node = node, project = project, **kwargs)
    
def closer_implement(
    node: bases.Component,
    project: interface.Project, 
    **kwargs) -> interface.Project:
    """Applies 'node' to 'project'.

    Args:
        node (bases.Component): node in a workflow to apply to 'project'.
        project (interface.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        interface.Project: with possible changes made by 'node'.
        
    """
    try:
        project = node.execute(project = project, **kwargs)
    except AttributeError:
        project = node(project, **kwargs)
    return project    

def test_implement(
    node: bases.Component,
    project: interface.Project, 
    **kwargs) -> interface.Project:
    """Applies 'node' to 'project'.

    Args:
        node (bases.Component): node in a workflow to apply to 'project'.
        project (interface.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        interface.Project: with possible changes made by 'node'.
        
    """
    connections = project.workflow[node]
    # Makes copies of project for each pipeline in a test.
    copies = [copy.deepcopy(project) for _ in connections]
    # if project.settings['general']['parallelize']:
    #     method = _test_implement_parallel
    # else:
    #     method = _test_implement_serial
    results = []
    for i, connection in enumerate(connections):
        results.append(implement(
            node = project.workflow[connection],
            project = copies[i], 
            **kwargs))
         
    
def task_implement(
    node: bases.Component,
    project: interface.Project, 
    **kwargs) -> interface.Project:
    """Applies 'node' to 'project'.

    Args:
        node (bases.Component): node in a workflow to apply to 'project'.
        project (interface.Project): instance from which data needed for 
            implementation should be derived and all results be added.

    Returns:
        interface.Project: with possible changes made by 'node'.
        
    """
    try:
        project = node.execute(project = project, **kwargs)
    except AttributeError:
        project = node(project, **kwargs)
    return project    

def count_ancestors(node: bases.Component, workflow: bases.Stage) -> int:
    connections = list(more_itertools.collapse(workflow.values()))
    return connections.count(node)
    
    
            
@dataclasses.dataclass
class Worker(Component, abc.ABC):
    """Keystone class for parts of a chrisjen workflow.

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

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                              
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1

    """ Public Methods """  
    
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    

    """ Private Methods """
    
    def _implement_in_serial(self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies stored nodes to 'project' in order.

        Args:
            project (Project): chrisjen project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        for node in self.paths[0]:
            project = node.execute(project = project, **kwargs)
        return project 
        

@dataclasses.dataclass
class Laborer(amos.Pipeline, Worker):
    """Keystone class for parts of a chrisjen workflow.

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

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                              
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
   
    """ Public Methods """  

    def integrate(self, project: interface.Project) -> interface.Project:
        """[summary]

        Args:
            project (interface.Project): [description]

        Returns:
            interface.Project: [description]
        """        
        pipeline = create_pipeline(
            name = self.name,
            project = project,
            base = amos.Pipeline)
        graph = amos.System.from_pipeline(item = pipeline)
        return project.workflow.append(graph)   

    def implement(
        self, project: interface.Project, **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        return self._implement_in_serial(project = project, **kwargs)    

 
@dataclasses.dataclass
class Manager(Worker, abc.ABC):
    """Base class for branching and parallel Workers.
        
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
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                          
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Union[Callable, str] = None
              
    """ Public Methods """
    
    def integrate(self, project: interface.Project) -> interface.Project:
        """[summary]

        Args:
            project (interface.Project): [description]

        Returns:
            interface.Project: [description]
        """        
        pipelines = create_pipelines(
            name = self.name,
            project = project,
            base = amos.Pipelines)
        graph = amos.System.from_pipelines(item = pipelines)
        return project.workflow.append(graph)   
           
    def implement(
        self,
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.
        
        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        if len(self.contents) > 1 and project.parallelize:
            project = self._implement_in_parallel(project = project, **kwargs)
        else:
            project = self._implement_in_serial(project = project, **kwargs)
        return project      

    """ Private Methods """
   
    def _implement_in_parallel(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'implementation' to 'project' using multiple cores.

        Args:
            project (Project): chrisjen project to apply changes to and/or
                gather needed data from.
                
        Returns:
            Project: with possible alterations made.       
        
        """
        if project.parallelize:
            with multiprocessing.Pool() as pool:
                project = pool.starmap(
                    self._implement_in_serial, 
                    project, 
                    **kwargs)
        return project 


@dataclasses.dataclass
class Contest(Manager):
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
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                          
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None
 
    
@dataclasses.dataclass
class Study(Manager):
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
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                        
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None
  
    
@dataclasses.dataclass
class Survey(Manager):
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
            parallel branches of the workflow or the name of a Component in 
            'library' to use. Defaults to None.
            
    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                            
    """
    name: Optional[str] = None
    contents: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    default: Any = dataclasses.field(default_factory = list)
    critera: Callable = None


@dataclasses.dataclass
class Task(Component):
    """Node type for chrisjen Workflows.

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
        step (Union[str, Callable]):
        
    """
    name: Optional[str] = None
    contents: Optional[Callable[..., Optional[Any]]] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    step: Union[str, Callable] = None
    technique: Callable = None
  
    """ Public Methods """
    
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        project = self.contents.execute(project = project, **kwargs)
        return project    


@dataclasses.dataclass
class Step(Task):
    """Wrapper for a Technique.

    Subclasses of Step can store additional methods and attributes to implement
    all possible technique instances that could be used. This is often useful 
    when creating branching, parallel workflows which test a variety of 
    strategies with similar or identical parameters and/or methods.

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

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                                                 
    """
    name: Optional[str] = None
    contents: Optional[Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
                    
    """ Properties """
    
    @property
    def technique(self) -> Technique:
        return self.contents
    
    @technique.setter
    def technique(self, value: Technique) -> None:
        self.contents = value
        return self
    
    @technique.deleter
    def technique(self) -> None:
        self.contents = None
        return self
    
    """ Public Methods """
    
    def integrate(self, project: interface.Project) -> interface.Project:
        """[summary]

        Args:
            technique (Technique): [description]

        Returns:
            Technique: [description]
            
        """
        if self.parameters:
            new_parameters = self.parameters
            new_parameters.update(project.parameters)
            project.parameters = new_parameters
        return project
        
                                                  
@dataclasses.dataclass
class Technique(Task):
    """Keystone class for primitive objects in an amicus composite object.

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

    Attributes:
        library (ClassVar[Library]): library that stores concrete (non-abstract) 
            subclasses and instances of Component. 
                                                 
    """
    name: Optional[str] = None
    contents: Optional[Callable[..., Optional[Any]]] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    step: str = None
        
    """ Properties """
    
    @property
    def algorithm(self) -> Union[object, str]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Union[object, str]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self

    """ Public Methods """

    def execute(self, 
        project: interface.Project, 
        iterations: Union[int, str] = None, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        if self.step is not None:
            step = self.library.withdraw(name = self.step)
            self = step.integrate(technique = self)
        return super().execute(
            project = project, 
            iterations = iterations, 
            **kwargs)


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
   