"""
tasks: primitive task nodes for chrisjen workflows
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
    Step
    Technique
    
"""
from __future__ import annotations
import abc
from collections.abc import Callable, Hashable, MutableMapping
import dataclasses
from typing import Any, Optional, TYPE_CHECKING, Union

from . import bases
from . import components

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
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
    
    """
    name: Optional[str] = None
    contents: Optional[components.Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)   
 
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
        contents (bases.Criteria]): stored criteria to be used to select from 
            several nodes or paths. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty bases.Parameters instance.
            
    Attributes:
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
        
    
    """
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)      
    
               
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
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
              
    """
    name: Optional[str] = None
    contents: Optional[components.Technique] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
    score_attribute: Optional[str] = None
    
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
class Contest(Judge):
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
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
    
    """
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)

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
        for key, result in results.items():
            self.scores[key] = result.score
            
        project = self.contents.execute(projects = results)  
        return project


@dataclasses.dataclass   
class Survey(Judge):
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
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
    
    """
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)


@dataclasses.dataclass   
class Validation(Judge):
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
        scores (MutableMapping[Hashable, float]): scores based on the criteria
            stored in 'contents'.
        options (ClassVar[amos.Catalog]): Component subclasses stored with str 
            keys derived from the 'amos.get_name' function.
    
    """
    name: Optional[str] = None
    contents: Optional[bases.Criteria] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = bases.Parameters)
