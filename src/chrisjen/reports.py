"""Subclasses of Report.

Contents:
    Summary: a short text summary of a project.

"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from . import base

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass
class Summary(base.Report):
    """A short text summary of a project.

    Args:
        contents: the text of the most recent summary. Defaults to `None`.

    """

    def generate(self, project: interface.Project) -> str:
        """Generates the summary and stores it in `contents`.

        Args:
            project: the project to summarize.

        Returns:
            The text of the summary.

        """
        paths = [
            ' > '.join(node.name for node in path)
            for path in project.workflow.walk()]
        lines = [
            f'project: {project.name}',
            f'id: {project.id}',
            f'paths: {"; ".join(paths) or "none"}',
            f'result: {project.result!r}',
        ]
        self.contents = '\n'.join(lines)
        return self.contents
