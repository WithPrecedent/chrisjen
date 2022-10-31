"""
librarians: classes facilitating different timing of project node construction
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
class UpFront(keystones.Librarian):
    """Constructs an entire workflow at once.
        
    Args:
        project (framework.Project): linked Project instance to modify and 
            control.
             
    """
    project: Optional[framework.Project] = None
                                 
    """ Public Methods """

 
@dataclasses.dataclass
class AsNeeded(keystones.Librarian):
    """Constructs all workers in workflows but not tasks.
        
    Args:
        project (framework.Project): linked Project instance to modify and 
            control.
             
    """
    project: Optional[framework.Project] = None
                                 
    """ Public Methods """
 
    # def acquire(
    #     self, 
    #     name: str | tuple[str, str], 
    #     **kwargs: Any) -> keystones.Node:
    #     """Gets node from the project library.

    #     Args:
    #         name (str | tuple[str, str]): name of the node that should match
    #             a key in the project library.

    #     Returns:
    #         keystones.Node: a Node subclass instance based on passed arguments.
            
    #     """
    #     if isinstance(name, tuple):
    #         step = self.acquire(name = name[0])
    #         technique = self.acquire(name = name[1])
    #         return step.create(
    #             name = name[0], 
    #             technique = technique,
    #             project = self.project)
    #     else:
    #         lookups = self._get_lookups(name = name)
    #         # initialization = self._get_initialization(lookups = lookups)
    #         # initialization.update(**kwargs)
    #         node = self._get_node(lookups = lookups)
    #         return node.create(name = name, project = self.project, **kwargs)

   
@dataclasses.dataclass
class OnlyAsNeeded(keystones.Librarian):
    """Constructs a workflow as it is iterated.
        
    Args:
        project (framework.Project): linked Project instance to modify and 
            control.
             
    """
    project: Optional[framework.Project] = None
                                 
    """ Public Methods """

    