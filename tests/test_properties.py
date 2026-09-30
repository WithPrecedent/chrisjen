"""Tests chrisjen against simple reference calculations on random inputs.

The random numbers are seeded, so every run checks the same cases.
"""

from __future__ import annotations

import abc
import itertools
import random
from collections.abc import Callable
from typing import Any

import pytest

import chrisjen

SEEDS = range(150)
TECHNIQUES: dict[str, Callable[[int], int]] = {}
for amount in range(1, 5):
    TECHNIQUES[f"prop_add_{amount}"] = lambda item, amount = amount: item + amount
    TECHNIQUES[f"prop_mul_{amount}"] = lambda item, amount = amount: item * amount
for _name, _function in TECHNIQUES.items():
    chrisjen.Technique.register(_name, _function)
STEP_NAMES = ["clean", "scale", "fit", "check", "report"]


def fold(functions: list[Callable[[int], int]], item: int) -> int:
    for function in functions:
        item = function(item)
    return item


def make_steps(plan: list[list[str]], names: list[str]) -> list[chrisjen.Step]:
    return [
        chrisjen.Step(
            name = name,
            contents = [chrisjen.Technique.create(t) for t in techniques],
        )
        for name, techniques in zip(names, plan, strict = True)
    ]


def random_plan(random_: random.Random) -> list[list[str]]:
    return [
        random_.choices(list(TECHNIQUES), k = random_.randint(1, 3))
        for _ in range(random_.randint(1, 4))
    ]


""" Graphs """


def random_requirements(
    random_: random.Random, names: list[str]
) -> dict[str, list[str]]:
    """Returns requirements that point only at earlier names, so no cycles."""
    requirements: dict[str, list[str]] = {}
    for index, name in enumerate(names[1:], start = 1):
        chosen = [n for n in names[:index] if random_.random() < 0.4]
        if chosen:
            requirements[name] = chosen
    return requirements


@pytest.mark.parametrize("seed", SEEDS)
def test_pert_order_and_critical_path(seed: int) -> None:
    random_ = random.Random(seed)
    names = STEP_NAMES[: random_.randint(1, len(STEP_NAMES))]
    requirements = random_requirements(random_, names)
    durations = {n: random_.randint(1, 9) for n in names}
    log: list[str] = []

    def recorder(name: str) -> Callable[[int], int]:
        def record(item: int) -> int:
            log.append(name)
            return item + 1

        return record

    nodes = [
        chrisjen.Step(
            name = name,
            contents = [chrisjen.Technique(name = name, contents = recorder(name))],
        )
        for name in names
    ]
    workflow = chrisjen.Workflow.design(
        "pert", nodes, requirements = requirements, durations = durations
    )
    order = workflow.order()
    assert sorted(order) == sorted(names)
    for name, required in requirements.items():
        for other in required:
            assert order.index(other) < order.index(name)
    # Every node runs exactly once, in a valid order.
    assert workflow.execute(0) == len(names)
    assert log == order
    # The critical path is the longest path from a root to an endpoint.
    path, total = workflow.critical_path()
    lengths = [
        sum(durations[node] for node in walked) for walked in workflow.walk()
    ]
    assert total == max(lengths)
    assert sum(durations[node] for node in path) == total
    assert path in workflow.walk()


""" Designs """


@pytest.mark.parametrize("seed", SEEDS)
def test_sequential_designs_agree_with_a_plain_loop(seed: int) -> None:
    random_ = random.Random(seed)
    plan = random_plan(random_)
    names = STEP_NAMES[: len(plan)]
    functions = [TECHNIQUES[t] for techniques in plan for t in techniques]
    item = random_.randint(-5, 5)
    expected = fold(functions, item)
    for design in ("waterfall", "kanban", "scrum", "pert", "sequential"):
        workflow = chrisjen.Workflow.design(design, make_steps(plan, names))
        assert workflow.execute(item) == expected, design


@pytest.mark.parametrize("seed", SEEDS)
def test_contest_and_survey_agree_with_brute_force(seed: int) -> None:
    random_ = random.Random(seed)
    plan = random_plan(random_)
    names = STEP_NAMES[: len(plan)]
    item = random_.randint(-5, 5)
    paths = list(itertools.product(*plan))
    results = [fold([TECHNIQUES[t] for t in path], item) for path in paths]
    # A contest returns the best result.
    for select, choose in (("max", max), ("min", min)):
        contest = chrisjen.Workflow.design(
            "contest",
            make_steps(plan, names),
            criteria = lambda r: r,
            select = select,
        )
        assert contest.execute(item) == choose(results)
        assert sorted(contest.scores.values()) == sorted(results)
        assert len(contest.results) == len(paths)
    # A survey returns the mean of all of the results.
    survey = chrisjen.Workflow.design("survey", make_steps(plan, names))
    assert survey.execute(item) == pytest.approx(sum(results) / len(results))


