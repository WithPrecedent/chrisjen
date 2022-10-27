"""
design: 
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
from collections.abc import Hashable, MutableMapping, MutableSequence
import itertools
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union


from ..core import keystones


def arrrange_parallel(
    name: str, 
    project: framework.Project) -> list[list[tuple[str, str]]]:
    steps = project.connections[name]
    connections = project.connections[name]
    possible = [connections[s] for s in steps]
    combos = list(itertools.product(*possible))   
    step_tasks = []
    for combo in combos:
        recipe = []
        for i, task in enumerate(combo):
            recipe.append((steps[i], task))
        step_tasks.append(recipe) 
    return step_tasks
        
def arrange_serial(name: str, project: framework.Project) -> list[tuple[str, str]]:
    steps = project.connections[name]
    connections = project.connections[name]
    possible = [connections[s] for s in steps]
    step_tasks = []
    for step in steps:
        pipeline = []
        for task in possible[step]:
            pipeline.append(step, task)
        step_tasks.append(pipeline)
    return step_tasks

   