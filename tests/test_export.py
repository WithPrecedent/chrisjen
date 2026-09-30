"""Tests exports of workflows."""

from __future__ import annotations

import pathlib
from typing import Any

import chrisjen


def step(name: str, *techniques: str) -> chrisjen.Step:
    return chrisjen.Step(
        name = name,
        contents = [
            chrisjen.Technique.create(t) for t in techniques or ("none",)
        ],
    )


def worker(
    name: str, design: str, steps: list[chrisjen.Step], **options: Any
) -> chrisjen.Worker:
    requirements = options.pop("requirements", None)
    return chrisjen.Worker(
        name = name,
        contents = chrisjen.Workflow.design(
            design, steps, requirements = requirements, name = name, **options
        ),
    )


def test_plain_workflow() -> None:
    workflow = chrisjen.Workflow.design(
        "waterfall", [step("a"), step("b")], name = "flow"
    )
    assert chrisjen.to_dot(workflow) == (
        'digraph "flow" {\n  "a";\n  "b";\n  "a" -> "b";\n}\n'
    )


def test_name_argument_and_default_name() -> None:
    workflow = chrisjen.Workflow.design("waterfall", [step("a")])
    assert chrisjen.to_dot(workflow).startswith('digraph "workflow" {')
    assert chrisjen.to_dot(workflow, name = "other").startswith(
        'digraph "other" {'
    )
    named = chrisjen.Workflow.design("waterfall", [step("a")], name = "mine")
    assert chrisjen.to_dot(named).startswith('digraph "mine" {')


def test_empty_workflow() -> None:
    workflow = chrisjen.Workflow.design("waterfall", [])
    assert chrisjen.to_dot(workflow) == 'digraph "workflow" {\n}\n'


def test_saves_file(tmp_path: pathlib.Path) -> None:
    workflow = chrisjen.Workflow.design("waterfall", [step("a"), step("b")])
    for path in (tmp_path / "one.dot", str(tmp_path / "two.dot")):
        text = chrisjen.to_dot(workflow, path = path)
        assert pathlib.Path(path).read_text(encoding = "utf-8") == text
    nothing = chrisjen.to_dot(workflow)
    assert not (tmp_path / "three.dot").exists()
    assert nothing == text


def test_workers_are_clusters() -> None:
    workflow = chrisjen.Workflow.design(
        "waterfall",
        [
            worker("first", "waterfall", [step("a", "none"), step("b")]),
            worker("second", "contest", [step("c", "none", "null")]),
        ],
        name = "project",
    )
    text = chrisjen.to_dot(workflow)
    assert 'subgraph "cluster_first" {' in text
    assert 'label = "first (waterfall)";' in text
    assert 'label = "second (contest)";' in text
    assert '"first..a" [label = "a\\nnone"];' in text
    assert '"second..c" [label = "c\\nnone, null"];' in text
    assert '"first..a" -> "first..b";' in text
    # The last step of the first worker connects to the first step of the next.
    assert '"first..b" -> "second..c";' in text
    assert text.count("subgraph") == 2
    assert text.endswith("}\n")


def test_clusters_with_several_roots_and_endpoints() -> None:
    parallel = worker(
        "parallel",
        "pert",
        [step("r1"), step("r2"), step("e1"), step("e2")],
        requirements = {"e1": ["r1", "r2"], "e2": ["r1", "r2"]},
    )
    after = worker(
        "after", "pert", [step("s1"), step("s2")], requirements = {"s2": ["s1"]}
    )
    text = chrisjen.to_dot(
        chrisjen.Workflow.design("waterfall", [parallel, after])
    )
    assert '"parallel..r1" -> "parallel..e1";' in text
    assert '"parallel..r2" -> "parallel..e2";' in text
    # Every endpoint connects to every root of the next worker.
    assert '"parallel..e1" -> "after..s1";' in text
    assert '"parallel..e2" -> "after..s1";' in text


def test_names_are_escaped() -> None:
    workflow = chrisjen.Workflow.design(
        "waterfall", [step('say "hi"'), step("back\\slash")]
    )
    text = chrisjen.to_dot(workflow, name = 'a "graph"')
    assert text.startswith('digraph "a \\"graph\\"" {')
    assert '"say \\"hi\\"";' in text
    assert '"back\\\\slash";' in text


def test_worker_without_a_workflow_is_a_plain_node() -> None:
    workflow = chrisjen.Workflow.design(
        "waterfall", [chrisjen.Worker(name = "empty"), step("after")]
    )
    text = chrisjen.to_dot(workflow)
    assert '"empty";' in text
    assert '"empty" -> "after";' in text
    assert "subgraph" not in text


def test_worker_with_an_empty_workflow_is_drawn_without_edges() -> None:
    hollow = worker("hollow", "waterfall", [])
    workflow = chrisjen.Workflow.design("waterfall", [hollow, step("after")])
    text = chrisjen.to_dot(workflow)
    assert 'subgraph "cluster_hollow"' in text
    assert "->" not in text


def test_project_export_matches_function() -> None:
    settings = {
        "demo_project": {"demo_workers": ["one", "two"]},
        "one": {"one_techniques": "none"},
        "two": {"two_techniques": "none"},
    }
    project = chrisjen.Project(settings)
    text = project.to_dot()
    assert text == chrisjen.to_dot(project.workflow)
    assert text.startswith('digraph "demo" {')
    assert '"one..one" -> "two..two";' in text
