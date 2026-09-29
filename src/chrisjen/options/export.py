"""Functions to export composite data structures to other formats

Contents:


To Do:


"""
from __future__ import annotations

import pathlib
from typing import Any

import holden

from .. import base

_LINE_BREAK = '\n'
_LINK = '->'

def to_dot(
    project: base.Project,
    path: str | pathlib.Path | None = None,
    name: str | None = None,
    settings: dict[str, Any] | None = None) -> str:
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
    dot = f'digraph {name}' + ' {\n'
    if settings is not None:
        for key, value in settings.items():
            dot = f'{dot}{key}={value};{_LINE_BREAK}'
    for edge in edges:
        cluster = None
        if isinstance(edge[0], tuple):
            cluster = edge[0][0]
            start = edge[0][1]
        else:
            start = edge[0]
        if start == 'none':
            start = f'{start}_{cluster}'
        stop = edge[1][1] if isinstance(edge[1], tuple) else edge[1]
        if stop == 'none':
            stop = f'{stop}_{cluster}'
        if cluster:
            dot = (
                f'{dot}subgraph cluster_{cluster} '
                 '{ label='
                + cluster
                + f' rank=same {start} labeljust=l '
                + '}\n'
            )
        dot = f'{dot}{start} {_LINK} {stop}{_LINE_BREAK}'
    dot = dot + '}'
    if path is not None:
        with open(path, 'w') as a_file:
            a_file.write(dot)
        a_file.close()
    return dot
