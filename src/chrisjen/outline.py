"""Plan for a project, derived from its settings.

Contents:
    Outline: the workers, steps, and techniques of a project and the options
        for each.

"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any

import bobbie

from . import utilities

# Settings in a worker's section that are options for its workflow. All other
# settings in the section are stored in `Outline.initialization`.
_WORKFLOW_OPTIONS: tuple[str, ...] = (
    "criteria",
    "max_iterations",
    "select",
    "tolerance",
)
_SUFFIXES: tuple[str, ...] = (
    "_design",
    "_requires",
    "_steps",
    "_technique_type",
    "_techniques",
    "_workers",
)


@dataclasses.dataclass
class Outline:
    """Workers, steps, and techniques of a project and the options for each.

    An outline is created from `bobbie.Settings` with `create`. The settings
    need a section named for the project with a "_project" suffix. Within it,
    "{name}_workers" lists the workers and "{name}_design" sets the design that
    combines them. Each worker has its own section:

    ```ini
    [example_project]
    example_workers = cleaner, modeler
    example_design = waterfall

    [modeler]
    design = contest
    modeler_steps = scale, fit
    scale_techniques = minmax, zscore
    fit_techniques = linear, forest
    criteria = accuracy
    model_type = classify

    [scale_parameters]
    clip = True
    ```

    In a worker's section, "design" (or "{worker}_design") selects the design,
    "{worker}_steps" lists its steps, and "{step}_techniques" lists the
    techniques of each step. If a worker has no steps, "{worker}_techniques"
    lists its techniques directly. A step with no techniques uses a technique
    with the same name as the step. "{step}_technique_type" (or
    "{worker}_technique_type" for a worker with no steps) names the type of technique to look in, such as
    "cleaner"; without it, techniques are looked up by name in every type. "{step}_requires" lists steps that must
    come before a step (see `Pert`), and "{worker}_requires" in the project
    section lists workers that must come before a worker. If any step (or
    worker) has requirements, only the listed requirements connect the steps
    (or workers), so those without them can start in parallel. The options `criteria`, `max_iterations`, `select`, and
    `tolerance` are passed to the design. Any other setting is kept in
    `initialization`. A section named "{name}_parameters" holds keyword
    parameters for the worker, step, or technique with that name.

    Lists are separated by commas. Because settings are read per worker, two
    workers can each have a step with the same name and different techniques.
    Parameters are shared by name, though: a step called "clean" gets the same
    "clean_parameters" wherever it appears.

    Args:
        name: name of the project.
        design: design used to combine the workers. Defaults to 'waterfall'.
        workers: names of the workers. Defaults to an empty `list`.
        designs: `dict` of worker names and their designs.
        steps: `dict` of worker names and the names of their steps.
        techniques: `dict` of worker names and a `dict` of the names of their
            steps and the names of the techniques of each step. A worker with
            no steps has a single entry, named for the worker.
        requirements: `dict` of worker names and a `dict` of the names of their
            steps and the names of steps that must come before them. The
            requirements of the workers themselves are stored under the name
            of the project.
        types: `dict` of worker names and a `dict` of the names of their steps
            and the type of technique named for each (if any).
        parameters: `dict` of names and their keyword parameters.
        durations: `dict` of names and their durations, taken from the
            "duration" parameter, if any.
        options: `dict` of worker names (and the project name) and their
            workflow options.
        initialization: `dict` of worker names and their other settings.
        kinds: `dict` of every name and its kind: 'worker', 'step', or
            'technique'.

    """

    name: str
    design: str = "waterfall"
    workers: list[str] = dataclasses.field(default_factory = list)
    designs: dict[str, str] = dataclasses.field(default_factory = dict)
    steps: dict[str, list[str]] = dataclasses.field(default_factory = dict)
    techniques: dict[str, dict[str, list[str]]] = dataclasses.field(
        default_factory = dict
    )
    requirements: dict[str, dict[str, list[str]]] = dataclasses.field(
        default_factory = dict
    )
    types: dict[str, dict[str, str]] = dataclasses.field(default_factory = dict)
    parameters: dict[str, dict[str, Any]] = dataclasses.field(
        default_factory = dict
    )
    durations: dict[str, float] = dataclasses.field(default_factory = dict)
    options: dict[str, dict[str, Any]] = dataclasses.field(default_factory = dict)
    initialization: dict[str, dict[str, Any]] = dataclasses.field(
        default_factory = dict
    )
    kinds: dict[str, str] = dataclasses.field(default_factory = dict)

    """ Properties """

    @property
    def summary(self) -> str:
        """Returns a text description of the outline."""
        lines = [f"{self.name} ({self.design})"]
        for worker in self.workers:
            lines.append(f"  {worker} ({self.designs[worker]})")
            for step, techniques in self.techniques[worker].items():
                if worker in self.steps:
                    lines.append(f"    {step}: {', '.join(techniques)}")
                else:
                    lines.append(f"    {', '.join(techniques)}")
        return "\n".join(lines)

    """ Class Methods """

    @classmethod
    def create(
        cls, idea: bobbie.Settings | Mapping[str, Any], name: str | None = None
    ) -> Outline:
        """Creates an outline from settings.

        Args:
            idea: settings that describe the project.
            name: name of the project. If it is `None`, the name is taken from
                the first section that ends in "_project".

        Raises:
            ValueError: if the settings have no project section, a worker has no
                section, a worker has neither steps nor techniques, or a worker
                or step is listed more than once.
            TypeError: if a section is not a mapping.

        Returns:
            An `Outline` based on `idea`.

        """
        section_name = cls._find_project(idea, name)
        name = section_name.removesuffix("_project")
        section = cls._get_section(idea, section_name)
        outline = cls(name = name)
        outline.design = cls._get_design(section, name)
        outline.workers = cls._get_names(
            section, f"{name}_workers", f"the workers of {name!r}"
        )
        if not outline.workers:
            message = (
                f"section {section_name!r} must list workers in a "
                f'"{name}_workers" setting'
            )
            raise ValueError(message)
        outline.options[name] = cls._get_options(section)
        outline.initialization[name] = cls._get_initialization(section)
        needed = {
            worker: cls._get_names(
                section,
                f"{worker}_requires",
                f"the requirements of {worker!r}",
            )
            for worker in outline.workers
        }
        needed = {worker: names for worker, names in needed.items() if names}
        if needed:
            outline.requirements[name] = needed
        for worker in outline.workers:
            outline.kinds[worker] = "worker"
            outline._add_worker(idea, worker)
        outline._add_parameters(idea)
        return outline

    """ Private Methods """

    @staticmethod
    def _find_project(
        idea: bobbie.Settings | Mapping[str, Any], name: str | None
    ) -> str:
        """Returns the name of the section that describes the project."""
        if name is not None:
            key = name if name.endswith("_project") else f"{name}_project"
            if key in idea:
                return key
        else:
            for key in idea:
                if str(key).endswith("_project"):
                    return str(key)
        target = f'"{name}_project"' if name else 'ending in "_project"'
        message = f"the settings have no section named {target}"
        raise ValueError(message)

    @staticmethod
    def _get_section(
        idea: bobbie.Settings | Mapping[str, Any], name: str
    ) -> Mapping[str, Any]:
        """Returns the section `name`, which must be a mapping."""
        section = idea[name]
        if not isinstance(section, Mapping):
            message = (
                f"section {name!r} must be a mapping of settings, not "
                f"{type(section).__name__}"
            )
            raise TypeError(message)
        return section

    @staticmethod
    def _get_design(section: Mapping[str, Any], name: str) -> str:
        """Returns the design named in a section, or the default."""
        design = section.get(
            "design", section.get(f"{name}_design", "waterfall")
        )
        return str(design).strip().lower()

    @staticmethod
    def _get_names(
        section: Mapping[str, Any],
        key: str,
        description: str,
        *,
        unique: bool = True,
    ) -> list[str]:
        """Returns the names in the list setting `key` of `section`.

        Values may be a `list` or comma-separated `str`. Text from an ini file
        is only split by `bobbie` on a comma followed by a space, so any names
        still joined with a comma are split here.

        Args:
            section: section containing the setting.
            key: name of the setting.
            description: what the names are, for an error message.
            unique: whether a name may only appear once. Techniques may be
                repeated (to apply one twice, for example), but workers, steps,
                and requirements may not.

        Raises:
            ValueError: if `unique` is `True` and a name appears more than
                once.

        Returns:
            The names, in order, as `str` types with no surrounding spaces.

        """
        names: list[str] = []
        for value in utilities.iterify(section.get(key)):
            names.extend(
                part.strip() for part in str(value).split(",") if part.strip()
            )
        duplicates = sorted({n for n in names if names.count(n) > 1})
        if unique and duplicates:
            message = (
                f"{description} must be unique, but {duplicates} "
                f"{'is' if len(duplicates) == 1 else 'are'} listed more "
                f'than once in "{key}"'
            )
            raise ValueError(message)
        return names

    @staticmethod
    def _get_options(section: Mapping[str, Any]) -> dict[str, Any]:
        """Returns the workflow options in a section."""
        return {k: section[k] for k in _WORKFLOW_OPTIONS if k in section}

    @staticmethod
    def _get_initialization(section: Mapping[str, Any]) -> dict[str, Any]:
        """Returns the settings in a section that are not otherwise used."""
        reserved = {"design", *_WORKFLOW_OPTIONS}
        return {
            k: v
            for k, v in section.items()
            if k not in reserved and not k.endswith(_SUFFIXES)
        }

    def _add_worker(
        self, idea: bobbie.Settings | Mapping[str, Any], worker: str
    ) -> None:
        """Adds a worker, its steps, and its techniques."""
        if worker not in idea:
            message = f"the settings have no section for worker {worker!r}"
            raise ValueError(message)
        section = self._get_section(idea, worker)
        self.designs[worker] = self._get_design(section, worker)
        self.options[worker] = self._get_options(section)
        self.initialization[worker] = self._get_initialization(section)
        self.techniques[worker] = {}
        steps = self._get_names(
            section, f"{worker}_steps", f"the steps of {worker!r}"
        )
        if not steps:
            techniques = self._get_names(
                section,
                f"{worker}_techniques",
                f"the techniques of {worker!r}",
                unique = False,
            )
            if not techniques:
                message = (
                    f"worker {worker!r} needs steps (in "
                    f'"{worker}_steps") or techniques (in '
                    f'"{worker}_techniques")'
                )
                raise ValueError(message)
            self.techniques[worker][worker] = techniques
            self._add_techniques(techniques)
            self._add_type(section, worker, worker)
            return
        self.steps[worker] = steps
        for step in steps:
            self.kinds[step] = "step"
            techniques = self._get_names(
                section,
                f"{step}_techniques",
                f"the techniques of {step!r}",
                unique = False,
            )
            self.techniques[worker][step] = techniques or [step]
            self._add_techniques(self.techniques[worker][step])
            self._add_type(section, worker, step)
            required = self._get_names(
                section, f"{step}_requires", f"the requirements of {step!r}"
            )
            if required:
                self.requirements.setdefault(worker, {})[step] = required

    def _add_type(
        self, section: Mapping[str, Any], worker: str, step: str
    ) -> None:
        """Records the type of technique for a step, if the section names one."""
        kind = section.get(f"{step}_technique_type")
        if kind is not None:
            self.types.setdefault(worker, {})[step] = str(kind).strip().lower()

    def _add_techniques(self, techniques: list[str]) -> None:
        """Records the names of techniques that are not also steps."""
        for technique in techniques:
            self.kinds.setdefault(technique, "technique")

    def _add_parameters(
        self, idea: bobbie.Settings | Mapping[str, Any]
    ) -> None:
        """Adds parameters and durations for every named item."""
        for name in self.kinds:
            key = f"{name}_parameters"
            if key not in idea:
                continue
            parameters = dict(self._get_section(idea, key))
            if "duration" in parameters:
                self.durations[name] = float(parameters.pop("duration"))
            self.parameters[name] = parameters
