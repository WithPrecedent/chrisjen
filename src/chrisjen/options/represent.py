"""represent

Contents:


To Do:


"""
from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import base


""" Public Functions """

"""
linear
linear steps
parallel steps
parallel steps judge


"""
def represent_parallel(
    name: str,
    project: base.Project) -> list[list[tuple[str, str]]]:
    """_summary_

    Args:
        name (str): _description_
        project (structure.Project): _description_

    Returns:
        list[list[tuple[str, str]]]: _description_

    """
    connections = project.outline.connections
    steps = connections[name]
    techniques = [connections[s] for s in steps]
    combos = list(itertools.product(*techniques))
    recipes = []
    recipes.extend(
        [(steps[i], t) for i, t in enumerate(combo)] for combo in combos
    )
    return recipes

def represent_serial(
    name: str,
    project: base.Project) -> list[str] | list[tuple[str, str]]:
    """_summary_

    Args:
        name (str): _description_
        project (structure.Project): _description_

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
    project: base.Project) -> list[tuple[str, str]]:
    """_summary_

    Args:
        name (str): _description_
        project (structure.Project): _description_

    Returns:
        list[list[tuple[str, str]]]: _description_

    """
    section = project.outline.workers[name]
    connections = section[name]
    steps = connections[name]
    techniques = [connections[s] for s in steps]
    process = []
    for step in steps:
        process.extend((step, technique) for technique in techniques)
    return process
