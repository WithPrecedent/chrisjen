"""Tests Project, including settings from files and file management."""

from __future__ import annotations

import dataclasses
import json
import pathlib
from typing import Any

import bobbie
import pytest

import chrisjen


def project_double(item: Any) -> Any:
    return item * 2


chrisjen.Technique.register("project_double", project_double)


def project_add(item: Any, amount: int = 1) -> Any:
    return item + amount


chrisjen.Technique.register("project_add", project_add)


def project_negate(item: Any) -> Any:
    return -item


chrisjen.Technique.register("project_negate", project_negate)


@chrisjen.criterion
def project_closeness(result: Any) -> Any:
    return -abs(result - 10)


@dataclasses.dataclass
class ProjectSquare(chrisjen.Technique):
    def implement(self, item: Any, **kwargs: Any) -> Any:  # noqa: ARG002
        return item**2


IDEA = {
    "demo_project": {
        "demo_workers": ["prep", "pick"],
        "demo_design": "waterfall",
    },
    "prep": {
        "prep_steps": ["grow", "shift"],
        "grow_techniques": "project_double",
        "shift_techniques": "project_add",
    },
    "shift_parameters": {"amount": 3},
    "pick": {
        "design": "contest",
        "criteria": "project_closeness",
        "pick_steps": ["first", "second"],
        "first_techniques": ["project_negate", "none", "project_square"],
        "second_techniques": ["project_double", "none"],
    },
}


def test_three_stages() -> None:
    project = chrisjen.Project(IDEA, item=2)
    assert project.name == "demo"
    assert project.outline is not None
    assert project.workflow is None
    workflow = project.publish()
    assert workflow is project.workflow
    assert workflow.walk() == [["prep", "pick"]]
    result = project.apply()
    # prep: 2 * 2 + 3 = 7. pick: the closest to 10 is 7 unchanged (score -3).
    assert result == 7
    assert project.result == 7
    pick = workflow.retrieve("pick").contents
    assert pick.winner == "none > none"
    assert pick.scores["none > project_double"] == -4


def test_apply_publishes_if_needed_and_accepts_an_item() -> None:
    project = chrisjen.Project.create(IDEA)
    assert project.apply(5) == 13
    assert project.workflow is not None
    assert project.apply(item=1, amount=10) == 12


def test_automatic() -> None:
    project = chrisjen.Project(IDEA, item=2, automatic=True)
    assert project.result == 7


def test_ini_file() -> None:
    path = pathlib.Path(__file__).parent / "cancer_settings.ini"
    project = chrisjen.Project(path)
    assert project.name == "wisconsin_cancer"
    assert project.outline.workers == ["wrangler", "analyst", "critic"]
    assert isinstance(project.idea, bobbie.Settings)


def test_json_and_toml_files(tmp_path: pathlib.Path) -> None:
    json_path = tmp_path / "settings.json"
    json_path.write_text(json.dumps(IDEA))
    assert chrisjen.Project(json_path, item=2).apply() == 7
    toml_path = tmp_path / "settings.toml"
    toml_path.write_text(
        "[demo_project]\n"
        'demo_workers = ["prep"]\n'
        "[prep]\n"
        'prep_steps = ["grow"]\n'
        'grow_techniques = "project_double"\n'
    )
    assert chrisjen.Project(toml_path, item=4).apply() == 8


def test_existing_settings_are_used_as_is() -> None:
    idea = bobbie.Settings.create(IDEA)
    project = chrisjen.Project(idea)
    assert project.idea is idea


def test_unknown_technique_is_reported_when_publishing() -> None:
    idea = {
        "x_project": {"x_workers": "w"},
        "w": {"w_techniques": ["nonexistent_technique"]},
    }
    project = chrisjen.Project(idea)
    with pytest.raises(KeyError, match="nonexistent_technique"):
        project.publish()


def test_missing_settings_file() -> None:
    with pytest.raises(FileNotFoundError):
        chrisjen.Project("does_not_exist.ini")


