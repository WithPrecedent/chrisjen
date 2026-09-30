"""Exports for workflows.

Contents:
    to_dot: creates a Graphviz dot description of a workflow.

"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from . import nodes

if TYPE_CHECKING:
    from . import workflows


def to_dot(
    workflow: workflows.Workflow,
    path: pathlib.Path | str | None = None,
    name: str | None = None,
) -> str:
    """Creates a Graphviz dot description of a workflow.

    A `Worker` node is drawn as a cluster that contains the nodes of its own
    workflow. Edges between workers connect the endpoints of one to the roots
    of the next.

    Args:
        workflow: workflow to describe.
        path: file to save the text to. Defaults to `None`.
        name: name of the graph. Defaults to the name of `workflow`.

    Returns:
        The dot text.

    """
    name = name or workflow.name or "workflow"
    lines = [f"digraph {_quote(name)} {{"]
    ports: dict[str, tuple[list[str], list[str]]] = {}
    for node_name in workflow.order():
        node = workflow.retrieve(node_name)
        if isinstance(node, nodes.Worker) and node.contents is not None:
            ports[node_name] = _cluster(node, lines)
        else:
            identifier = _quote(node_name)
            lines.append(f"  {identifier};")
            ports[node_name] = ([node_name], [node_name])
    for start, stops in workflow.contents.items():
        for stop in sorted(stops):
            for tail in ports[start][1]:
                for head in ports[stop][0]:
                    lines.append(f"  {_quote(tail)} -> {_quote(head)};")
    lines.append("}")
    text = "\n".join(lines) + "\n"
    if path is not None:
        pathlib.Path(path).write_text(text, encoding = "utf-8")
    return text


def _cluster(
    worker: nodes.Worker, lines: list[str]
) -> tuple[list[str], list[str]]:
    """Writes a cluster for `worker` and returns its roots and endpoints."""
    inner = worker.contents
    design = type(inner).__name__.lower()
    lines.append(f"  subgraph {_quote('cluster_' + worker.name)} {{")
    lines.append(f"    label = {_quote(f'{worker.name} ({design})')};")
    for step_name in inner.order():
        step = inner.retrieve(step_name)
        techniques = ", ".join(t.name for t in step.alternatives)
        label = f"{step_name}\\n{techniques}" if techniques else step_name
        lines.append(
            f"    {_quote(worker.name + '..' + step_name)} "
            f"[label = {_quote(label, escape=False)}];"
        )
    for start, stops in inner.contents.items():
        for stop in sorted(stops):
            lines.append(
                f"    {_quote(worker.name + '..' + start)} -> "
                f"{_quote(worker.name + '..' + stop)};"
            )
    lines.append("  }")
    return (
        [f"{worker.name}..{r}" for r in inner.root],
        [f"{worker.name}..{e}" for e in inner.endpoint],
    )


def _quote(text: str, *, escape: bool = True) -> str:
    """Returns `text` as a quoted dot string."""
    if escape:
        text = text.replace("\\", "\\\\")
    return '"' + text.replace('"', '\\"') + '"'
