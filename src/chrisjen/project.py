"""Interface for creating and running a project.

Contents:
    Project: creates a workflow from settings and applies it.

"""

from __future__ import annotations

import dataclasses
import pathlib
from collections.abc import Mapping
from typing import Any

import bobbie
import nagata

from . import export, nodes, utilities, workflows
from . import outline as outlines


@dataclasses.dataclass
class Project:
    """Creates a workflow from settings and applies it to an item.

    A project moves through three stages:

    1. `draft`: the settings (`idea`) are turned into an `outline`.
    2. `publish`: the outline is turned into a `workflow` of nodes.
    3. `apply`: the workflow is applied to an item, and the result is stored in
       `result`.

    Creating a `Project` drafts it. If `automatic` is `True`, the project is
    also published and applied to `item`.

    Args:
        idea: settings that describe the project. It may be a path to an ini,
            json, toml, py, xml, or yaml file, a `dict`, or a
            `bobbie.Settings` instance.
        name: name of the project. Defaults to `None`, in which case it is
            taken from the section of `idea` that ends with "_project".
        item: data or object that the workflow is applied to. Defaults to
            `None`.
        automatic: whether to publish and apply the project as soon as it is
            created. Defaults to `False`.
        identification: unique name for this run, which is used for the name
            of the folder where the project's files are kept. Defaults to
            `None`, in which case it is the name of the project and the
            current date and time.
        root: folder for all projects' files. Defaults to 'data'.

    Attributes:
        outline: the `Outline` created by `draft`.
        workflow: the workflow created by `publish`.
        result: the result of the last call to `apply`.

    """

    idea: bobbie.Settings | Mapping[str, Any] | pathlib.Path | str
    name: str | None = None
    item: Any = None
    automatic: bool = False
    identification: str | None = None
    root: pathlib.Path | str = "data"
    outline: outlines.Outline | None = dataclasses.field(
        default=None, init=False, repr=False
    )
    workflow: workflows.Workflow | None = dataclasses.field(
        default=None, init=False, repr=False
    )
    result: Any = dataclasses.field(default=None, init=False)
    _clerk: nagata.FileManager | None = dataclasses.field(
        default=None, init=False, repr=False
    )

    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Validates the settings and drafts the project."""
        if not isinstance(self.idea, bobbie.Settings):
            self.idea = bobbie.Settings.create(self.idea)
        self.draft()
        if self.identification is None:
            self.identification = utilities.how_soon_is_now(
                prefix=f"{self.name}_"
            )
        if self.automatic:
            self.publish()
            self.apply()

    """ Class Methods """

    @classmethod
    def create(
        cls,
        idea: bobbie.Settings | Mapping[str, Any] | pathlib.Path | str,
        **kwargs: Any,
    ) -> Project:
        """Creates a project.

        Args:
            idea: settings that describe the project.
            **kwargs: other arguments for `Project`.

        Returns:
            A drafted `Project`.

        """
        return cls(idea=idea, **kwargs)

    """ Properties """

    @property
    def clerk(self) -> nagata.FileManager:
        """Returns the project's file manager.

        The first time it is accessed, folders for input, interim, and output
        files are created in `root` under the project's `identification`. The
        "files" section of `idea`, if there is one, overrides the default file
        settings (such as 'file_encoding').

        Returns:
            A `nagata.FileManager` for the project.

        """
        if self._clerk is None:
            # `bobbie.Settings.get` raises an error for a missing key, so the
            # "files" section is checked for explicitly.
            files = self.idea["files"] if "files" in self.idea else {}  # noqa: SIM401
            settings = {**nagata.FileFramework.settings, **dict(files)}
            framework = type(
                "ProjectFramework",
                (nagata.FileFramework,),
                {"settings": settings},
            )
            self._clerk = nagata.FileManager(
                root_folder=pathlib.Path(self.root) / self.identification,
                input_folder="input",
                interim_folder="interim",
                output_folder="output",
                framework=framework,
            )
        return self._clerk

    @property
    def summary(self) -> str:
        """Returns a text description of the project."""
        text = [self.outline.summary if self.outline else str(self.name)]
        if self.workflow is not None:
            path, duration = self.workflow.critical_path()
            text.append(f"critical path: {' > '.join(path)} ({duration})")
        return "\n".join(text)

    """ Public Methods """

    def apply(self, item: Any = None, **kwargs: Any) -> Any:
        """Applies the workflow to `item`, publishing it first if needed.

        Args:
            item: data or object to change. Defaults to the project's `item`.
            **kwargs: keyword arguments passed to the nodes in the workflow.

        Returns:
            The result of the workflow, which is also stored in `result`.

        """
        if self.workflow is None:
            self.publish()
        self.result = self.workflow.execute(
            self.item if item is None else item, **kwargs
        )
        return self.result

    def draft(self) -> outlines.Outline:
        """Creates the `outline` from the settings.

        Returns:
            The `Outline`.

        """
        self.outline = outlines.Outline.create(self.idea, name=self.name)
        self.name = self.outline.name
        return self.outline

    def publish(self) -> workflows.Workflow:
        """Creates the `workflow` from the outline.

        Returns:
            The `Workflow`, whose nodes are `Worker` instances.

        """
        plan = self.outline
        workers = [self._build_worker(worker) for worker in plan.workers]
        names = {worker.name for worker in workers}
        self.workflow = workflows.Workflow.design(
            plan.design,
            workers,
            name=plan.name,
            requirements=plan.requirements.get(plan.name, {}),
            durations=_pick(plan.durations, names),
            **plan.options.get(plan.name, {}),
        )
        return self.workflow

    def to_dot(
        self, path: pathlib.Path | str | None = None, name: str | None = None
    ) -> str:
        """Returns the workflow as a Graphviz dot `str`.

        Args:
            path: file to save the text to. Defaults to `None`.
            name: name of the graph. Defaults to the name of the project.

        Returns:
            The dot text. Each worker is a cluster of its steps.

        """
        if self.workflow is None:
            self.publish()
        return export.to_dot(self.workflow, path=path, name=name)

    def to_mermaid(
        self, path: pathlib.Path | str | None = None, name: str | None = None
    ) -> str:
        """Returns the top-level workflow as a mermaid flowchart `str`.

        Args:
            path: file to save the text to. Defaults to `None`.
            name: name of the chart. Defaults to the name of the project.

        Returns:
            The mermaid text.

        """
        if self.workflow is None:
            self.publish()
        return self.workflow.to_mermaid(path=path, name=name or self.name)

    """ Private Methods """

    def _build_technique(
        self, name: str, kind: str | None = None
    ) -> nodes.Technique:
        """Returns a copy of the registered technique with `name`."""
        parameters = dict(self.outline.parameters.get(name, {}))
        return nodes.Technique.create(
            name,
            parameters={"name": name, "parameters": parameters},
            kind=kind,
        )

    def _build_step(
        self, name: str, techniques: list[str], kind: str | None = None
    ) -> nodes.Step:
        """Returns a step with `techniques`."""
        return nodes.Step(
            name=name,
            contents=[self._build_technique(t, kind) for t in techniques],
            parameters=dict(self.outline.parameters.get(name, {})),
        )

    def _build_worker(self, name: str) -> nodes.Worker:
        """Returns a worker with its steps and workflow."""
        plan = self.outline
        techniques = plan.techniques[name]
        # A worker without steps has a single step named for the worker.
        kinds = plan.types.get(name, {})
        steps = [
            self._build_step(step, step_techniques, kinds.get(step))
            for step, step_techniques in techniques.items()
        ]
        names = {step.name for step in steps}
        workflow = workflows.Workflow.design(
            plan.designs[name],
            steps,
            requirements=plan.requirements.get(name, {}),
            name=name,
            durations=_pick(plan.durations, names),
            **plan.options.get(name, {}),
        )
        return nodes.Worker(
            name=name,
            contents=workflow,
            parameters=dict(plan.parameters.get(name, {})),
        )


def _pick(items: Mapping[str, Any], names: set[str]) -> dict[str, Any]:
    """Returns the items of `items` with keys in `names`."""
    return {k: v for k, v in items.items() if k in names}
