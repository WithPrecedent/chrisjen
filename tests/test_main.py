"""Tests the package as a whole."""

from __future__ import annotations

import pathlib
import tomllib

import chrisjen

ROOT = pathlib.Path(__file__).parent.parent


def test_version_matches_the_package_settings_and_changelog() -> None:
    with (ROOT / "pyproject.toml").open("rb") as file:
        project = tomllib.load(file)["project"]
    assert project["version"] == chrisjen.__version__
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {chrisjen.__version__}\n" in changelog


def test_dependencies_are_declared() -> None:
    with (ROOT / "pyproject.toml").open("rb") as file:
        dependencies = tomllib.load(file)["project"]["dependencies"]
    names = {d.split(">")[0].split("=")[0].strip() for d in dependencies}
    assert names == {"bobbie", "holden", "nagata", "wonka"}


def test_public_names_exist() -> None:
    for name in chrisjen.__all__:
        assert hasattr(chrisjen, name), name
    assert len(set(chrisjen.__all__)) == len(chrisjen.__all__)


def test_all_designs_are_available_by_name() -> None:
    for name in (
        "waterfall",
        "kanban",
        "scrum",
        "pert",
        "agile",
        "lean",
        "contest",
        "survey",
    ):
        design = chrisjen.Workflow.design(name, [])
        assert type(design).__name__.lower() == name
