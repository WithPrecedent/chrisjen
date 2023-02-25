"""
export: functions to export composite data structures to other formats
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2023, Corey Rayburn Yung
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
import pathlib
from typing import Any, Callable, Optional

import holden 

from ..core import framework


_LINE_BREAK = '\n'
_LINK = '->'

def to_dot(
    project: framework.Project,
    path: Optional[str | pathlib.Path] = None,
    name: Optional[str] = None,
    settings: Optional[dict[str, Any]] = None) -> str:
    """Converts 'item' to a dot format.

    Args:
        item (holden.Composite): item to convert to a dot format.
        path (Optional[str | pathlib.Path]): path to export 'item' to. Defaults
            to None.
        name (Optional[str]): name of 'item' to put in the dot str. Defaults to
            None.
        settings (Optional[dict[str, Any]]): any global settings to add to the
            dot graph. Defaults to None.

    Returns:
        str: composite object in graphviz dot format.

    """
    edges = holden.transform(
        item = project.workflow.graph, 
        output = 'edges', 
        raise_same_error = False)
    name = name or 'chrisjen'
    dot = 'digraph ' +  name + ' {\n'
    if settings is not None:
        for key, value in settings.items():
            dot = dot + f'{key}={value};{_LINE_BREAK}'
    for edge in edges:
        cluster = None
        if isinstance(edge[0], tuple):
            cluster = edge[0][0]
            start = edge[0][1]
        else:
            start = edge[0]
        if isinstance(edge[1], tuple):
            stop = edge[1][1]
        else:
            stop = edge[1]
        if start == 'none':
            start = start + '_' + cluster
        if stop == 'none':
            stop = stop + '_' + cluster
        if cluster:
            dot = (
                dot 
                + f'subgraph cluster_{cluster} '
                + '{ label='
                + cluster
                + f' rank=same {start} labeljust=l '
                + '}\n')
        dot = dot + f'{start} {_LINK} {stop}{_LINE_BREAK}'
    dot = dot + '}'
    if path is not None:
        with open(path, 'w') as a_file:
            a_file.write(dot)
        a_file.close()
    return dot
 