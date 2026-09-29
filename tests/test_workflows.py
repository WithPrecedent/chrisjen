"""Tests workflow designs."""

from __future__ import annotations

import copy
from typing import Any

import pytest

import chrisjen


def make_step(name: str, *functions: Any, **parameters: Any) -> chrisjen.Step:
    techniques = [
        chrisjen.Technique(name=f.__name__, contents=f) for f in functions
    ]
    return chrisjen.Step(name=name, contents=techniques, parameters=parameters)


def add_one(item: int) -> int:
    return item + 1


def times_two(item: int) -> int:
    return item * 2


def minus_three(item: int) -> int:
    return item - 3


def steps() -> list[chrisjen.Step]:
    return [make_step("a", add_one), make_step("b", times_two)]


""" Base behavior """


def test_design_by_name_and_alias() -> None:
    nodes = steps()
    assert isinstance(
        chrisjen.Workflow.design("waterfall", nodes), chrisjen.Waterfall
    )
    assert isinstance(
        chrisjen.Workflow.design("compete", nodes), chrisjen.Contest
    )
    assert isinstance(
        chrisjen.Workflow.design("sequential", nodes), chrisjen.Waterfall
    )


def test_unknown_design() -> None:
    with pytest.raises(KeyError, match="not a known workflow design"):
        chrisjen.Workflow.design("spiral", steps())


def test_graph_structure() -> None:
    workflow = chrisjen.Workflow.design("waterfall", steps())
    assert workflow.walk() == [["a", "b"]]
    assert workflow.root == ["a"]
    assert workflow.endpoint == ["b"]
    assert workflow.retrieve("a").name == "a"
    assert [n.name for n in workflow.sequence] == ["a", "b"]


def test_cycle_is_detected() -> None:
    workflow = chrisjen.Workflow.design("waterfall", steps())
    workflow.connect(("b", "a"))
    with pytest.raises(ValueError, match="cycle"):
        workflow.order()


def test_unknown_requirement() -> None:
    with pytest.raises(KeyError, match="unknown nodes"):
        chrisjen.Workflow.design(
            "pert", steps(), requirements={"b": ["missing"]}
        )


def test_empty_workflow() -> None:
    workflow = chrisjen.Workflow.design("waterfall", [])
    assert workflow.execute(5) == 5
    assert workflow.critical_path() == ([], 0.0)


""" Sequential designs """


def test_waterfall() -> None:
    workflow = chrisjen.Workflow.design("waterfall", steps())
    assert workflow.execute(1) == 4
    assert workflow.results == {"a": 2, "b": 4}
    assert workflow.execute(10) == 22
    assert workflow.results == {"a": 11, "b": 22}


def test_keyword_arguments_reach_techniques() -> None:
    def scale(item: int, factor: int = 1) -> int:
        return item * factor

    workflow = chrisjen.Workflow.design("waterfall", [make_step("s", scale)])
    assert workflow.execute(3) == 3
    assert workflow.execute(3, factor=5) == 15


def test_kanban_isolates_stages() -> None:
    def append_x(item: list[str]) -> list[str]:
        item.append("x")
        return item

    workflow = chrisjen.Workflow.design(
        "kanban", [make_step("one", append_x), make_step("two", append_x)]
    )
    original: list[str] = []
    result = workflow.execute(original)
    assert result == ["x", "x"]
    assert original == []
    assert workflow.results["one"] == ["x"]
    assert workflow.results["two"] == ["x", "x"]


def test_scrum() -> None:
    workflow = chrisjen.Workflow.design("scrum", steps())
    assert workflow.upcoming == "a"
    item = workflow.advance(1)
    assert item == 2
    assert workflow.upcoming == "b"
    item = workflow.advance(item + 10)
    assert item == 24
    assert workflow.done
    with pytest.raises(StopIteration):
        workflow.advance(item)
    # execute finishes what is left and then resets.
    workflow.position = 1
    assert workflow.execute(5) == 10
    assert workflow.position == 0
    assert workflow.execute(1) == 4


def test_pert_dependencies_and_critical_path() -> None:
    nodes = [
        make_step("start", add_one),
        make_step("left", times_two),
        make_step("right", minus_three),
        make_step("finish", add_one),
    ]
    workflow = chrisjen.Workflow.design(
        "pert",
        nodes,
        requirements={
            "left": ["start"],
            "right": ["start"],
            "finish": ["left", "right"],
        },
        durations={"start": 1, "left": 5, "right": 2, "finish": 1},
    )
    assert workflow.root == ["start"]
    assert workflow.endpoint == ["finish"]
    assert sorted(map(tuple, workflow.walk())) == [
        ("start", "left", "finish"),
        ("start", "right", "finish"),
    ]
    path, total = workflow.critical_path()
    assert path == ["start", "left", "finish"]
    assert total == 7
    assert workflow.order() == ["start", "left", "right", "finish"]
    # Every node runs once, in dependency order.
    assert workflow.execute(1) == ((1 + 1) * 2 - 3) + 1


def test_pert_without_requirements_is_sequential() -> None:
    workflow = chrisjen.Workflow.design("pert", steps())
    assert workflow.walk() == [["a", "b"]]
    assert workflow.critical_path() == (["a", "b"], 2.0)


