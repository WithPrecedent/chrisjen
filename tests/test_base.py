"""Tests the base module: the library, ideas, vertexes, and criteria."""

from __future__ import annotations

import abc
import dataclasses
import pathlib
from typing import Any

import pytest

import chrisjen
from chrisjen import base

SETTINGS = pathlib.Path(__file__).parent / 'cancer_settings.ini'


""" Library """


def test_the_library_of_the_package() -> None:
    contents = chrisjen.library.contents
    assert contents['idea'] is chrisjen.Idea
    assert contents['vertex']['technique'] is chrisjen.Technique
    assert contents['vertex']['none'] is chrisjen.NullVertex
    assert contents['vertex']['worker'] == {
        'flow': chrisjen.Flow,
        'benchmark': chrisjen.Benchmark,
        'contest': chrisjen.Contest,
        'survey': chrisjen.Survey,
    }
    assert contents['report'] == {'summary': chrisjen.Summary}
    assert contents['criteria'] == {}


def test_abstract_classes_form_genres() -> None:
    class Shelf(chrisjen.Genre, abc.ABC):
        pass

    class Fiction(Shelf, abc.ABC):
        pass

    class Novel(Fiction):
        pass

    class Mystery(Novel):
        pass

    class Poem(Shelf):
        pass

    assert chrisjen.library['shelf'] == {
        'fiction': {'novel': Novel, 'mystery': Mystery},
        'poem': Poem,
    }
    assert 'shelf' in chrisjen.library.genres
    assert 'fiction' in chrisjen.library.genres
    assert 'shelfs' in chrisjen.library.plurals
    assert chrisjen.library.all['mystery'] is Mystery


def test_adding_a_genre_again_keeps_its_layer() -> None:
    class Shelf(chrisjen.Genre, abc.ABC):
        pass

    class Novel(Shelf):
        pass

    chrisjen.library.add(Shelf)
    assert chrisjen.library['shelf'] == {'novel': Novel}


def test_add_errors() -> None:
    with pytest.raises(TypeError, match = 'subclass of Genre'):
        chrisjen.library.add(int)
    with pytest.raises(ValueError, match = 'Genre itself'):
        chrisjen.library.add(chrisjen.Genre)

    class Shelf(chrisjen.Genre, abc.ABC):
        pass

    with pytest.raises(ValueError, match = "'shelf' is already a genre"):
        type('Shelf', (chrisjen.Genre,), {})

    class Bookend(chrisjen.Genre):
        pass

    with pytest.raises(ValueError, match = "'bookend' is already a stored"):
        type('Bookend', (chrisjen.Genre, abc.ABC), {})


def test_add_with_a_name_and_other_ways_to_add() -> None:
    class Bookend(chrisjen.Genre):
        pass

    chrisjen.library.add(Bookend, name = 'stand')
    assert chrisjen.library['stand'] is Bookend
    chrisjen.library['prop'] = Bookend
    assert chrisjen.library['prop'] is Bookend
    assert (chrisjen.library + Bookend) is chrisjen.library
    chrisjen.library['shelf'] = {'novel': Bookend}
    assert chrisjen.library['shelf'] == {'novel': Bookend}


def test_classify() -> None:
    class Shelf(chrisjen.Genre, abc.ABC):
        pass

    class Fiction(Shelf, abc.ABC):
        pass

    class Novel(Fiction):
        pass

    class Bookend(chrisjen.Genre):
        pass

    assert chrisjen.library.classify('novel') == 'fiction'
    assert chrisjen.library.classify(Novel) == 'fiction'
    assert chrisjen.library.classify(Novel()) == 'fiction'
    assert chrisjen.library.classify('fiction') == 'shelf'
    assert chrisjen.library.classify(chrisjen.Contest) == 'worker'
    with pytest.raises(ValueError, match = 'not in a genre'):
        chrisjen.library.classify('shelf')
    with pytest.raises(ValueError, match = 'not in a genre'):
        chrisjen.library.classify(Bookend)
    with pytest.raises(ValueError, match = 'not in the library'):
        chrisjen.library.classify('nothing')
    with pytest.raises(ValueError, match = 'not in the library'):
        chrisjen.library.classify(int)


def test_delete() -> None:
    class Shelf(chrisjen.Genre, abc.ABC):
        pass

    class Fiction(Shelf, abc.ABC):
        pass

    class Novel(Fiction):
        pass

    class Poem(Shelf):
        pass

    del chrisjen.library['fiction']
    assert chrisjen.library['shelf'] == {'poem': Poem}
    chrisjen.library.delete('poem')
    assert chrisjen.library['shelf'] == {}
    with pytest.raises(KeyError, match = 'not in the library'):
        chrisjen.library.delete('nothing')


def test_get_genre() -> None:
    assert chrisjen.library.get_genre('worker')['flow'] is chrisjen.Flow
    assert chrisjen.library.get_genre(chrisjen.Report) == {
        'summary': chrisjen.Summary}
    with pytest.raises(KeyError, match = 'not a layer'):
        chrisjen.library.get_genre('flow')


def test_borrow() -> None:
    class Analyst(chrisjen.Contest):
        pass

    library = chrisjen.library
    assert library.borrow('flow') is chrisjen.Flow
    assert library.borrow(['analyst', 'flow'], genre = 'worker') is Analyst
    assert library.borrow(['critic', 'flow'], genre = 'worker') is chrisjen.Flow
    # Only classes in the genre are found.
    with pytest.raises(KeyError, match = "no class named 'technique'"):
        library.borrow('technique', genre = 'worker')
    with pytest.raises(KeyError, match = r"no class named \['a', 'b'\]"):
        library.borrow(['a', 'b'])


