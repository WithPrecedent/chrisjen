"""Tests edge cases of nodes, workflows, and projects."""

from __future__ import annotations

import dataclasses
import pathlib
from typing import Any

import pytest

import chrisjen


def technique(
    name: str, function: Any, **parameters: Any
) -> chrisjen.Technique:
    return chrisjen.Technique(
        name = name, contents = function, parameters = parameters
    )


def step(name: str, *functions: Any) -> chrisjen.Step:
    return chrisjen.Step(
        name = name,
        contents = [technique(f.__name__, f) for f in functions],
    )


def add_one(item: Any) -> Any:
    return item + 1


def times_two(item: Any) -> Any:
    return item * 2


def fail(item: Any) -> Any:
    message = "broken"
    raise RuntimeError(message)


def edge_add_one(item: Any) -> Any:
    return item + 1


chrisjen.Technique.register("edge_add_one", edge_add_one)


def edge_add_bonus(item: Any, bonus: int = 0) -> Any:
    return item + bonus


chrisjen.Technique.register("edge_add_bonus", edge_add_bonus)


def edge_log(item: Any, label: str = "x") -> Any:
    return [*item, label]


chrisjen.Technique.register("edge_log", edge_log)


""" Nodes """


def test_node_is_abstract() -> None:
    with pytest.raises(TypeError):
        chrisjen.Node()  # type: ignore[abstract]


def test_technique_created_by_name_can_be_renamed() -> None:
    created = chrisjen.Technique.create(
        "edge_add_one", parameters = {"name": "renamed"}
    )
    assert created.name == "renamed"
    assert created.complete(1) == 2


@dataclasses.dataclass
class EdgeShadow(chrisjen.Technique):
    def implement(self, item: Any, **kwargs: Any) -> Any:
        return "class"


def edge_shadow(item: Any) -> Any:
    return "function"


chrisjen.Technique.register("edge_shadow", edge_shadow)


def test_the_latest_registration_replaces_an_earlier_one() -> None:
    # The class was registered first, and the function replaced it.
    assert chrisjen.Technique.create("edge_shadow").complete(1) == "function"
    chrisjen.Technique.register("edge_shadow", EdgeShadow)  # type: ignore[arg-type]


@dataclasses.dataclass
class EdgeEcho(chrisjen.Technique):
    def implement(self, item: Any, **kwargs: Any) -> Any:
        return (item, kwargs)


def test_subclasses_receive_every_parameter() -> None:
    echo = chrisjen.Technique.create(
        "edge_echo", parameters = {"parameters": {"a": 1}}
    )
    assert echo.complete(0, b = 2) == (0, {"a": 1, "b": 2})
    assert echo.complete(0, a = 5) == (0, {"a": 5})


def test_null_node() -> None:
    node = chrisjen.NullNode()
    assert node.name == "none"
    item = object()
    assert node.complete(item, anything = 1) is item
    assert chrisjen.NullNode(name = "skip").name == "skip"


def test_register() -> None:
    def original(item: Any) -> Any:
        return "first"

    def replacement(item: Any) -> Any:
        return "second"

    registered = chrisjen.Technique.register("edge_swap", original)
    assert isinstance(registered, chrisjen.Technique)
    assert registered.contents is original
    assert chrisjen.Technique.create("edge_swap").complete(0) == "first"
    chrisjen.Technique.register("edge_swap", replacement)
    assert chrisjen.Technique.create("edge_swap").complete(0) == "second"
    chrisjen.Technique.register("edge_lambda", lambda item: item)
    assert chrisjen.Technique.create("edge_lambda").complete(3) == 3


def test_errors_in_techniques_are_not_hidden() -> None:
    with pytest.raises(RuntimeError, match = "broken"):
        technique("fail", fail).complete(1)
    workflow = chrisjen.Workflow.design("waterfall", [step("s", fail)])
    with pytest.raises(RuntimeError, match = "broken"):
        workflow.execute(1)


def test_nodes_are_not_equal_to_unrelated_objects() -> None:
    node = technique("same", add_one)
    assert node != 3
    assert node != object()
    assert node != "different"
    assert node == "same"
    assert {node: 1}["same"] == 1 if hash("same") == hash(node) else True


def test_step_without_techniques_passes_the_item_through() -> None:
    assert chrisjen.Step(name = "empty").complete("item") == "item"


def test_worker_passes_keyword_arguments_to_its_workflow() -> None:
    inner = chrisjen.Workflow.design(
        "waterfall",
        [
            chrisjen.Step(
                name = "s", contents = [chrisjen.Technique.create("edge_add_bonus")]
            )
        ],
    )
    worker = chrisjen.Worker(name = "w", contents = inner, parameters = {"bonus": 5})
    assert worker.complete(1) == 6
    assert worker.complete(1, bonus = 10) == 11


