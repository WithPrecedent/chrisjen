"""Tests for bugs that were found and fixed, so they do not come back."""

from __future__ import annotations

import pathlib
from typing import Any

import pytest

import chrisjen


def reg_add_one(item: Any) -> Any:
    return item + 1


chrisjen.Technique.register("reg_add_one", reg_add_one)


def reg_times_two(item: Any) -> Any:
    return item * 2


chrisjen.Technique.register("reg_times_two", reg_times_two)


def reg_minus_three(item: Any) -> Any:
    return item - 3


chrisjen.Technique.register("reg_minus_three", reg_minus_three)


@chrisjen.criterion
def reg_largest(result: Any) -> Any:
    return result


def write_ini(tmp_path: pathlib.Path, text: str) -> pathlib.Path:
    path = tmp_path / "settings.ini"
    path.write_text(text, encoding = "utf-8")
    return path


""" The same step name in different workers """


def test_workers_can_reuse_step_names() -> None:
    settings = {
        "x_project": {"x_workers": ["one", "two"]},
        "one": {"one_steps": ["clean"], "clean_techniques": "reg_add_one"},
        "two": {"two_steps": ["clean"], "clean_techniques": "reg_times_two"},
    }
    project = chrisjen.Project(settings, item = 5)
    assert project.apply() == 12
    assert project.outline.techniques == {
        "one": {"clean": ["reg_add_one"]},
        "two": {"clean": ["reg_times_two"]},
    }


def test_workers_can_reuse_step_names_with_different_requirements() -> None:
    settings = {
        "x_project": {"x_workers": ["one", "two"]},
        "one": {
            "design": "pert",
            "one_steps": ["a", "b"],
            "a_techniques": "reg_add_one",
            "b_techniques": "reg_add_one",
            "b_requires": "a",
        },
        "two": {
            "design": "pert",
            "two_steps": ["a", "b"],
            "a_techniques": "reg_times_two",
            "b_techniques": "reg_times_two",
            "a_requires": "b",
        },
    }
    project = chrisjen.Project(settings, item = 1)
    project.publish()
    one = project.workflow.retrieve("one").contents
    two = project.workflow.retrieve("two").contents
    assert one.order() == ["a", "b"]
    assert two.order() == ["b", "a"]
    # Worker one: 1 + 1 + 1 = 3. Worker two runs b then a: 3 * 2 * 2 = 12.
    assert project.apply() == 12
    assert list(two.results) == ["b", "a"]


def test_a_worker_and_its_step_and_technique_can_share_a_name() -> None:
    settings = {
        "x_project": {"x_workers": ["reg_add_one"]},
        "reg_add_one": {
            "reg_add_one_steps": ["reg_add_one"],
            "reg_add_one_techniques": "reg_add_one",
        },
    }
    assert chrisjen.Project(settings, item = 1).apply() == 2


""" Lists in settings files """


def test_lists_without_spaces_after_commas(tmp_path: pathlib.Path) -> None:
    path = write_ini(
        tmp_path,
        "[x_project]\n"
        "x_workers = one,two\n"
        "[one]\n"
        "one_techniques = reg_add_one\n"
        "[two]\n"
        "two_steps = a,b\n"
        "a_techniques = reg_times_two,reg_add_one\n"
        "b_techniques = reg_minus_three\n",
    )
    project = chrisjen.Project(path, item = 1)
    assert project.outline.workers == ["one", "two"]
    assert project.outline.techniques["two"] == {
        "a": ["reg_times_two", "reg_add_one"],
        "b": ["reg_minus_three"],
    }
    # ((1 + 1) * 2 + 1) - 3
    assert project.apply() == 2


def test_lists_with_extra_spaces_and_trailing_commas(
    tmp_path: pathlib.Path,
) -> None:
    path = write_ini(
        tmp_path,
        "[x_project]\n"
        "x_workers =  one ,  two , \n"
        "[one]\n"
        "one_techniques = reg_add_one\n"
        "[two]\n"
        "two_techniques = reg_add_one ,\n",
    )
    project = chrisjen.Project(path, item = 0)
    assert project.outline.workers == ["one", "two"]
    assert project.apply() == 2


def test_single_names_and_lists_from_dicts() -> None:
    for workers in ("one", ["one"], ("one",)):
        settings = {
            "x_project": {"x_workers": workers},
            "one": {"one_techniques": ["reg_add_one", "reg_add_one"]},
        }
        assert chrisjen.Project(settings, item = 0).apply() == 2


""" Names that are not case sensitive """


def test_design_names_ignore_case_and_spaces() -> None:
    settings = {
        "x_project": {"x_workers": ["w"], "design": " Waterfall "},
        "w": {"design": "KANBAN", "w_techniques": "reg_add_one"},
    }
    project = chrisjen.Project(settings, item = 1)
    assert project.outline.design == "waterfall"
    assert project.outline.designs == {"w": "kanban"}
    assert project.apply() == 2
    assert isinstance(project.workflow, chrisjen.Waterfall)
    assert isinstance(project.workflow.retrieve("w").contents, chrisjen.Kanban)


@pytest.mark.parametrize(("select", "expected"), [("MIN", 6), ("Max", 10)])
def test_select_ignores_case(select: str, expected: int) -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {
            "design": "contest",
            "criteria": "reg_largest",
            "select": select,
            "w_techniques": ["reg_add_one", "reg_times_two"],
        },
    }
    assert chrisjen.Project(settings, item = 5).apply() == expected


""" Unique names """


