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
    Component
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
import inspect
import multiprocessing
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos
import more_itertools

from . import bases
from . import workshop

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass    
class ComponentParameters(amos.Dictionary):
    """Creates and stores parameters for a Component.
    
    The use of ComponentParameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    ComponentParameters can be unpacked with '**', which will turn the 
    'contents' attribute an ordinary set of kwargs. In this way, it can serve as 
    a drop-in replacement for a dict that would ordinarily be used for 
    accumulating keyword arguments.
    
    If a chrisjen class uses a ComponentParameters instance, the 'finalize' 
    method should be called before that instance's 'implement' method in order 
    for each of the parameter types to be incorporated.
    
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
        selected (Sequence[str]): an exclusive list of parameters that are 
            allowed. If 'selected' is empty, all possible parameters are 
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
    selected: Sequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, project: interface.Project, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            project (interface.Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting amos.
        parameters = self.default
        # Adds any parameters from 'settings'.
        try:
            parameters.update(self._from_settings(project = project))
        except AttributeError:
            pass
        # Adds any implementation parameters.
        if self.implementation:
            parameters.update(self._at_runtime(project = project))
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
     
    def _from_settings(self, project: interface.Project) -> dict[str, Any]: 
        """Returns any applicable parameters from 'settings'.

        Args:
            settings (amos.Settings): instance with possible 
                parameters.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
            
        """
        if hasattr(project, 'outline'):
            parameters = project.outline.runtime[self.name]
        else:
            try:
                parameters = project.settings[f'{self.name}_parameters']
            except KeyError:
                suffix = self.name.split('_')[-1]
                prefix = self.name[:-len(suffix) - 1]
                try:
                    parameters = project.settings[f'{prefix}_parameters']
                except KeyError:
                    try:
                        parameters = project.settings[f'{suffix}_parameters']
                    except KeyError:
                        parameters = {}
        return parameters
   
    def _at_runtime(self, project: interface.Project) -> dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            project (interface.Project): instance from which implementation 
                parameters can be derived.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(project, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = project.contents[attribute]
                except (KeyError, AttributeError):
                    pass
        return self

    
@dataclasses.dataclass
class Component(bases.ProjectNode, amos.LibraryFactory, abc.ABC):
    """Base class for nodes in a project workflow.

    Args:
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty 'ComponentParameters' instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
  
    """
    contents: Optional[Any] = None
    name: Optional[str] = None
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
        try:
            project = self.contents.execute(project = project, **kwargs)
        except AttributeError:
            project = self.contents(project, **kwargs)
        return project    
       
        
@dataclasses.dataclass
class Worker(Component, abc.ABC):
    """Keystone class for parts of a chrisjen workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (dict[str, list[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.

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
class Laborer(amos.Graph, Worker):
    """Keystone class for parts of a chrisjen workflow.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (dict[str, list[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.

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
        pipeline = workshop.create_pipeline(
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (dict[str, list[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
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
        pipelines = workshop.create_pipelines(
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (dict[str, list[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (dict[str, list[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (dict[str, list[str]]): an adjacency list where the keys are 
            names of components and the values are names of components which the 
            key component is connected to. Defaults to an empty dict.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        default (Any): default value to return when the 'get' method is used.
            Defaults to an empty list.
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. 
            Defaults to None. 
        step (Union[str, Callable]):
        

    """
    name: Optional[str] = None
    contents: Optional[Callable[..., Optional[Any]]] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = ComponentParameters)
    iterations: Union[int, str] = 1
    step: Union[str, Callable] = None
    technique: Callable = None
      
    """ Required Subclass Methods """
    
    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass
  
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
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (Technique): stored Technique instance to be used by the 
            'implement' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
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
    
    def integrate(self, technique: Technique) -> Technique:
        """[summary]

        Args:
            technique (Technique): [description]

        Returns:
            Technique: [description]
            
        """
        if self.parameters:
            new_parameters = self.parameters
            new_parameters.update(technique.parameters)
            technique.parameters = new_parameters
        return technique
        
                                                  
@dataclasses.dataclass
class Technique(Task):
    """Keystone class for primitive objects in an amicus composite object.

    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout amicus. For example, if an amicus 
            instance needs settings from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        contents (Callable): stored Callable algorithm to be used by the 
            'implement' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty Parameters instance.
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

