"""
tasks: primitive task nodes for chrisjen workflows
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
    Step
    Technique
    
"""
from __future__ import annotations
import abc
from collections.abc import Callable, Hashable, MutableMapping
import dataclasses
from typing import Any, Optional, TYPE_CHECKING, Union

from . import framework
from . import components

if TYPE_CHECKING:
    from . import framework


@dataclasses.dataclass
class Step(components.Task):
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

    Attributes:
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
                                                 
    """
    name: Optional[str] = None
    contents: Optional[Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)
                    
    """ Properties """
    
    @property
    def technique(self) -> Optional[Technique]:
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
    
    def complete(self, 
        project: base.Project, 
        **kwargs) -> base.Project:
        """Calls the 'implement' method of 'contents'.

        Args:
            project (base.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            base.Project: with possible changes made.
            
        """
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if hasattr(self.parameters, 'finalize'):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if self.technique.parameters:
                if hasattr(self.technique.parameters, 'finalize'):
                    self.technique.parameters.finalize(project = project)
                technique_parameters = self.technique.parameters
                parameters.update(technique_parameters)  
            self.technique.implement(project = project, **parameters)
        return project
        
                                                  
@dataclasses.dataclass
class Technique(components.Task):
    """Primitive node for single task execution.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.

    Attributes:
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
                                                 
    """
    name: Optional[str] = None
    contents: Optional[Callable[..., Optional[Any]]] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)
    step: Optional[Union[str, Step]] = None
        
    """ Properties """
    
    @property
    def algorithm(self) -> Optional[Callable[..., Optional[Any]]]:
        return self.contents
    
    @algorithm.setter
    def algorithm(self, value: Callable[..., Optional[Any]]) -> None:
        self.contents = value
        return self
    
    @algorithm.deleter
    def algorithm(self) -> None:
        self.contents = None
        return self


@dataclasses.dataclass
class Proctor(components.Task, abc.ABC):
    """Base class for making multiple instances of a project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'project'
            passed to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty base.Parameters instance.
            
    Attributes:
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
    
    """
    name: Optional[str] = None
    contents: Optional[components.Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)   
 
    """ Private Methods """

    def _name_worker(self, index: int, prefix: str = 'experiment') -> str:
        """[summary]

        Args:
            index (int): [description]
            prefix (str, optional): [description]. Defaults to 'experiment'.

        Returns:
            str: [description]
            
        """        
        return prefix + '_' + str(index)


@dataclasses.dataclass
class Judge(components.Task, abc.ABC):
    """Base class for selecting a node or path.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (base.Criteria]): stored criteria to be used to select from 
            several nodes or paths. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty base.Parameters instance.
            
    Attributes:
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
        
    
    """
    name: Optional[str] = None
    contents: Optional[framework.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)      
    
               
@dataclasses.dataclass
class Scorer(components.Task):
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
            
    Attributes:
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
              
    """
    name: Optional[str] = None
    contents: Optional[components.Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)
    score_attribute: Optional[str] = None
    
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
class Contest(Judge):
    """Base class for selecting a node or path.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (base.Criteria]): stored criteria to be used to select from 
            several nodes or paths. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty base.Parameters instance.
            
    Attributes:
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
    
    """
    name: Optional[str] = None
    contents: Optional[framework.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)

    """ Public Methods """
    
    def implement(
        self, 
        project: base.Project, 
        **kwargs) -> base.Project:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (base.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            base.Project: with possible changes made.
            
        """
        results = super().implement(project = project, **kwargs)
        for key, result in results.items():
            self.scores[key] = result.score
            
        project = self.contents.complete(projects = results)  
        return project


@dataclasses.dataclass   
class Survey(Judge):
    """Base class for selecting a node or path.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (base.Criteria]): stored criteria to be used to select from 
            several nodes or paths. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty base.Parameters instance.
            
    Attributes:
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
    
    """
    name: Optional[str] = None
    contents: Optional[framework.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)


@dataclasses.dataclass   
class Validation(Judge):
    """Base class for selecting a node or path.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow
            Defaults to None.
        contents (base.Criteria]): stored criteria to be used to select from 
            several nodes or paths. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty base.Parameters instance.
            
    Attributes:
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
    
    """
    name: Optional[str] = None
    contents: Optional[framework.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = framework.Parameters)
