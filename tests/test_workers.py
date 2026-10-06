"""Tests the worker designs."""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

import chrisjen


def technique(name: str, function: Any) -> chrisjen.Technique:
    return chrisjen.Technique(name = name, contents = function)


def worker(design: type, nodes: list[Any], **kwargs: Any) -> Any:
    built = design(name = 'w', **kwargs)
    built.populate(nodes)
    return built


""" Flow """


def test_flow_applies_nodes_in_order() -> None:
    flow = worker(
        chrisjen.Flow,
        [
            technique('add', lambda x: x + 1),
            technique('double', lambda x: x * 2),
        ])
    assert flow.apply(1) == 4


def test_flow_passes_keyword_arguments_to_its_nodes() -> None:
    def shift(item: Any, amount: int = 0) -> Any:
        return item + amount

    flow = worker(chrisjen.Flow, [technique('shift', shift)])
    assert flow.apply(1, amount = 5) == 6
    flow.parameters = {'amount': 2}
    assert flow.apply(1) == 3


def test_a_list_in_a_flow_is_applied_in_order() -> None:
    flow = worker(
        chrisjen.Flow,
        [
            technique('add', lambda x: x + 1),
            [
                technique('double', lambda x: x * 2),
                technique('neg', lambda x: -x),
            ],
        ])
    assert [[node.name for node in path] for path in flow.walk()] == [
        ['add', 'double', 'neg']]
    assert flow.apply(1) == -4


def test_an_empty_flow_returns_the_item() -> None:
    assert chrisjen.Flow(name = 'empty').apply(5) == 5


def test_workers_of_workers() -> None:
    inner = worker(chrisjen.Flow, [technique('add', lambda x: x + 1)])
    inner.name = 'inner'
    outer = worker(
        chrisjen.Flow, [inner, technique('negate', lambda x: -x)])
    assert outer.apply(1) == -2


""" Benchmark """


def test_benchmark_repeats_until_the_criteria_is_met() -> None:
    bench = worker(
        chrisjen.Benchmark,
        [technique('double', lambda x: x * 2)],
        criteria = chrisjen.Criteria(contents = lambda x: x > 100))
    assert bench.apply(1) == 128
    assert bench.iterations == 7


def test_benchmark_stops_at_max_iterations() -> None:
    bench = worker(
        chrisjen.Benchmark,
        [technique('add', lambda x: x + 1)],
        criteria = chrisjen.Criteria(contents = lambda x: False),
        max_iterations = 3)
    assert bench.apply(0) == 3
    assert bench.iterations == 3


def test_benchmark_needs_criteria() -> None:
    with pytest.raises(ValueError, match = 'needs criteria'):
        chrisjen.Benchmark(name = 'b').apply(1)


""" Contest """


def test_contest_keeps_the_best_path() -> None:
    contest = worker(
        chrisjen.Contest,
        [[technique('half', lambda x: x / 2), chrisjen.NullVertex()]],
        criteria = chrisjen.Criteria(contents = lambda x: x))
    assert contest.apply(10) == 10
    assert contest.winner == 'none'
    assert contest.results == {'half': 5.0, 'none': 10}


def test_contest_tries_every_combination() -> None:
    contest = worker(
        chrisjen.Contest,
        [
            [
                technique('add', lambda x: x + 1),
                technique('double', lambda x: x * 2),
            ],
            [technique('negate', lambda x: -x), chrisjen.NullVertex()],
        ],
        criteria = chrisjen.Criteria(contents = lambda x: x))
    assert contest.apply(3) == 6
    assert contest.results == {
        'add > negate': -4,
        'add > none': 4,
        'double > negate': -6,
        'double > none': 6,
    }
    assert contest.winner == 'double > none'


def test_each_path_uses_its_own_copies_of_the_nodes() -> None:
    @dataclasses.dataclass
    class Counter(chrisjen.Technique):
        calls: int = 0

        def implement(self, item: Any, **kwargs: Any) -> Any:
            self.calls += 1
            return self.calls

    counter = Counter(name = 'counter')
    survey = worker(
        chrisjen.Survey,
        [counter, [technique('a', lambda x: x), technique('b', lambda x: x)]])
    assert survey.results == {}
    assert survey.apply(0) == 1
    assert survey.results == {'counter > a': 1, 'counter > b': 1}
    assert counter.calls == 0


def test_contest_ties_go_to_the_first_path() -> None:
    contest = worker(
        chrisjen.Contest,
        [[technique('a', lambda x: x), technique('b', lambda x: x)]],
        criteria = chrisjen.Criteria(contents = lambda x: 0))
    contest.apply(1)
    assert contest.winner == 'a'


def test_contest_does_not_change_the_input() -> None:
    def append(item: list[int]) -> list[int]:
        item.append(1)
        return item

    contest = worker(
        chrisjen.Contest,
        [[technique('a', append), technique('b', append)]],
        criteria = chrisjen.Criteria(contents = len))
    original: list[int] = []
    assert contest.apply(original) == [1]
    assert original == []


def test_contest_errors() -> None:
    with pytest.raises(ValueError, match = 'no paths'):
        chrisjen.Contest(name = 'c').apply(1)
    contest = worker(chrisjen.Contest, [technique('a', lambda x: x)])
    with pytest.raises(ValueError, match = 'needs criteria'):
        contest.apply(1)


""" Survey """


def test_survey_averages_the_paths() -> None:
    survey = worker(
        chrisjen.Survey,
        [[technique('half', lambda x: x / 2), chrisjen.NullVertex()]])
    assert survey.apply(4) == 3.0
    assert survey.average == 3.0
    assert survey.results == {'half': 2.0, 'none': 4}


def test_survey_of_paths_with_several_nodes() -> None:
    inner = worker(
        chrisjen.Flow,
        [technique('add', lambda x: x + 1), technique('add2', lambda x: x + 2)])
    inner.name = 'inner'
    survey = worker(chrisjen.Survey, [[inner, chrisjen.NullVertex()]])
    assert survey.apply(1) == 2.5