@pytest.mark.parametrize("seed", SEEDS)
def test_iterative_designs_agree_with_a_plain_loop(seed: int) -> None:
    random_ = random.Random(seed)
    plan = random_plan(random_)
    names = STEP_NAMES[: len(plan)]
    functions = [TECHNIQUES[t] for techniques in plan for t in techniques]
    item = random_.randint(1, 5)
    limit = random_.randint(1, 6)
    target = random_.randint(5, 200)
    # Agile repeats until the criterion is met or the limit is reached.
    expected = item
    passes = 0
    while passes < limit:
        expected = fold(functions, expected)
        passes += 1
        if expected >= target:
            break
    agile = chrisjen.Workflow.design(
        "agile",
        make_steps(plan, names),
        criteria = lambda r: r >= target,
        max_iterations = limit,
    )
    assert agile.execute(item) == expected
    assert agile.iterations == passes


""" Projects """


@pytest.mark.parametrize("seed", SEEDS)
def test_random_projects_agree_with_a_plain_calculation(seed: int) -> None:
    random_ = random.Random(seed)
    worker_names = [f"worker_{i}" for i in range(random_.randint(1, 3))]
    settings: dict[str, Any] = {"prop_project": {"prop_workers": worker_names}}
    designs = ["waterfall", "kanban", "scrum", "pert", "contest", "survey"]
    item = random_.randint(-5, 5)
    expected = item
    for worker in worker_names:
        # Workers may reuse the names of steps in other workers.
        names = random_.sample(STEP_NAMES, random_.randint(1, 3))
        plan = [
            random_.choices(list(TECHNIQUES), k = random_.randint(1, 2))
            for _ in names
        ]
        design = random_.choice(designs)
        section: dict[str, Any] = {f"{worker}_steps": names, "design": design}
        for name, techniques in zip(names, plan, strict = True):
            section[f"{name}_techniques"] = techniques
        if design in {"contest", "survey"}:
            section["criteria"] = "prop_largest"
        settings[worker] = section
        results = [
            fold([TECHNIQUES[t] for t in path], expected)
            for path in itertools.product(*plan)
        ]
        if design == "contest":
            expected = max(results)
        elif design == "survey":
            expected = sum(results) / len(results)
        else:
            expected = fold(
                [TECHNIQUES[t] for techniques in plan for t in techniques],
                expected,
            )
    project = chrisjen.Project(settings, item = item)
    assert project.outline.workers == worker_names
    for worker in worker_names:
        assert (
            project.outline.steps[worker] == settings[worker][f"{worker}_steps"]
        )
    assert project.apply() == pytest.approx(expected)
    # The project can be applied again with the same result.
    assert project.apply() == pytest.approx(expected)


@chrisjen.criterion
def prop_largest(result: Any) -> Any:
    return result


""" Types of techniques """


class PropAdd(chrisjen.Technique, abc.ABC):
    """Adds the amount in the name."""


class PropMul(chrisjen.Technique, abc.ABC):
    """Multiplies by the amount in the name."""


for _amount in range(1, 5):
    PropAdd.register(f"op_{_amount}", lambda item, _a = _amount: item + _a)
    PropMul.register(f"op_{_amount}", lambda item, _a = _amount: item * _a)
OPERATIONS = {
    "prop_add": lambda item, amount: item + amount,
    "prop_mul": lambda item, amount: item * amount,
}


@pytest.mark.parametrize("seed", SEEDS)
def test_the_type_of_a_step_chooses_which_technique_is_used(seed: int) -> None:
    random_ = random.Random(seed)
    steps = STEP_NAMES[: random_.randint(1, 4)]
    section: dict[str, Any] = {"w_steps": steps}
    item = random_.randint(-5, 5)
    expected = item
    for step in steps:
        kind = random_.choice(["prop_add", "prop_mul"])
        amounts = random_.choices(range(1, 5), k = random_.randint(1, 3))
        section[f"{step}_techniques"] = [f"op_{a}" for a in amounts]
        # Half of the steps write the type in the names instead.
        if random_.random() < 0.5:
            section[f"{step}_technique_type"] = kind
        else:
            section[f"{step}_techniques"] = [f"{kind}.op_{a}" for a in amounts]
        for amount in amounts:
            expected = OPERATIONS[kind](expected, amount)
    settings = {"prop_project": {"prop_workers": ["w"]}, "w": section}
    assert chrisjen.Project(settings, item = item).apply() == expected


def test_names_in_both_types_need_a_type() -> None:
    settings = {
        "prop_project": {"prop_workers": ["w"]},
        "w": {"w_techniques": "op_1"},
    }
    with pytest.raises(KeyError, match = "more than one type"):
        chrisjen.Project(settings, item = 1).publish()
