"""Functions to organize workflows.

Contents:

To Do:


"""
from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import base


def arrrange_parallel(
    name: str,
    project: base.Project) -> list[list[tuple[str, str]]]:
    """_summary_

    Args:
        name (str): _description_
        project (framework.Project): _description_

    Returns:
        list[list[tuple[str, str]]]: _description_
    """
    steps = project.connections[name]
    connections = project.connections[name]
    possible = [connections[s] for s in steps]
    combos = list(itertools.product(*possible))
    step_tasks = []
    for combo in combos:
        recipe = []
        recipe.extend((steps[i], task) for i, task in enumerate(combo))
        step_tasks.append(recipe)
    return step_tasks

def arrange_serial(name: str, project: base.Project) -> list[tuple[str, str]]:
    """_summary_

    Args:
        name (str): _description_
        project (framework.Project): _description_

    Returns:
        list[tuple[str, str]]: _description_
    """
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