""" Workflows """


def test_results_are_replaced_on_each_execution() -> None:
    workflow = chrisjen.Workflow.design(
        "waterfall", [step("a", add_one), step("b", times_two)]
    )
    workflow.execute(1)
    workflow.results["stale"] = 0
    workflow.execute(2)
    assert workflow.results == {"a": 3, "b": 6}


def test_unknown_design_options_are_rejected() -> None:
    with pytest.raises(TypeError):
        chrisjen.Workflow.design("waterfall", [], bogus = 1)


def test_criteria_names_are_looked_up_when_executing() -> None:
    workflow = chrisjen.Workflow.design(
        "contest", [step("a", add_one, times_two)], criteria = "edge_later"
    )

    @chrisjen.criterion
    def edge_later(result: Any) -> Any:
        return -result

    assert workflow.execute(5) == 6


def test_scrum_keeps_its_place_after_an_error() -> None:
    workflow = chrisjen.Workflow.design(
        "scrum", [step("a", add_one), step("b", fail), step("c", times_two)]
    )
    item = workflow.advance(1)
    with pytest.raises(RuntimeError, match = "broken"):
        workflow.advance(item)
    assert workflow.position == 1
    assert workflow.upcoming == "b"
    assert not workflow.done


def test_scrum_upcoming_when_done() -> None:
    workflow = chrisjen.Workflow.design("scrum", [step("a", add_one)])
    workflow.advance(0)
    assert workflow.done
    assert workflow.upcoming is None


def test_lean_iteration_limits() -> None:
    def build(**options: Any) -> chrisjen.Workflow:
        return chrisjen.Workflow.design(
            "lean", [step("a", add_one)], criteria = lambda r: r, **options
        )

    once = build(max_iterations = 1)
    assert once.execute(0) == 1
    assert once.iterations == 1
    assert once.score == 1
    never = build(max_iterations = 0)
    assert never.execute(7) == 7
    assert never.iterations == 0
    assert never.score is None
    # Keeps going for as long as the score improves by more than the tolerance.
    assert build(max_iterations = 5).execute(0) == 5


def test_lean_returns_the_best_result_when_the_score_drops() -> None:
    workflow = chrisjen.Workflow.design(
        "lean", [step("a", add_one)], criteria = lambda r: -r
    )
    assert workflow.execute(0) == 1
    assert workflow.score == -1
    assert workflow.iterations == 2


def test_agile_iteration_limits() -> None:
    def build(**options: Any) -> chrisjen.Workflow:
        return chrisjen.Workflow.design(
            "agile", [step("a", add_one)], criteria = lambda r: r > 2, **options
        )

    assert build().execute(10) == 11
    quick = build()
    quick.execute(10)
    assert quick.iterations == 1
    idle = build(max_iterations = 0)
    assert idle.execute(0) == 0
    assert idle.iterations == 0


def test_keyword_arguments_reach_every_alternative() -> None:
    nodes = [
        chrisjen.Step(
            name = "a",
            contents = [
                chrisjen.Technique.create("edge_add_bonus"),
                chrisjen.Technique.create("edge_add_one"),
            ],
        )
    ]
    workflow = chrisjen.Workflow.design("contest", nodes, criteria = lambda r: r)
    assert workflow.execute(0, bonus = 10) == 10
    assert workflow.scores == {"edge_add_bonus": 10, "edge_add_one": 1}


def test_comparisons_need_paths() -> None:
    hollow = chrisjen.Step(name = "hollow")
    with pytest.raises(ValueError, match = "no paths"):
        chrisjen.Workflow.design(
            "contest", [hollow], criteria = lambda r: r
        ).execute(1)
    with pytest.raises(ValueError, match = "empty"):
        chrisjen.Workflow.design("survey", [hollow]).execute(1)


def test_a_comparison_of_steps_and_workers_treats_each_node_as_a_path() -> None:
    inner = chrisjen.Workflow.design("waterfall", [step("i", times_two)])
    nodes = [
        step("plain", add_one),
        chrisjen.Worker(name = "worker", contents = inner),
    ]
    workflow = chrisjen.Workflow.design("contest", nodes, criteria = lambda r: r)
    assert workflow.execute(10) == 20
    assert workflow.results == {"plain": 11, "worker": 20}


def test_comparisons_do_not_change_the_input() -> None:
    def append(item: list[int]) -> list[int]:
        item.append(len(item))
        return item

    workflow = chrisjen.Workflow.design(
        "contest", [step("a", append)], criteria = len
    )
    original = [0]
    assert workflow.execute(original) == [0, 1]
    assert original == [0]


