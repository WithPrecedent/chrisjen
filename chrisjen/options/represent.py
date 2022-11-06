"""
represent
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
from collections.abc import Hashable, MutableMapping, Sequence
import itertools
from typing import Any, Optional, Type, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from ..core import framework
    

""" Public Functions """
         
"""
linear
linear steps
parallel steps
parallel steps judge


"""
def represent_parallel(
    name: str, 
    project: framework.Project) -> list[list[tuple[str, str]]]:
    """_summary_

    Args:
        name (str): _description_
        project (framework.Project): _description_

    Returns:
        list[list[tuple[str, str]]]: _description_
    
    """   
    connections = project.outline.connections
    steps = connections[name]
    techniques = [connections[s] for s in steps]
    combos = list(itertools.product(*techniques)) 
    recipes = [] 
    for combo in combos:
        recipes.append([tuple([steps[i], t]) for i, t in enumerate(combo)])
    return recipes

def represent_serial(
    name: str, 
    project: framework.Project) -> list[str] | list[tuple[str, str]]:
    """_summary_

    Args:
        name (str): _description_
        project (framework.Project): _description_

    Returns:
        list[str]: _description_
        
    """    
    section = project.outline.connections[name]
    connections = section[name]   
    if any(c in section for c in connections):
        return represent_serial_steps(name = name, project = project)
    elif len(section) == 1:
        return connections
    else:
        return list(itertools.chain.from_iterable(section.values()))
                
def represent_serial_steps(
    name: str, 
    project: framework.Project) -> list[tuple[str, str]]:
    """_summary_

    Args:
        name (str): _description_
        project (framework.Project): _description_

    Returns:
        list[list[tuple[str, str]]]: _description_
    
    """   
    section = project.outline.workers[name]
    connections = section[name]
    steps = connections[name]
    techniques = [connections[s] for s in steps]
    process = [] 
    for step in steps:
        for technique in techniques:
            process.append(tuple([step, technique]))
    return process
