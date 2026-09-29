"""classes facilitating different timing of project node construction

Contents:
    UpFront (base.Engineer): all nodes are created at the beginning of a
        project and stored in a repository for when they are needed. This method
        is the fastest.
    AsNeeded (base.Engineer): nodes are created the first time that they are
        needed and then stored in a repository of they are needed again. This
        method balances speed and memory usage.
    OnlyAsNeeded (base.Engineer): nodes are created only when needed and need
        to be recreated if needed again. This method conserves memory the best.

To Do:


"""
from __future__ import annotations

import dataclasses

from ..core import framework, resources


@dataclasses.dataclass
class UpFront(resources.Engineer):
    """Constructs an entire workflow at once.

    Args:
        project (structure.Project): linked Project instance to modify and
            control.

    """
    project: framework.Project | None = None

    """ Public Methods """


@dataclasses.dataclass
class AsNeeded(resources.Engineer):
    """Constructs all workers in workflows but not tasks.

    Args:
        project (structure.Project): linked Project instance to modify and
            control.

    """
    project: framework.Project | None = None

    """ Public Methods """

    # def acquire(
    #     self,
    #     name: str | tuple[str, str],
    #     **kwargs: base.Kwargs) -> keystones.Node:
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
class OnlyAsNeeded(resources.Engineer):
    """Constructs a workflow as it is iterated.

    Args:
        project (structure.Project): linked Project instance to modify and
            control.

    """
    project: framework.Project | None = None

    """ Public Methods """