def test_compare_returns_labeled_results() -> None:
    workflow = chrisjen.Workflow.design(
        "contest", [step("a", add_one, times_two)], criteria = lambda r: r
    )
    assert workflow.compare(3) == {"add_one": 4, "times_two": 6}
    assert workflow.results == {"add_one": 4, "times_two": 6}


def test_pert_picks_the_longest_of_separate_chains() -> None:
    nodes = [step(name, add_one) for name in ("a", "b", "c", "d")]
    workflow = chrisjen.Workflow.design(
        "pert",
        nodes,
        requirements = {"b": ["a"], "d": ["c"]},
        durations = {"a": 1, "b": 1, "c": 5, "d": 1},
    )
    assert sorted(map(tuple, workflow.walk())) == [("a", "b"), ("c", "d")]
    assert workflow.critical_path() == (["c", "d"], 6)
    assert workflow.order() == ["a", "b", "c", "d"]


def test_pert_durations_default_to_one() -> None:
    nodes = [step(name, add_one) for name in ("a", "b", "c")]
    workflow = chrisjen.Workflow.design("pert", nodes, durations = {"b": 2.5})
    assert workflow.critical_path() == (["a", "b", "c"], 4.5)


def test_single_node_workflow() -> None:
    workflow = chrisjen.Workflow.design("pert", [step("only", add_one)])
    assert workflow.walk() == [["only"]]
    assert workflow.critical_path() == (["only"], 1.0)
    assert workflow.execute(1) == 2


""" Projects """


def test_project_name_argument() -> None:
    settings = {
        "first_project": {"first_workers": "w"},
        "second_project": {"second_workers": "w"},
        "w": {"w_techniques": "edge_add_one"},
    }
    assert chrisjen.Project(settings).name == "first"
    project = chrisjen.Project(settings, name = "second")
    assert project.name == "second"
    assert project.outline.name == "second"
    assert project.identification.startswith("second_")


def test_falsy_items_are_applied() -> None:
    settings = {
        "x_project": {"x_workers": "w"},
        "w": {"w_techniques": "edge_add_one"},
    }
    project = chrisjen.Project(settings, item = 100)
    assert project.apply(0) == 1
    assert chrisjen.Project(settings, item = 0).apply() == 1


def test_applying_without_an_item() -> None:
    settings = {
        "x_project": {"x_workers": "w"},
        "w": {"w_techniques": "none"},
    }
    project = chrisjen.Project(settings, automatic = True)
    assert project.result is None


def test_publishing_again_builds_a_new_workflow() -> None:
    settings = {
        "x_project": {"x_workers": "w"},
        "w": {"w_techniques": "edge_add_one"},
    }
    project = chrisjen.Project(settings, item = 1)
    first = project.publish()
    second = project.publish()
    assert first is not second
    assert project.workflow is second
    assert project.apply() == 2


def test_summary_before_and_after_publishing() -> None:
    settings = {
        "x_project": {"x_workers": "w"},
        "w": {"w_techniques": "none"},
    }
    project = chrisjen.Project(settings)
    assert "critical path" not in project.summary
    assert project.summary.startswith("x (waterfall)")
    project.publish()
    assert project.summary.endswith("critical path: w (1.0)")


def test_unknown_project_design() -> None:
    settings = {
        "x_project": {"x_workers": "w", "design": "spiral"},
        "w": {"w_techniques": "none"},
    }
    project = chrisjen.Project(settings)
    with pytest.raises(KeyError, match = "spiral"):
        project.publish()


