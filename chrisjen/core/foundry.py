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

import amos

if TYPE_CHECKING:
    from . import base
    from . import nodes


_DEFAULT_DESIGN: str = 'waterfall'

def find_design(name: str, project: base.Project) -> str:
    """_summary_

    Args:
        name (str): _description_
        project (base.Project): _description_

    Returns:
        str: _description_
        
    """
    try:
        return project.outline.designs[name]
    except KeyError:
        return _DEFAULT_DESIGN
    
def complete_worker(
    name: str, 
    worker: nodes.Worker, 
    project: base.Project) -> nodes.Worker:
    """_summary_

    Args:
        name (str): _description_
        worker (nodes.Worker): _description_
        project (base.Project): _description_

    Returns:
        nodes.Worker: _description_
        
    """
    for name in amos.iterify(project.outline.connections[name]):
        kind = project.outline.kinds[name]  
        if kind in project.outline.suffixes['workers']:
            design = find_design(name = name, project = project)
            parameters = {'name': name, 'project': project}
            worker = project.factory.create(
                item = (name, design),
                parameters = parameters)
            node = complete_worker(
                name = name, 
                worker = worker, 
                project = project)
            worker.append(node)
        else:
            worker.append(name) 
    return worker
