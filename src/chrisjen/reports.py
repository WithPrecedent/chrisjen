"""Subclasses of Report.

Contents:
    Summary: a short text summary of a project.

"""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from . import base, utilities

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
        workflow = project.workflow
        paths = [
            utilities._label_path(path)
            for path in (workflow.walk() if workflow is not None else [])]
        lines = [
            f'project: {project.name}',
            f'id: {project.id}',
            f'paths: {"; ".join(paths) or "none"}',
            f'result: {project.result!r}',
        ]
        text = '\n'.join(lines)
        self.contents = text
        return text
