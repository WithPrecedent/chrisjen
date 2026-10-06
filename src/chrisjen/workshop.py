"""Functions for building a project's workflow from its settings.

The workshop decides what each name in the settings is (a worker, a step, or a
technique) and which class to build it with. Each class builds itself from the
settings with its `build` method.

Contents:
    build_criteria: builds the criteria named in settings.
    build_node: builds a worker or a technique from its name.
    build_step: builds the alternatives for a step.
    build_worker: builds a worker and all of the nodes in it.
    build_workflow: builds the workflow of a project.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import base, nodes, options

if TYPE_CHECKING:
    from . import interface


def build_criteria(name: str, project: interface.Project) -> base.Criteria:
    """Builds the criteria named `name`.

    Args:
        name: name of a `Criteria` subclass in the library, or the import path
            of a scoring function.
        project: the project the criteria belongs to.

    Returns:
        A `Criteria` instance.

    """
    parameters = project.idea.parameters.get(name, {})
    criteria = project.library.all.get(name)
    if criteria is None:
        return base.Criteria(contents = name, parameters = parameters)
    return criteria(parameters = parameters)


def build_node(name: str, project: interface.Project) -> base.Vertex:
    """Builds the node `name`: a worker or a technique.

    A name is a worker if it has a section of its own or a list of steps (see
    `build_worker`). Otherwise, it is built with the class in the library that
    has its name (usually a `Technique` subclass).

    Args:
        name: name of the node.
        project: the project the node belongs to.

    Raises:
        KeyError: if `name` is not a worker and no class in the library has
            its name.

    Returns:
        The built node.

    """
    idea = project.idea
    if name in idea.workers or name in idea.steps:
        return build_worker(name, project)
    return project.library.borrow(name).build(name, project)


def build_step(name: str, project: interface.Project) -> list[base.Vertex]:
    """Builds the alternatives for the step `name`.

    A step with techniques has one node for each of them: a `Step` that wraps
    the technique and is named "{technique}_{step}". The class of the step is
    the `Step` subclass named `name`, if there is one. Its parameters come from
    the "{step}_parameters" section of the settings and, for one technique in
    that step, the "{technique}_{step}_parameters" section. A step without
    techniques (or that is a worker) is a node itself (see `build_node`).

    Args:
        name: name of the step.
        project: the project the step belongs to.

    Returns:
        The alternatives for the step.

    """
    idea = project.idea
    if name in idea.workers or name not in idea.techniques:
        return [build_node(name, project)]
    try:
        kind = project.library.borrow(name, genre = 'step')
    except KeyError:
        kind = nodes.Step
    alternatives = []
    for technique in idea.techniques[name]:
        label = f'{technique}_{name}'
        step = kind.build(
            name,
            project,
            parameters = idea.parameters.get(label, {}),
            contents = build_node(technique, project))
        step.name = label
        alternatives.append(step)
    return alternatives


def build_worker(name: str, project: interface.Project) -> nodes.Worker:
    """Builds the worker `name` and all of the nodes in it.

    The class of the worker is the worker class named `name`, if there is one,
    and otherwise the class of its design (from the settings or
    `options._DEFAULT_DESIGN`). Its nodes are its steps, each a list of
    alternatives (see `build_step`), or, if it has no steps, its techniques,
    which are alternatives to each other. The `populate` method of the worker
    connects them: one after another for a `Flow`, or as every combination of
    alternatives for a `Contest` or `Survey`.

    Args:
        name: name of the worker.
        project: the project the worker belongs to.

    Returns:
        The built worker.

    """
    idea = project.idea
    design = idea.designs.get(name, options._DEFAULT_DESIGN)
    kind = project.library.borrow([name, design], genre = 'worker')
    worker = kind.build(name, project)
    if name in idea.criteria:
        worker.criteria = build_criteria(idea.criteria[name], project)
    if name in idea.steps:
        parts = [build_step(step, project) for step in idea.steps[name]]
    else:
        techniques = idea.techniques.get(name, [])
        parts = [[build_node(technique, project) for technique in techniques]]
    worker.populate(parts)
    return worker


def build_workflow(project: interface.Project) -> nodes.Worker:
    """Builds the workflow of `project`.

    The workflow is the worker for the project section of the settings.

    Args:
        project: the project to build the workflow for.

    Returns:
        The workflow of the project.

    """
    return build_worker(project.name, project)
