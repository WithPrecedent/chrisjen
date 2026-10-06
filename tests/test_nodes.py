"""Tests the nodes module: techniques, null vertexes, steps, and workers."""

from __future__ import annotations

import copy
import dataclasses
import threading
from typing import Any

import pytest

import chrisjen


def add_one(item: Any) -> Any:
    return item + 1


""" Technique """


def test_technique_wraps_a_callable_or_an_import_path() -> None:
    assert chrisjen.Technique(name = 't', contents = add_one).apply(1) == 2
    mean = chrisjen.Technique(name = 'm', contents = 'statistics.fmean')
    assert mean.apply([1, 2, 3, 6]) == 3.0
    colon = chrisjen.Technique(name = 'm', contents = 'statistics:fmean')
    assert colon.apply([2, 4]) == 3.0


def test_technique_parameters_are_filtered_for_the_tool() -> None:
    rounded = chrisjen.Technique(
        name = 'round',
        contents = round,
        parameters = {'ndigits': 1, 'unused': True},
    )
    assert rounded.apply(3.14159) == 3.1
    assert rounded.apply(3.14159, ndigits = 3) == 3.142


def test_technique_errors() -> None:
    with pytest.raises(NotImplementedError, match = 'no tool'):
        chrisjen.Technique(name = 'empty').apply(1)
    with pytest.raises(TypeError, match = 'not callable'):
        chrisjen.Technique(name = 'constant', contents = 5).apply(1)
    with pytest.raises(ImportError, match = 'no_such_package'):
        chrisjen.Technique(name = 'x', contents = 'no_such_package.x').apply(1)


def test_technique_subclasses_override_implement() -> None:
    @dataclasses.dataclass
    class Cube(chrisjen.Technique):
        def implement(self, item: Any, **kwargs: Any) -> Any:
            return item**3

    assert Cube(name = 'cube').apply(2) == 8
    assert chrisjen.library['vertex']['cube'] is Cube


def test_a_technique_is_copied_with_its_tool() -> None:
    class Guarded:
        def __init__(self) -> None:
            self.lock = threading.Lock()

        def __call__(self, item: Any) -> Any:
            return item

    counter = [0]
    technique = chrisjen.Technique(
        name = 'c', contents = counter.append, parameters = {'a': [1]})
    clone = copy.deepcopy(technique)
    assert clone.parameters['a'] is not technique.parameters['a']
    tool = Guarded()
    shared = copy.deepcopy(chrisjen.Technique(name = 'g', contents = tool))
    assert shared.contents is tool
    # Only the tool in contents may be shared. Other fields must be copied.
    locked = chrisjen.Technique(
        name = 'l', parameters = {'lock': threading.Lock()})
    with pytest.raises(TypeError):
        copy.deepcopy(locked)


""" NullVertex """


def test_null_vertex() -> None:
    sentinel = object()
    assert chrisjen.NullVertex().name == 'none'
    assert chrisjen.NullVertex().apply(sentinel, anything = 1) is sentinel
    assert chrisjen.library.all['none'] is chrisjen.NullVertex


""" Step """


def test_step_applies_its_contents_between_begin_and_end() -> None:
    calls: list[str] = []

    @dataclasses.dataclass
    class Logged(chrisjen.Step):
        def begin(self, item: Any) -> Any:
            calls.append('begin')
            return item + 100

        def end(self, item: Any) -> Any:
            calls.append('end')
            return item * 2

    step = Logged(
        name = 'l',
        contents = chrisjen.Technique(name = 'a', contents = add_one))
    assert step.apply(1) == (1 + 100 + 1) * 2
    assert calls == ['begin', 'end']


def test_step_parameter_priority() -> None:
    def shift(item: Any, amount: int = 1) -> Any:
        return item + amount

    technique = chrisjen.Technique(
        name = 't', contents = shift, parameters = {'amount': 2})
    assert chrisjen.Step(name = 's', contents = technique).apply(0) == 2
    step = chrisjen.Step(
        name = 's', contents = technique, parameters = {'amount': 5})
    assert step.apply(0) == 5
    assert step.apply(0, amount = 7) == 7


def test_step_returns_the_attributes_of_its_contents() -> None:
    @dataclasses.dataclass
    class Model(chrisjen.Technique):
        kind: str = 'forest'

        def implement(self, item: Any, **kwargs: Any) -> Any:
            return item

    step = chrisjen.Step(name = 's', contents = Model(name = 'm'))
    assert step.kind == 'forest'
    assert step.name == 's'
    with pytest.raises(AttributeError):
        step.missing  # noqa: B018
    with pytest.raises(AttributeError):
        chrisjen.Step(name = 'e').kind  # noqa: B018
    clone = copy.deepcopy(step)
    assert type(clone) is chrisjen.Step
    assert clone.contents is not step.contents
    assert clone.kind == 'forest'


def test_step_without_contents() -> None:
    with pytest.raises(ValueError, match = "step 'e' has no technique"):
        chrisjen.Step(name = 'e').apply(1)


""" Worker """


def test_worker_is_abstract_and_hashed_by_name() -> None:
    with pytest.raises(TypeError):
        chrisjen.Worker(name = 'w')
    for design in (
        chrisjen.Flow, chrisjen.Benchmark, chrisjen.Contest, chrisjen.Survey):
        worker = design(name = 'w')
        assert hash(worker) == hash('w')
        assert worker == 'w'


def test_populate_connects_nodes_in_sequence() -> None:
    nodes = [
        chrisjen.Technique(name = name, contents = add_one)
        for name in ('a', 'b', 'c')]
    flow = chrisjen.Flow(name = 'f')
    flow.populate(nodes)
    assert flow.walk() == [nodes]
    assert flow.root == [nodes[0]]
    assert flow.endpoint == [nodes[2]]
