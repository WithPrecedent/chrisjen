"""
components: core node types for project workflows
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
    Worker
    Manager
    Task
    Judge
    Step 
    Technique
    
"""
from __future__ import annotations
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, MutableSequence, Sequence)
import dataclasses
import multiprocessing
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos
import holden

from . import base
from . import nodes


@dataclasses.dataclass
class Worker(holden.Path, nodes.Component):
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

    Attributes:
        library (ClassVar[base.Options]): Component subclasses and
            instances stored with str keys derived from the 'amos.namify' 
            function.
                              
    """
    name: Optional[str] = None
    contents: MutableSequence[Hashable] = dataclasses.field(
        default_factory = list)
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = base.Parameters)
    library: ClassVar[amos.Library] = base.PROJECT_BASES['options']()

    """ Public Methods """  
    
    def execute(self, 
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
            project = node.execute(project = project, **kwargs)
        return project  
    
    
               
@dataclasses.dataclass
class Task(nodes.Component):
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
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = base.Parameters)
    library: ClassVar[amos.Library] = base.PROJECT_BASES['options']()
    
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
            project = self.contents.execute(project = project, **kwargs)
        except AttributeError:
            project = self.contents(project, **kwargs)
        return project   

