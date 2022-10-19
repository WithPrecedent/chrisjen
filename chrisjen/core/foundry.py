"""
foundry: functions for creating and modifying project-related classes
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
    create_workflow
    create_worker
    create_worker
    create_judge
    create_step
    create_technique
    create_results

To Do:
    Add support for parallel construction of Results in the 'create_results'
        function.
        
"""
from __future__ import annotations
from collections.abc import Hashable, MutableMapping, Sequence
import copy
import itertools
from typing import Any, Optional, Type, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .core import base
    from .. import components
    from . import views
    

def create_workflow(
    project: base.Project,
    name: Optional[str] = None,
    base: Optional[Type[views.Workflow]] = None, 
    **kwargs) -> views.Workflow:
    """Creates workflow based on 'project'.

    Args:
        project (base.Project): project with information needed to create a
            workflow.
        name (Optional[str]): name of node from which to start the workflow. 
            Defaults to None.
        base (Optional[Type[base.Workflow]]): base workflow case to use. 
            Defaults to None.

    Returns:
        views.Workflow: completed workflow.
        
    """   
    base = base or project.repository.keystones['workflow']
    name = name or project.name
    workflow = base(project = project, **kwargs)
    connections = project.settings.connections
    design = project.outline.designs[name]
    