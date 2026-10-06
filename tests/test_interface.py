"""Tests building and running a project from its settings."""

from __future__ import annotations

import dataclasses
import itertools
import pathlib
import sys
import types
from collections.abc import Iterator
from typing import Any

import nagata
import pytest

import chrisjen
from chrisjen import workshop

SETTINGS = pathlib.Path(__file__).parent / 'cancer_settings.ini'


@pytest.fixture(autouse = True)
def techniques() -> Iterator[None]:
    """Adds the techniques used by the settings below to the library."""

    @dataclasses.dataclass
    class DropNegatives(chrisjen.Technique):
        def implement(self, item: Any, **kwargs: Any) -> Any:
            return [x for x in item if x >= 0]

    @dataclasses.dataclass
    class Scale(chrisjen.Technique):
        def implement(self, item: Any, factor: int = 1, **kwargs: Any) -> Any:
            return [x * factor for x in item]

    @dataclasses.dataclass
    class Halve(chrisjen.Technique):
        def implement(self, item: Any, **kwargs: Any) -> Any:
            return [x / 2 for x in item]

    # A scoring function that settings can name by its import path.
    module = types.ModuleType('chrisjen_test_scores')
    module.total = sum  # type: ignore[attr-defined]
    module.never = lambda item: False  # type: ignore[attr-defined]
    sys.modules['chrisjen_test_scores'] = module
    yield
    del sys.modules['chrisjen_test_scores']


def settings() -> dict[str, Any]:
    return {
        'demo_project': {'demo_workers': 'prepare, model'},
        'prepare': {'steps': 'drop_negatives, scale'},
        'model': {
            'design': 'contest',
            'criterion': 'chrisjen_test_scores.total',
            'techniques': 'halve, none',
        },
        'scale_parameters': {'factor': 3},
    }


def create(tmp_path: pathlib.Path, **kwargs: Any) -> chrisjen.Project:
    return chrisjen.Project.create(
        settings(), name = 'demo', clerk = tmp_path, **kwargs)


""" Project """


def test_project_builds_and_applies_the_workflow(
    tmp_path: pathlib.Path,
) -> None:
    project = create(tmp_path, item = [1, -2, 3])
    assert project.name == 'demo'
    assert project.id.startswith('demo_')
    assert [[n.name for n in p] for p in project.workflow.walk()] == [
        ['prepare', 'model']]
    assert project.result == [3, 9]


def test_a_project_that_is_not_automatic(tmp_path: pathlib.Path) -> None:
    project = create(tmp_path, automatic = False)
    assert project.result is None
    assert project.apply([2, -1]) == [6]
    assert project.result == [6]


def test_project_report(tmp_path: pathlib.Path) -> None:
    project = create(tmp_path, item = [1])
    assert isinstance(project.report, chrisjen.Summary)
    assert project.report.contents.splitlines() == [
        'project: demo',
        f'id: {project.id}',
        'paths: prepare > model',
        'result: [3]',
    ]


def test_project_exports(tmp_path: pathlib.Path) -> None:
    project = create(tmp_path, automatic = False)
    assert 'prepare(prepare) --> model(model)' in project.to_mermaid()
    assert 'title: demo' in project.to_mermaid()
    assert project.to_dot() == 'digraph demo {\nprepare -> model\n}\n'


def test_project_clerk(tmp_path: pathlib.Path) -> None:
    project = create(tmp_path, automatic = False)
    assert isinstance(project.clerk, nagata.FileManager)
    clerk = nagata.FileManager(root_folder = tmp_path)
    project = chrisjen.Project.create(
        settings(), name = 'demo', clerk = clerk, automatic = False)
    assert project.clerk is clerk


def test_project_name_is_found_in_the_settings(
    tmp_path: pathlib.Path,
) -> None:
    project = chrisjen.Project.create(
        settings(), clerk = tmp_path, automatic = False)
    assert project.name == 'demo'
    unnamed = {'files': {}, 'prepare': {'techniques': 'none'}}
    project = chrisjen.Project.create(
        unnamed, clerk = tmp_path, automatic = False)
    assert project.name == 'prepare'
    with pytest.raises(ValueError, match = 'could not be found'):
        chrisjen.Project.create({'files': {}}, clerk = tmp_path)


def test_project_from_an_idea_and_an_id(tmp_path: pathlib.Path) -> None:
    idea = chrisjen.Idea.create(settings())
    project = chrisjen.Project.create(
        idea, name = 'demo', id = 'run', clerk = tmp_path, automatic = False)
    assert project.idea is idea
    assert project.id == 'run'


def test_project_from_an_idea_class(tmp_path: pathlib.Path) -> None:
    project = chrisjen.Project.create(
        chrisjen.Idea, name = 'empty', clerk = tmp_path, item = 5)
    assert isinstance(project.idea, chrisjen.Idea)
    assert isinstance(project.workflow, chrisjen.Flow)
    assert project.result == 5


