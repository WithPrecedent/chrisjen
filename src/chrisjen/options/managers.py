"""Classes for project direction and control.

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

import wonka

from .. import base, resources


@dataclasses.dataclass
class Publisher(resources.Manager):
    """Constructs an entire workflow at once.

    Args:
        project (structure.Project): linked Project instance.

    """
    project: base.Project

    """ Public Methods """

    def complete(self) -> None:
        """Completes all stages in 'project'."""
        self.draft()
        self.publish()
        self.execute()
        return

    def draft(self) -> None:
        """Adds an outline to 'project'."""
        outline = wonka.Keystones.view['outline']
        self.project.outline = outline.create(project = self.project)
        return

    def publish(self) -> None:
        """Adds a workflow to 'project'."""
        workflow = wonka.Keystones.view['workflow']
        self.project.workflow = workflow.create(project = self.project)
        return

    def execute(self) -> None:
        """Adds a summary to 'project'."""
        summary = wonka.Keystones.view['summary']
        self.project.summary = summary.create(project = self.project)
        return

