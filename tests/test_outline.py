"""Tests Outline."""

from __future__ import annotations

import pathlib

import bobbie
import pytest

import chrisjen

SETTINGS = pathlib.Path(__file__).parent / "cancer_settings.ini"


def test_outline_from_ini() -> None:
    idea = bobbie.Settings.create(SETTINGS)
    outline = chrisjen.Outline.create(idea)
    assert outline.name == "wisconsin_cancer"
    assert outline.design == "waterfall"
    assert outline.workers == ["wrangler", "analyst", "critic"]
    assert outline.designs == {
        "wrangler": "waterfall",
        "analyst": "compete",
        "critic": "waterfall",
    }
    assert outline.steps["analyst"] == [
        "scale",
        "split",
        "encode",
        "sample",
        "model",
    ]
    assert outline.steps["critic"] == ["shap", "sklearn"]
    assert "wrangler" not in outline.steps
    assert outline.techniques["wrangler"] == {"wrangler": ["none"]}
    assert outline.techniques["analyst"]["scale"] == [
        "minmax",
        "robust",
        "normalize",
    ]
    assert outline.techniques["analyst"]["sample"] == ["none", "smote"]
    # A step with no list of techniques uses a technique of the same name.
    assert outline.techniques["critic"]["shap"] == ["shap"]
    assert outline.kinds["analyst"] == "worker"
    assert outline.kinds["scale"] == "step"
    assert outline.kinds["minmax"] == "technique"


def test_outline_initialization_settings() -> None:
    outline = chrisjen.Outline.create(bobbie.Settings.create(SETTINGS))
    assert outline.initialization["analyst"] == {
        "model_type": "classify",
        "label": "target",
        "default_package": "sklearn",
        "search_method": "random",
    }
    assert outline.initialization["critic"] == {
        "data_to_review": "test",
        "join_predictions": True,
    }


def test_percent_in_values_is_not_interpolated() -> None:
    idea = bobbie.Settings.create(SETTINGS)
    assert idea["files"]["float_format"] == "%.4f"


def test_outline_from_dict_with_options_and_parameters() -> None:
    outline = chrisjen.Outline.create(
        {
            "demo_project": {
                "demo_workers": "worker",
                "design": "pert",
                "criteria": "score",
                "extra": 1,
            },
            "worker": {
                "worker_steps": ["one", "two", "three"],
                "design": "lean",
                "max_iterations": 4,
                "tolerance": 0.5,
                "three_requires": ["one", "two"],
                "other": "value",
            },
            "one_parameters": {"duration": 3, "speed": "fast"},
            "worker_parameters": {"shared": True},
        }
    )
    assert outline.name == "demo"
    assert outline.design == "pert"
    assert outline.options["demo"] == {"criteria": "score"}
    assert outline.options["worker"] == {"max_iterations": 4, "tolerance": 0.5}
    assert outline.initialization["demo"] == {"extra": 1}
    assert outline.initialization["worker"] == {"other": "value"}
    assert outline.requirements == {"worker": {"three": ["one", "two"]}}
    assert outline.durations == {"one": 3.0}
    assert outline.parameters == {
        "one": {"speed": "fast"},
        "worker": {"shared": True},
    }


def test_design_setting_named_for_worker() -> None:
    outline = chrisjen.Outline.create(
        {
            "x_project": {"x_workers": ["w"], "x_design": "kanban"},
            "w": {"w_design": "survey", "w_techniques": ["a", "b"]},
        }
    )
    assert outline.design == "kanban"
    assert outline.designs["w"] == "survey"
    assert outline.techniques["w"] == {"w": ["a", "b"]}


def test_outline_summary() -> None:
    outline = chrisjen.Outline.create(bobbie.Settings.create(SETTINGS))
    lines = outline.summary.splitlines()
    assert lines[0] == "wisconsin_cancer (waterfall)"
    assert "  analyst (compete)" in lines
    assert "    scale: minmax, robust, normalize" in lines


def test_named_project() -> None:
    settings = {
        "first_project": {"first_workers": "a"},
        "second_project": {"second_workers": "b"},
        "a": {"a_techniques": "none"},
        "b": {"b_techniques": "none"},
    }
    assert chrisjen.Outline.create(settings).name == "first"
    assert chrisjen.Outline.create(settings, name="second").name == "second"
    assert chrisjen.Outline.create(settings, name="second_project").workers == [
        "b"
    ]


def test_no_project_section() -> None:
    with pytest.raises(ValueError, match="_project"):
        chrisjen.Outline.create({"general": {"seed": 1}})
    with pytest.raises(ValueError, match='"nope_project"'):
        chrisjen.Outline.create({"a_project": {"a_workers": "w"}}, name="nope")


def test_no_workers() -> None:
    with pytest.raises(ValueError, match="a_workers"):
        chrisjen.Outline.create({"a_project": {"other": 1}})


def test_missing_worker_section() -> None:
    with pytest.raises(ValueError, match="worker 'w'"):
        chrisjen.Outline.create({"a_project": {"a_workers": "w"}})