def test_project_with_a_workflow(tmp_path: pathlib.Path) -> None:
    workflow = chrisjen.Flow(name = 'given')
    workflow.populate([chrisjen.NullVertex()])
    project = create(tmp_path, workflow = workflow, item = [1, -2])
    # The workflow is used instead of one built from the settings.
    assert project.workflow is workflow
    assert project.result == [1, -2]


def paths(worker: chrisjen.Worker) -> list[list[str]]:
    return [[node.name for node in path] for path in worker.walk()]


def test_workflow_from_the_cancer_settings(tmp_path: pathlib.Path) -> None:
    # Techniques whose snake case names match the names in the settings.
    for name in (
        'minmax', 'robust', 'normalize', 'stratified_kfold', 'train_test',
        'target', 'weight_of_evidence', 'one_hot', 'james_stein', 'smote',
        'xgboost', 'logit', 'random_forest', 'shap', 'sklearn'):
        type(name, (chrisjen.Technique,), {})
    project = chrisjen.Project.create(
        SETTINGS, clerk = tmp_path, automatic = False)
    workflow = project.workflow
    assert project.name == 'wisconsin_cancer'
    assert isinstance(workflow, chrisjen.Flow)
    assert workflow.name == 'wisconsin_cancer'
    assert paths(workflow) == [['wrangler', 'analyst', 'critic']]
    workers = {node.name: node for node in workflow}
    # The wrangler has one technique and no steps.
    assert isinstance(workers['wrangler'], chrisjen.Flow)
    assert paths(workers['wrangler']) == [['none']]
    assert isinstance(
        next(iter(workers['wrangler'])), chrisjen.NullVertex)
    # The analyst is a contest of every combination of one technique from
    # each of its steps. Each node is a step that wraps one technique, and the
    # techniques of steps that are not listed in `analyst_steps` (such as
    # "fill") are not used.
    analyst = workers['analyst']
    assert isinstance(analyst, chrisjen.Contest)
    assert analyst.criteria is None
    options = [
        ['minmax_scale', 'robust_scale', 'normalize_scale'],
        ['stratified_kfold_split', 'train_test_split'],
        [
            'target_encode', 'weight_of_evidence_encode', 'one_hot_encode',
            'james_stein_encode'],
        ['none_sample', 'smote_sample'],
        ['xgboost_model', 'logit_model', 'random_forest_model'],
    ]
    expected = [list(path) for path in itertools.product(*options)]
    assert len(expected) == 144
    assert sorted(paths(analyst)) == sorted(expected)
    steps = {node.name: node for node in analyst}
    assert all(isinstance(step, chrisjen.Step) for step in steps.values())
    assert steps['minmax_scale'].contents.name == 'minmax'
    assert isinstance(steps['none_sample'].contents, chrisjen.NullVertex)
    # The critic's steps are used instead of its techniques. Its steps have no
    # techniques, so they are techniques themselves.
    assert isinstance(workers['critic'], chrisjen.Flow)
    assert paths(workers['critic']) == [['shap', 'sklearn']]
    # Parameters come from the "{name}_parameters" sections.
    assert steps['xgboost_model'].contents.parameters['max_depth'] == 5
    forest = steps['random_forest_model'].contents
    assert forest.parameters['n_estimators'] == [20, 1000]
    assert steps['logit_model'].contents.parameters == {}


""" Workshop """


def test_build_worker_follows_the_settings(tmp_path: pathlib.Path) -> None:
    project = create(tmp_path, automatic = False)
    model = workshop.build_worker('model', project)
    assert isinstance(model, chrisjen.Contest)
    assert model.criteria.contents == 'chrisjen_test_scores.total'
    assert sorted(paths(model)) == [['halve'], ['none']]
    prepare = workshop.build_worker('prepare', project)
    assert isinstance(prepare, chrisjen.Flow)
    scale = prepare.walk()[0][1]
    assert scale.parameters == {'factor': 3}


def test_build_uses_the_settings(tmp_path: pathlib.Path) -> None:
    project = create(tmp_path, automatic = False)
    scale = chrisjen.library.all['scale'].build('scale', project, {'factor': 2})
    assert scale.parameters == {'factor': 2}

    @dataclasses.dataclass
    class Shift(chrisjen.Technique):
        parameters: dict[str, Any] = dataclasses.field(
            default_factory = lambda: {'amount': 1, 'unit': 'm'})

    shift = Shift.build('shift', project, {'amount': 5})
    assert shift.parameters == {'amount': 5, 'unit': 'm'}
    assert Shift.build('shift', project).parameters == {
        'amount': 1, 'unit': 'm'}
    with pytest.raises(KeyError, match = "no class named 'nothing'"):
        workshop.build_node('nothing', project)