def test_a_separate_library() -> None:
    library = chrisjen.Library()
    library.add(chrisjen.Flow)
    assert library.contents == {'vertex': {'worker': {'flow': chrisjen.Flow}}}
    assert list(library) == ['vertex']
    assert len(library) == 1


""" Idea """


def test_idea_from_a_dict() -> None:
    idea = chrisjen.Idea.create({
        'general': {'verbose': True},
        'files': {'root': 'data'},
        'demo_project': {'demo_workers': 'prepare, model'},
        'prepare': {
            'steps': 'clean, scale',
            'clean_techniques': 'drop, none',
            'criterion': 'accuracy',
            'scale_criterion': 'variance',
        },
        'model': {'design': 'contest', 'techniques': ['forest', 'linear']},
        'scale_parameters': {'factor': 3},
    })
    assert isinstance(idea, chrisjen.Idea)
    assert list(idea.workers) == ['demo', 'prepare', 'model']
    assert idea.parameters == {'scale': {'factor': 3}}
    assert idea.designs == {
        'model': 'contest', 'demo': 'flow', 'prepare': 'flow'}
    assert idea.criteria == {'prepare': 'accuracy', 'scale': 'variance'}
    assert idea.steps == {
        'demo': ['prepare', 'model'], 'prepare': ['clean', 'scale']}
    assert idea.techniques == {
        'clean': ['drop', 'none'], 'model': ['forest', 'linear']}


def test_idea_from_a_file() -> None:
    idea = chrisjen.Idea.create(SETTINGS)
    assert list(idea.workers) == [
        'wisconsin_cancer', 'wrangler', 'analyst', 'critic']
    assert idea.designs == {
        'wisconsin_cancer': 'flow',
        'analyst': 'contest',
        'critic': 'flow',
        'wrangler': 'flow',
    }
    assert idea.steps['wisconsin_cancer'] == ['wrangler', 'analyst', 'critic']
    assert idea.techniques['scale'] == ['minmax', 'robust', 'normalize']
    assert idea.parameters['scaler']['n_bins'] == 5
    assert idea.criteria == {}


def test_get_settings() -> None:
    idea = chrisjen.Idea.create({
        'demo_project': {'max_iterations': 5, 'scale_copy': False},
        'model': {'max_iterations': 2, 'label': 'target'},
    })
    assert idea.get_settings('demo', ['max_iterations', 'label']) == {
        'max_iterations': 5}
    assert idea.get_settings('model', ['max_iterations', 'label']) == {
        'max_iterations': 2, 'label': 'target'}
    assert idea.get_settings('scale', ['copy']) == {'copy': False}
    assert idea.get_settings('other', ['copy']) == {}


def test_idea_ignores_settings_that_are_not_sections() -> None:
    idea = chrisjen.Idea.create({
        'version': 2,
        'demo_project': {'techniques': 'none'},
        'none_parameters': {'unused': True},
    })
    assert list(idea.workers) == ['demo']
    assert idea.parameters == {'none': {'unused': True}}


def test_steps_take_precedence_over_workers() -> None:
    idea = chrisjen.Idea.create(
        {'a_project': {'a_workers': 'x', 'steps': 'y'}})
    assert idea.steps == {'a': ['y']}


""" Vertex """


def test_vertexes_are_hashed_and_compared_by_name() -> None:
    first = chrisjen.Technique(name = 'same', contents = len)
    second = chrisjen.NullVertex(name = 'same')
    assert first == second
    assert hash(first) == hash('same')
    assert first == 'same'
    assert len({first, second}) == 1


def test_apply_merges_parameters() -> None:
    @dataclasses.dataclass
    class Adder(chrisjen.Vertex):
        def implement(self, item: Any, **kwargs: Any) -> Any:
            return item + kwargs.get('amount', 0)

    vertex = Adder(name = 'a', parameters = {'amount': 2})
    assert vertex.apply(1) == 3
    assert vertex.apply(1, amount = 10) == 11
    with pytest.raises(TypeError):
        chrisjen.Vertex()


def test_build_passes_settings_to_the_constructor() -> None:
    class Holder:
        idea = chrisjen.Idea.create({
            'grow_project': {'max_iterations': 3, 'unknown': 'skipped'},
            'grow_parameters': {'factor': 2},
        })

    bench = chrisjen.Benchmark.build('grow', Holder())
    assert bench.name == 'grow'
    assert bench.max_iterations == 3
    assert bench.parameters == {'factor': 2}
    # Arguments win over the settings.
    bench = chrisjen.Benchmark.build(
        'grow', Holder(), {'factor': 5}, max_iterations = 9)
    assert bench.max_iterations == 9
    assert bench.parameters == {'factor': 5}


""" Criteria """


def test_criteria_wraps_a_tool() -> None:
    criteria = chrisjen.Criteria(contents = sum)
    assert criteria.score([1, 2]) == 3
    assert criteria.test([1, 2])
    assert not criteria.test([])
    mean = chrisjen.Criteria(contents = 'statistics.fmean')
    assert mean.score([1, 2, 3]) == 2.0
    rounded = chrisjen.Criteria(contents = round, parameters = {'ndigits': 1})
    assert rounded.score(3.14159) == 3.1


def test_criteria_without_a_tool() -> None:
    with pytest.raises(NotImplementedError, match = 'no tool'):
        chrisjen.Criteria().score(1)


def test_criteria_subclasses() -> None:
    @dataclasses.dataclass
    class Positive(chrisjen.Criteria):
        def score(self, item: Any) -> Any:
            return item > 0

    assert chrisjen.library['criteria'] == {'positive': Positive}
    assert Positive().test(1)
    assert not Positive().test(-1)


def test_report_is_abstract() -> None:
    with pytest.raises(TypeError):
        base.Report()