""" Iterative designs """


def test_agile_repeats_until_criteria_met() -> None:
    workflow = chrisjen.Workflow.design(
        "agile", [make_step("a", add_one)], criteria=lambda r: r >= 5
    )
    assert workflow.execute(0) == 5
    assert workflow.iterations == 5


def test_agile_stops_at_max_iterations() -> None:
    workflow = chrisjen.Workflow.design(
        "agile",
        [make_step("a", add_one)],
        criteria=lambda r: False,  # noqa: ARG005
        max_iterations=3,
    )
    assert workflow.execute(0) == 3
    assert workflow.iterations == 3


def test_lean_keeps_the_best() -> None:
    # Scores go up for three passes and then down.
    def shape(item: int) -> int:
        return item + 1

    workflow = chrisjen.Workflow.design(
        "lean", [make_step("a", shape)], criteria=lambda r: -abs(r - 3)
    )
    assert workflow.execute(0) == 3
    assert workflow.score == 0
    assert workflow.iterations == 4


def test_lean_tolerance() -> None:
    workflow = chrisjen.Workflow.design(
        "lean",
        [make_step("a", add_one)],
        criteria=lambda r: min(r, 10) * 0.01,
        tolerance=0.05,
    )
    # Each pass improves the score by 0.01, which is below the tolerance.
    result = workflow.execute(0)
    assert workflow.iterations == 2
    assert result == 2


def test_iterative_designs_need_criteria() -> None:
    for design in ("agile", "lean", "contest"):
        workflow = chrisjen.Workflow.design(design, steps())
        with pytest.raises(ValueError, match="criteria"):
            workflow.execute(1)


""" Comparative designs """


def two_choice_steps() -> list[chrisjen.Step]:
    return [
        make_step("first", add_one, times_two),
        make_step("second", minus_three, add_one),
    ]


def test_contest_tries_every_combination() -> None:
    workflow = chrisjen.Workflow.design(
        "contest", two_choice_steps(), criteria=lambda r: r
    )
    result = workflow.execute(10)
    assert set(workflow.results) == {
        "add_one > minus_three",
        "add_one > add_one",
        "times_two > minus_three",
        "times_two > add_one",
    }
    assert result == 21
    assert workflow.winner == "times_two > add_one"
    assert workflow.scores["add_one > minus_three"] == 8


def test_contest_select_min_and_ties() -> None:
    workflow = chrisjen.Workflow.design(
        "contest", two_choice_steps(), criteria=lambda r: r, select="min"
    )
    assert workflow.execute(10) == 8
    assert workflow.winner == "add_one > minus_three"
    tied = chrisjen.Workflow.design(
        "contest", two_choice_steps(), criteria=lambda r: 0
    )
    tied.execute(10)
    assert tied.winner == "add_one > minus_three"


def test_contest_does_not_change_the_input() -> None:
    def append_x(item: list[str]) -> list[str]:
        item.append("x")
        return item

    workflow = chrisjen.Workflow.design(
        "contest",
        [make_step("a", append_x, append_x)],
        criteria=lambda r: len(r),
    )  # noqa: PLW0108
    original: list[str] = []
    workflow.execute(original)
    assert original == []


def test_contest_invalid_select() -> None:
    workflow = chrisjen.Workflow.design(
        "contest", steps(), criteria=lambda r: r, select="median"
    )
    with pytest.raises(ValueError, match="select"):
        workflow.execute(1)


def test_contest_named_criterion() -> None:
    @chrisjen.criterion
    def workflows_biggest(result: int) -> int:
        return result

    workflow = chrisjen.Workflow.design(
        "contest", two_choice_steps(), criteria="workflows_biggest"
    )
    assert workflow.execute(10) == 21
    missing = chrisjen.Workflow.design(
        "contest", two_choice_steps(), criteria="workflows_missing"
    )
    with pytest.raises(KeyError, match="not a registered criterion"):
        missing.execute(10)


def test_contest_between_workers() -> None:
    def branch(function: Any, name: str) -> chrisjen.Worker:
        inner = chrisjen.Workflow.design(
            "waterfall", [make_step(name, function)]
        )
        return chrisjen.Worker(name=name, contents=inner)

    workflow = chrisjen.Workflow.design(
        "contest",
        [branch(add_one, "slow"), branch(times_two, "fast")],
        criteria=lambda r: r,
    )
    assert workflow.execute(10) == 20
    assert workflow.winner == "fast"
    assert set(workflow.results) == {"slow", "fast"}


def test_survey_averages() -> None:
    workflow = chrisjen.Workflow.design("survey", two_choice_steps())
    # The four paths give 8, 12, 17, and 21.
    expected = (8 + 12 + 17 + 21) / 4
    assert workflow.execute(10) == expected
    assert len(workflow.results) == 4


def test_survey_of_a_single_path() -> None:
    workflow = chrisjen.Workflow.design("survey", steps())
    assert workflow.execute(1) == 4


def test_deepcopy_of_workflow_results_are_independent() -> None:
    workflow = chrisjen.Workflow.design("waterfall", steps())
    workflow.execute(1)
    clone = copy.deepcopy(workflow)
    clone.execute(100)
    assert workflow.results == {"a": 2, "b": 4}
