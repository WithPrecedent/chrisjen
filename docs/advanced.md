# Advanced User Guide

## Core Classes

The core classes of a typical `chrisjen` project are:

| Class | Description |
| --- | --- |
| Project | Interface for a project |
| Architect | Settings from a file or `dict`-like object |
| Workflow | Iterable graph of nodes in a project |
| Node | A step in a project workflow, which may include its own workflow |

To make `chrisjen` extensible and flexible, these additional classes are included:

| Class | Description |
| --- | --- |
| Resources | A `dict`-like class containing available options |
| Engineer | Accesses and stores resources |
| Resource | Base class for all items stored in a `Resources` class |
| Defaults | Contains default resource options when not specified by the user |
| Manager | Assembles and controls a project workflow |
| View | An abstraction layer for viewing data stored in another class |

Out of the box, there are different types of workflows:

| Class | Description |
| --- | --- |
| Waterfall | Typical linear workflow |
| Research | Integrates criteria for branching or selection |
| Compare | A `Research` subclass that includes branches to compare |
| Observe | A `Research` subclass that branches but, unlike `Compare`, does not select or reduce |
| Compete | A `Compare` subclass that selects one branch to continue based on criteria |
| Lean | A `Compare` subclass that maximizes efficiency based on criteria |
| Survey | A `Compare` subclass that averages results across the branches |

These are the included `Node` subclasses:

| Class | Description |
| --- | --- |
| Worker | Iterable node with its own workflow |
| Task | Non-iterable node |
| NullNode | An empty node included for convenience when comparison to inaction is important |