def test_settings_reach_the_fields_of_a_class(tmp_path: pathlib.Path) -> None:
    settings = {
        'grow_project': {
            'design': 'benchmark',
            'criterion': 'chrisjen_test_scores.never',
            'max_iterations': 3,
            'techniques': 'scale',
        },
        'scale_parameters': {'factor': 2},
    }
    project = chrisjen.Project.create(settings, item = [1], clerk = tmp_path)
    assert project.workflow.max_iterations == 3
    assert project.result == [8]
    assert project.workflow.iterations == 3
    settings['grow_project'] = {
        'grow_workers': 'inner',
        'inner_design': 'benchmark',
        'inner_criterion': 'chrisjen_test_scores.never',
        'inner_max_iterations': 2,
    }
    settings['inner'] = {'techniques': 'scale'}
    project = chrisjen.Project.create(settings, item = [1], clerk = tmp_path)
    assert project.result == [4]


def test_steps_wrap_their_techniques(tmp_path: pathlib.Path) -> None:
    @dataclasses.dataclass
    class Resize(chrisjen.Step):
        log: list[str] = dataclasses.field(default_factory = list)

        def begin(self, item: Any) -> Any:
            self.log.append(self.name)
            return item

    settings = {
        'demo_project': {
            'steps': 'clean, resize',
            'clean_techniques': 'drop_negatives',
            'resize_techniques': 'scale, halve',
        },
        'resize_parameters': {'factor': 10},
        'scale_resize_parameters': {'factor': 3},
    }
    project = chrisjen.Project.create(
        settings, item = [1, -2, 3], clerk = tmp_path)
    assert paths(project.workflow) == [
        ['drop_negatives_clean', 'scale_resize', 'halve_resize']]
    steps = {node.name: node for node in project.workflow}
    assert type(steps['drop_negatives_clean']) is chrisjen.Step
    assert isinstance(steps['scale_resize'], Resize)
    assert steps['scale_resize'].parameters == {'factor': 3}
    assert steps['halve_resize'].parameters == {'factor': 10}
    assert steps['scale_resize'].log == ['scale_resize']
    # The "{technique}_{step}" parameters win over the step's parameters.
    assert project.result == [1.5, 4.5]


def test_build_criteria_from_the_library(tmp_path: pathlib.Path) -> None:
    @dataclasses.dataclass
    class Positive(chrisjen.Criteria):
        def score(self, item: Any) -> Any:
            return item > 0

    project = create(tmp_path, automatic = False)
    assert isinstance(workshop.build_criteria('positive', project), Positive)
    path = workshop.build_criteria('statistics.fmean', project)
    assert type(path) is chrisjen.Criteria
    assert path.score([1, 3]) == 2.0


def test_build_criteria_with_parameters(tmp_path: pathlib.Path) -> None:
    project = chrisjen.Project.create(
        {
            'demo_project': {'techniques': 'none'},
            'builtins.round_parameters': {'ndigits': 1},
        },
        clerk = tmp_path,
        automatic = False)
    criteria = workshop.build_criteria('builtins.round', project)
    assert criteria.parameters == {'ndigits': 1}
    assert criteria.score(3.14159) == 3.1


def test_a_worker_class_named_after_a_worker(tmp_path: pathlib.Path) -> None:
    @dataclasses.dataclass
    class Prepare(chrisjen.Flow):
        label: str = 'none'

    project = chrisjen.Project.create(
        {
            'demo_project': {'demo_workers': 'prepare, finish'},
            'prepare': {'techniques': 'drop_negatives', 'label': 'target'},
            'finish': {'techniques': 'halve'},
        },
        item = [2, -2],
        clerk = tmp_path)
    workers = {node.name: node for node in project.workflow}
    # A class named after the worker is used instead of its design.
    assert type(workers['prepare']) is Prepare
    assert workers['prepare'].label == 'target'
    assert type(workers['finish']) is chrisjen.Flow
    assert project.result == [1.0]


def test_a_step_with_a_section_is_a_worker(tmp_path: pathlib.Path) -> None:
    project = chrisjen.Project.create(
        {
            'demo_project': {
                'steps': 'clean, finish',
                'finish_techniques': 'halve',
            },
            'clean': {'design': 'survey', 'techniques': 'drop_negatives, none'},
        },
        item = [2, -2],
        clerk = tmp_path,
        automatic = False)
    assert paths(project.workflow) == [['clean', 'halve_finish']]
    clean = next(iter(project.workflow))
    assert isinstance(clean, chrisjen.Survey)
    assert sorted(paths(clean)) == [['drop_negatives'], ['none']]