def test_worker_without_steps_uses_techniques_directly() -> None:
    idea = {
        "x_project": {"x_workers": ["w"]},
        "w": {"w_techniques": ["project_double", "project_add"]},
    }
    assert chrisjen.Project(idea, item=3).apply() == 7


def test_project_and_worker_parameters() -> None:
    idea = {
        "x_project": {"x_workers": ["w"]},
        "w": {"w_steps": ["s"], "s_techniques": "project_add"},
        "s_parameters": {"amount": 10},
        "project_add_parameters": {"amount": 20},
        "w_parameters": {"amount": 30},
    }
    # Worker parameters are passed to every node and take precedence.
    assert chrisjen.Project(idea, item=0).apply() == 30
    del idea["w_parameters"]
    # A technique's parameters beat its step's.
    assert chrisjen.Project(idea, item=0).apply() == 20
    del idea["project_add_parameters"]
    assert chrisjen.Project(idea, item=0).apply() == 10


def test_durations_and_summary() -> None:
    idea = {
        "x_project": {"x_workers": ["w"], "design": "pert"},
        "w": {
            "design": "pert",
            "w_steps": ["a", "b", "c"],
            "c_requires": ["a", "b"],
            "a_techniques": "none",
            "b_techniques": "none",
            "c_techniques": "none",
        },
        "a_parameters": {"duration": 4},
        "b_parameters": {"duration": 1},
    }
    project = chrisjen.Project(idea, item=0)
    project.publish()
    worker = project.workflow.retrieve("w").contents
    assert worker.critical_path() == (["a", "c"], 5.0)
    assert worker.walk() == [["a", "c"], ["b", "c"]] or worker.walk() == [
        ["b", "c"],
        ["a", "c"],
    ]
    assert "x (pert)" in project.summary
    assert "critical path: w" in project.summary


def test_clerk_creates_folders_and_saves_files(tmp_path: pathlib.Path) -> None:
    project = chrisjen.Project(IDEA, root=tmp_path, identification="run1")
    # Nothing is written to disk until the clerk is used.
    assert not (tmp_path / "run1").exists()
    clerk = project.clerk
    assert clerk is project.clerk
    for folder in ("input", "interim", "output"):
        assert (tmp_path / "run1" / folder).is_dir()
    clerk.save(item="hello", file_name="greeting.txt")
    assert (tmp_path / "run1" / "output" / "greeting.txt").read_text() == (
        "hello"
    )
    assert (
        clerk.load(file_path=tmp_path / "run1" / "output" / "greeting.txt")
        == "hello"
    )
    clerk.save(item={"a": 1}, file_name="data", file_format="pickle")
    assert clerk.load(
        file_name="data", file_format="pickle", folder="output"
    ) == {"a": 1}


def test_default_identification() -> None:
    project = chrisjen.Project(IDEA)
    assert project.identification.startswith("demo_")


def test_clerk_uses_file_settings_without_changing_defaults(
    tmp_path: pathlib.Path,
) -> None:
    import nagata

    idea = {**IDEA, "files": {"file_encoding": "utf-8", "custom": 1}}
    before = dict(nagata.FileFramework.settings)
    project = chrisjen.Project(idea, root=tmp_path)
    assert project.clerk.framework.settings["file_encoding"] == "utf-8"
    assert project.clerk.framework.settings["custom"] == 1
    assert nagata.FileFramework.settings == before


def test_to_dot_and_mermaid(tmp_path: pathlib.Path) -> None:
    project = chrisjen.Project(IDEA)
    dot = project.to_dot(path=tmp_path / "flow.dot")
    assert (tmp_path / "flow.dot").read_text() == dot
    assert dot.startswith('digraph "demo" {')
    assert 'subgraph "cluster_prep"' in dot
    assert '"prep..shift" -> "pick..first";' in dot
    assert 'label = "pick (contest)";' in dot
    mermaid = project.to_mermaid()
    assert "prep(prep) --> pick(pick)" in mermaid
    assert chrisjen.to_dot(project.workflow, name="other").startswith(
        'digraph "other" {'
    )
