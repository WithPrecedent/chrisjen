"""
managers: classes for project direction and control
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
    UpFront (base.Librarian): all nodes are created at the beginning of a 
        project and stored in a repository for when they are needed. This method 
        is the fastest.
    AsNeeded (base.Librarian): nodes are created the first time that they are 
        needed and then stored in a repository of they are needed again. This 
        method balances speed and memory usage.
    OnlyAsNeeded (base.Librarian): nodes are created only when needed and need 
        to be recreated if needed again. This method conserves memory the best.
        
To Do:

            
"""
from __future__ import annotations
from collections.abc import Hashable, MutableMapping, MutableSequence
import contextlib
import dataclasses
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING

from ..core import framework
from ..core import keystones

    
@dataclasses.dataclass
class Publisher(keystones.Manager):
    """Constructs an entire workflow at once.
        
    Args:
        project (framework.Project): linked Project instance.
             
    """
    project: framework.Project
                                 
    """ Public Methods """
        
    def complete(self) -> None:
        """Completes all stages in 'project'."""
        self.draft()
        self.publish()
        self.execute()
        return
        
    def draft(self) -> None:
        """Adds an outline to 'project'."""
        outline = framework.ProjectKeystones.view['outline']
        self.project.outline = outline.create(project = self.project)
        return
    
    def publish(self) -> None:
        """Adds a workflow to 'project'."""
        workflow = framework.ProjectKeystones.view['workflow']
        self.project.workflow = workflow.create(project = self.project)
        return
     
    def execute(self) -> None:
        """Adds a summary to 'project'."""
        summary = framework.ProjectKeystones.view['summary']
        self.project.summary = summary.create(project = self.project)
        return       
 
    