def test_typed_parameters_from_an_ini_file(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "settings.ini"
    path.write_text(
        "[x_project]\n"
        "x_workers = w\n"
        "[w]\n"
        "w_techniques = edge_add_bonus\n"
        "[edge_add_bonus_parameters]\n"
        "bonus = 7\n",
        encoding = "utf-8",
    )
    project = chrisjen.Project(str(path), item = 1)
    assert project.outline.parameters == {"edge_add_bonus": {"bonus": 7}}
    assert project.apply() == 8


def test_python_settings_file(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "settings.py"
    path.write_text(
        "settings = {\n"
        "    'x_project': {'x_workers': 'w'},\n"
        "    'w': {'w_techniques': 'edge_add_one'},\n"
        "}\n",
        encoding = "utf-8",
    )
    assert chrisjen.Project(path, item = 1).apply() == 2


def test_the_default_root_folder_is_in_the_working_directory(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    settings = {
        "x_project": {"x_workers": "w"},
        "w": {"w_techniques": "none"},
    }
    project = chrisjen.Project(settings, identification = "run")
    assert not (tmp_path / "data").exists()
    project.clerk  # noqa: B018
    assert (tmp_path / "data" / "run" / "input").is_dir()
    assert (tmp_path / "data" / "run" / "output").is_dir()


def test_keyword_arguments_reach_techniques_in_every_worker() -> None:
    settings = {
        "x_project": {"x_workers": ["one", "two"]},
        "one": {"one_techniques": "edge_add_bonus"},
        "two": {"two_techniques": "edge_add_bonus"},
    }
    assert chrisjen.Project(settings, item = 0).apply(bonus = 3) == 6


def test_a_project_of_workers_with_requirements() -> None:
    settings = {
        "x_project": {
            "x_workers": ["prepare", "left", "right", "finish"],
            "design": "pert",
            "left_requires": "prepare",
            "right_requires": "prepare",
            "finish_requires": "left, right",
        },
        "prepare": {"prepare_techniques": "edge_log"},
        "left": {"left_techniques": "edge_log"},
        "right": {"right_techniques": "edge_log"},
        "finish": {"finish_techniques": "edge_log"},
        "left_parameters": {"duration": 4, "label": "left"},
        "right_parameters": {"duration": 1, "label": "right"},
        "prepare_parameters": {"label": "prepare"},
        "finish_parameters": {"label": "finish"},
    }
    project = chrisjen.Project(settings, item = [])
    assert project.outline.requirements == {
        "x": {
            "left": ["prepare"],
            "right": ["prepare"],
            "finish": ["left", "right"],
        }
    }
    project.publish()
    assert project.workflow.critical_path() == (
        ["prepare", "left", "finish"],
        6.0,
    )
    assert sorted(map(tuple, project.workflow.walk())) == [
        ("prepare", "left", "finish"),
        ("prepare", "right", "finish"),
    ]
    assert project.apply() == ["prepare", "left", "right", "finish"]


def test_project_level_requirements_must_name_workers() -> None:
    settings = {
        "x_project": {
            "x_workers": ["a", "b"],
            "design": "pert",
            "b_requires": "nobody",
        },
        "a": {"a_techniques": "none"},
        "b": {"b_techniques": "none"},
    }
    project = chrisjen.Project(settings)
    with pytest.raises(KeyError, match = "nobody"):
        project.publish()


def test_project_settings_that_are_not_used_by_chrisjen_are_kept() -> None:
    settings = {
        "x_project": {"x_workers": "w", "author": "me"},
        "w": {"w_techniques": "none", "note": "hello", "w_requires": "x"},
        "general": {"seed": 4},
    }
    outline = chrisjen.Project(settings).outline
    assert outline.initialization == {
        "x": {"author": "me"},
        "w": {"note": "hello"},
    }


def test_exports_publish_the_project_if_needed(tmp_path: pathlib.Path) -> None:
    settings = {
        "x_project": {"x_workers": ["a", "b"]},
        "a": {"a_techniques": "none"},
        "b": {"b_techniques": "none"},
    }
    project = chrisjen.Project(settings)
    assert project.workflow is None
    mermaid = project.to_mermaid(path = tmp_path / "flow.mmd", name = "renamed")
    assert project.workflow is not None
    assert (tmp_path / "flow.mmd").read_text(encoding = "utf-8") == mermaid
    assert "title: renamed" in mermaid
    assert "a(a) --> b(b)" in mermaid
    # The workflow is not rebuilt for a second export.
    workflow = project.workflow
    dot = project.to_dot(name = "again")
    assert project.workflow is workflow
    assert dot.startswith('digraph "again" {')
    fresh = chrisjen.Project(settings)
    assert fresh.to_dot().startswith('digraph "x" {')
    assert fresh.workflow is not None


def test_lean_stops_when_the_improvement_equals_the_tolerance() -> None:
    # The score goes up by exactly 1 on each pass, which is not *more* than
    # the tolerance, so a second pass is the last one.
    workflow = chrisjen.Workflow.design(
        "lean",
        [step("a", add_one)],
        criteria = lambda r: r,
        tolerance = 1,
    )
    assert workflow.execute(0) == 2
    assert workflow.iterations == 2
    # A smaller tolerance lets it keep going (to the limit).
    keeps_going = chrisjen.Workflow.design(
        "lean",
        [step("a", add_one)],
        criteria = lambda r: r,
        tolerance = 0.99,
        max_iterations = 4,
    )
    assert keeps_going.execute(0) == 4
    assert keeps_going.iterations == 4


def test_lean_keeps_the_earlier_result_when_scores_tie() -> None:
    def copy_list(item: list[int]) -> list[int]:
        return [*item]

    workflow = chrisjen.Workflow.design(
        "lean", [step("a", copy_list)], criteria = lambda r: 0
    )
    result = workflow.execute([1])
    assert workflow.iterations == 2
    # The second pass tied, so its result (the last one saved) was not kept.
    assert result is not workflow.results["a"]
    assert result == workflow.results["a"]