def test_duplicate_workers() -> None:
    settings = {
        "x_project": {"x_workers": ["w", "w"]},
        "w": {"w_techniques": "none"},
    }
    with pytest.raises(ValueError, match = r"workers of 'x' must be unique.*'w'"):
        chrisjen.Project(settings)


def test_duplicate_steps() -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {"w_steps": ["a", "a", "b"], "a_techniques": "none"},
    }
    with pytest.raises(ValueError, match = r"steps of 'w' must be unique.*'a'"):
        chrisjen.Project(settings)


def test_duplicate_nodes_in_a_workflow() -> None:
    steps = [
        chrisjen.Step(name = "a"),
        chrisjen.Step(name = "b"),
        chrisjen.Step(name = "a"),
    ]
    with pytest.raises(ValueError, match = "unique names.*'a'"):
        chrisjen.Workflow.design("waterfall", steps)


def test_repeated_techniques_are_allowed() -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {"w_steps": ["s"], "s_techniques": ["reg_add_one"] * 3},
    }
    assert chrisjen.Project(settings, item = 0).apply() == 3


def test_repeated_techniques_are_separate_paths_in_a_contest() -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {
            "design": "contest",
            "criteria": "reg_largest",
            "w_steps": ["s"],
            "s_techniques": ["reg_add_one", "reg_add_one", "reg_times_two"],
        },
    }
    project = chrisjen.Project(settings, item = 5)
    assert project.apply() == 10
    contest = project.workflow.retrieve("w").contents
    assert list(contest.results) == [
        "reg_add_one",
        "reg_add_one (2)",
        "reg_times_two",
    ]
    assert contest.scores == {
        "reg_add_one": 6,
        "reg_add_one (2)": 6,
        "reg_times_two": 10,
    }


def test_repeated_techniques_keep_their_weight_in_a_survey() -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {
            "design": "survey",
            "w_steps": ["s"],
            "s_techniques": ["reg_add_one", "reg_add_one", "reg_times_two"],
        },
    }
    assert chrisjen.Project(settings, item = 5).apply() == pytest.approx(22 / 3)


""" Bad settings """


def test_sections_must_be_mappings() -> None:
    with pytest.raises(TypeError, match = "'x_project' must be a mapping"):
        chrisjen.Project({"x_project": "oops"})
    with pytest.raises(TypeError, match = "'w' must be a mapping.*int"):
        chrisjen.Project({"x_project": {"x_workers": "w"}, "w": 3})
    with pytest.raises(TypeError, match = "'w_parameters' must be a mapping"):
        chrisjen.Project(
            {
                "x_project": {"x_workers": "w"},
                "w": {"w_techniques": "none"},
                "w_parameters": 3,
            }
        )


def test_a_worker_needs_steps_or_techniques() -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {"model_type": "classify"},
    }
    with pytest.raises(ValueError, match = "worker 'w' needs steps"):
        chrisjen.Project(settings)


def test_bad_duration() -> None:
    settings = {
        "x_project": {"x_workers": ["w"]},
        "w": {"w_techniques": "none"},
        "w_parameters": {"duration": "soon"},
    }
    with pytest.raises(ValueError, match = "soon"):
        chrisjen.Project(settings)


""" Circular requirements """


def circular_settings() -> dict[str, Any]:
    return {
        "x_project": {"x_workers": ["w"]},
        "w": {
            "design": "pert",
            "w_steps": ["a", "b", "c"],
            "a_techniques": "none",
            "b_techniques": "none",
            "c_techniques": "none",
            "a_requires": "c",
            "b_requires": "a",
            "c_requires": "b",
        },
    }


def test_a_cycle_is_found_when_the_project_is_published() -> None:
    project = chrisjen.Project(circular_settings(), item = 1)
    with pytest.raises(ValueError, match = "cycle"):
        project.publish()
    with pytest.raises(ValueError, match = "cycle"):
        project.apply()


def test_a_cycle_is_found_when_a_workflow_is_built() -> None:
    steps = [chrisjen.Step(name = "a"), chrisjen.Step(name = "b")]
    with pytest.raises(ValueError, match = "cycle"):
        chrisjen.Workflow.design(
            "pert", steps, requirements = {"a": ["b"], "b": ["a"]}
        )


def test_requirements_cannot_name_steps_of_other_workers() -> None:
    settings = {
        "x_project": {"x_workers": ["one", "two"]},
        "one": {"one_steps": ["a"], "a_techniques": "none"},
        "two": {
            "design": "pert",
            "two_steps": ["b"],
            "b_techniques": "none",
            "b_requires": "a",
        },
    }
    project = chrisjen.Project(settings)
    with pytest.raises(KeyError, match = "unknown nodes.*'a'"):
        project.publish()


""" Settings objects with different behaviors """


class StrictSettings(dict):
    """Like `bobbie.Settings`, `get` raises an error for a missing key."""

    def get(self, key: Any, default: Any = None) -> Any:
        if default is None and key not in self:
            raise KeyError(key)
        return super().get(key, default)


def test_project_does_not_rely_on_get_for_missing_sections() -> None:
    settings = StrictSettings(
        {
            "x_project": {"x_workers": ["w"]},
            "w": {"w_techniques": "reg_add_one"},
        }
    )
    outline = chrisjen.Outline.create(settings)
    assert outline.workers == ["w"]
    assert outline.parameters == {}
    project = chrisjen.Project(settings, item = 1)
    assert project.apply() == 2
    # The file manager does not need a "files" section either.
    assert "files" not in project.idea
