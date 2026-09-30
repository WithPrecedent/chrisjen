"""Tests nodes and techniques."""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

import chrisjen


def nodes_double(item: Any) -> Any:
    return item * 2


chrisjen.Technique.register("nodes_double", nodes_double)


def _shift(item: Any, amount: int = 1) -> Any:
    return item + amount


chrisjen.Technique.register("nodes_shift", _shift)


def nodes_flexible(item: Any, **kwargs: Any) -> Any:
    return (item, kwargs)


chrisjen.Technique.register("nodes_flexible", nodes_flexible)


@dataclasses.dataclass
class NodesCube(chrisjen.Technique):
    def implement(self, item: Any, **kwargs: Any) -> Any:
        return item**3


def test_registered_function() -> None:
    technique = chrisjen.Technique.create("nodes_double")
    assert technique.name == "nodes_double"
    assert technique.complete(4) == 8
    assert nodes_double(4) == 8


def test_registered_name_and_parameters() -> None:
    technique = chrisjen.Technique.create(
        "nodes_shift", parameters = {"parameters": {"amount": 5}}
    )
    assert technique.complete(1) == 6
    assert technique.complete(1, amount = 10) == 11


def test_unaccepted_parameters_are_dropped() -> None:
    technique = chrisjen.Technique.create(
        "nodes_double", parameters = {"parameters": {"unused": 1}}
    )
    assert technique.complete(3) == 6
    flexible = chrisjen.Technique.create(
        "nodes_flexible", parameters = {"parameters": {"a": 1}}
    )
    assert flexible.complete(0, b = 2) == (0, {"a": 1, "b": 2})


def test_subclass_by_name() -> None:
    technique = chrisjen.Technique.create("nodes_cube")
    assert isinstance(technique, NodesCube)
    assert technique.complete(2) == 8


@pytest.mark.parametrize("alias", ["none", "null", "null_node"])
def test_null_node(alias: str) -> None:
    technique = chrisjen.Technique.create(alias)
    assert isinstance(technique, chrisjen.NullNode)
    assert technique.name == alias
    sentinel = object()
    assert technique.complete(sentinel) is sentinel


def test_unknown_technique() -> None:
    with pytest.raises(KeyError, match = "not a known technique"):
        chrisjen.Technique.create("nodes_missing")


def test_technique_without_function() -> None:
    technique = chrisjen.Technique(name = "empty")
    with pytest.raises(NotImplementedError, match = "no tool"):
        technique.complete(1)


def test_function_as_contents() -> None:
    technique = chrisjen.Technique(name = "inline", contents = lambda x: x + 1)
    assert technique.complete(1) == 2


def test_nodes_hash_and_compare_by_name() -> None:
    first = chrisjen.Technique(name = "same", contents = lambda x: x)
    second = NodesCube(name = "same")
    assert first == second
    assert hash(first) == hash(second)
    assert first == "same"
    assert first != chrisjen.Technique(name = "other")
    assert len({first, second}) == 1


def test_step_applies_techniques_in_order() -> None:
    step = chrisjen.Step(
        name = "step",
        contents = [
            chrisjen.Technique.create("nodes_double"),
            chrisjen.Technique.create("nodes_shift"),
        ],
    )
    assert step.complete(3) == 7
    assert [t.name for t in step.alternatives] == [
        "nodes_double",
        "nodes_shift",
    ]


def test_step_parameter_precedence() -> None:
    technique = chrisjen.Technique.create(
        "nodes_shift", parameters = {"parameters": {"amount": 2}}
    )
    step = chrisjen.Step(
        name = "step", contents = [technique], parameters = {"amount": 100}
    )
    # The technique's own parameters beat the step's.
    assert step.complete(0) == 2
    # Keyword arguments beat both.
    assert step.complete(0, amount = 7) == 7
    plain = chrisjen.Technique.create("nodes_shift")
    assert (
        chrisjen.Step(
            name = "plain", contents = [plain], parameters = {"amount": 4}
        ).complete(0)
        == 4
    )


def test_worker_needs_workflow() -> None:
    with pytest.raises(ValueError, match = "no workflow"):
        chrisjen.Worker(name = "worker").complete(1)


def test_node_alternatives_default() -> None:
    technique = chrisjen.Technique.create("nodes_double")
    assert technique.alternatives == [technique]
