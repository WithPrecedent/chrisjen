# Tutorial

This tutorial builds a small project in stages. It starts with a few lines of
Python and ends with a project that compares alternatives, reads its settings
from a file, and saves its results. Every example on this page is run by the
`chrisjen` unit tests, so you can copy and paste them.

## The vocabulary

| Part | What it is | In code |
| --- | --- | --- |
| Technique | An action, such as "drop_negatives". | `chrisjen.Technique` |
| Worker | A part of a project, such as "prepare" or "model". | `chrisjen.Worker` |
| Step | A stage of a worker, with techniques of its own. | A worker in a worker |

The **item** is the data (or any object) that the project works on. Each
technique takes the item and returns the changed item, and the result of one
becomes the input of the next.

## 1. Write techniques

A technique is a subclass of `chrisjen.Technique` with an `implement` method
that takes the item and returns the changed item. Its other keyword arguments
are its parameters:

```python
import dataclasses

import chrisjen


@dataclasses.dataclass
class DropNegatives(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return [x for x in item if x >= 0]


@dataclasses.dataclass
class Scale(chrisjen.Technique):
    def implement(self, item, factor = 2, **kwargs):
        return [x * factor for x in item]


@dataclasses.dataclass
class Total(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return sum(item)
```

Each class is added to `chrisjen.library` as soon as it is defined, under its
snake case name. That is the name you use in settings:

```python
print(chrisjen.library.all["drop_negatives"] is DropNegatives)
# True
print(Scale().apply([1, 2, 3]))
# [2, 4, 6]
```

## 2. Describe the project

Settings are a collection of sections. A project needs a section whose name ends
in `_project`. The part before `_project` is the name of the project, and its
`{name}_workers` setting lists the project's workers. Each worker has a section
of its own:

```python
settings = {
    "report_project": {"report_workers": "prepare, summarize"},
    "prepare": {
        "steps": "clean, resize",
        "clean_techniques": "drop_negatives",
        "resize_techniques": "scale",
    },
    "summarize": {"techniques": "total"},
}
```

The "prepare" worker has two steps, "clean" and "resize", and the
`{step}_techniques` settings say which techniques each step uses. The
"summarize" worker has no steps, so its `techniques` setting lists its
techniques directly. Lists can be written as text separated by commas or as
Python lists.

## 3. Create and run the project

```python
project = chrisjen.Project.create(settings, item = [3, -1, 4, -1, 5])
print(project.result)
# 24
```

`Project.create` reads the settings, builds the `workflow`, and applies it to
the item. The workflow is a worker for the whole project, whose nodes are the
workers. You can look at it:

```python
print([[node.name for node in path] for path in project.workflow.walk()])
# [['prepare', 'summarize']]
workers = {node.name: node for node in project.workflow}
print(type(workers["prepare"]).__name__)
# Flow
```

Each step of "prepare" is a `Step` node that wraps one of its techniques. A step
node is named "{technique}_{step}":

```python
print([[node.name for node in path] for path in workers["prepare"].walk()])
# [['drop_negatives_clean', 'scale_resize']]
```

## 4. Use a settings file

Settings can live in an ini, toml, json, yaml, xml, or Python file. Pass its
path instead of a `dict`. In an ini file, `bobbie` (the settings package that
`chrisjen` uses) turns text into numbers, `True` and `False`, and
comma-separated lists automatically.

<!-- file: report.ini -->
```ini
[report_project]
report_workers = prepare, summarize

[prepare]
steps = clean, resize
clean_techniques = drop_negatives
resize_techniques = scale

[summarize]
techniques = total
```

To build a project without running it, pass `automatic = False`. Then call
`apply` with an item, as many times as you like:

```python
project = chrisjen.Project.create("report.ini", automatic = False)
print(project.apply([3, -1, 4, -1, 5]))
# 24
print(project.apply([10, -5, 20]))
# 60
```

## 5. Set parameters

Parameters come from a section named `{name}_parameters`, where `name` is the
name of a technique, a step, or a worker. A step's parameters are passed to its
techniques, and a "{technique}_{step}_parameters" section is for one technique
in one step. Add a section to the settings to change the `factor` of `scale`:

```python
settings["scale_parameters"] = {"factor": 10}
project = chrisjen.Project.create(settings, item = [3, -1, 4, -1, 5])
print(project.result)
# 120
```

A step's parameters win over the parameters of its techniques, and a worker's
parameters (which are passed to everything in the worker) win over both.
Parameters passed to `apply` win over all of them:

```python
print(project.apply([3, -1, 4, -1, 5], factor = 1))
# 12
```

Only the parameters that an `implement` method (or a wrapped tool) accepts are
passed to it, so a parameter meant for one technique does not break the others.

## 6. Compare alternatives

A worker's `design` decides how its nodes are applied. The default, `flow`,
applies them one after another. A `contest` treats them as *alternatives*
instead: it applies each one to its own copy of the item and keeps the result
with the best score. A score comes from a **criterion**, a subclass of
`chrisjen.Criteria` with a `score` method (higher is better):

```python
@dataclasses.dataclass
class Halve(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return [x / 2 for x in item]


@dataclasses.dataclass
class SmallestSpread(chrisjen.Criteria):
    def score(self, item):
        return -(max(item) - min(item))


settings = {
    "compare_project": {"compare_workers": "shrinker"},
    "shrinker": {
        "design": "contest",
        "criterion": "smallest_spread",
        "techniques": "scale, halve, none",
    },
}
project = chrisjen.Project.create(settings, item = [1, 2, 3])
print(project.result)
# [0.5, 1.0, 1.5]
contest = {node.name: node for node in project.workflow}["shrinker"]
print(contest.winner)
# halve
print(contest.results)
# {'scale': [2, 4, 6], 'halve': [0.5, 1.0, 1.5], 'none': [1, 2, 3]}
```

`none` is a built-in technique that does nothing. It is useful for testing
whether a technique helps at all.

With steps, the techniques of each step are the alternatives. A contest tries
every combination of one technique from each step, and each combination is
labeled with the names of its step nodes joined with ">":

```python
settings["shrinker"] = {
    "design": "contest",
    "criterion": "smallest_spread",
    "steps": "clean, shrink",
    "clean_techniques": "drop_negatives, none",
    "shrink_techniques": "scale, halve",
}
project = chrisjen.Project.create(settings, item = [-8, 1, 2, 3])
contest = {node.name: node for node in project.workflow}["shrinker"]
print(len(contest.results))
# 4
print(contest.winner)
# drop_negatives_clean > halve_shrink
```

Each combination uses its own copies of the item and of the nodes, so a
technique that stores something (such as a fitted model) does not carry it from
one combination to the next.

A `survey` is like a contest, but returns the mean of the results instead of
choosing one. Its results must support addition and division by an integer, as
numbers do:

```python
@dataclasses.dataclass
class Largest(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return max(item)


settings = {
    "estimate_project": {
        "design": "survey",
        "techniques": "total, largest",
    },
}
print(chrisjen.Project.create(settings, item = [2, 4]).result)
# 5.0
```

## 7. Wrap tools from other packages

A technique can wrap a tool instead of having an `implement` method. Set
`contents` to the tool, or to its import path as a `str`. A path is only
imported when the technique is used, so techniques can wrap optional packages:

```python
@dataclasses.dataclass
class Mean(chrisjen.Technique):
    contents: str = "statistics.fmean"


@dataclasses.dataclass
class Root(chrisjen.Technique):
    contents: str = "math.sqrt"


@dataclasses.dataclass
class Rounded(chrisjen.Technique):
    contents: object = round


settings = {
    "wrap_project": {
        "techniques": "mean, root, rounded",
    },
    "rounded_parameters": {"ndigits": 1},
}
print(chrisjen.Project.create(settings, item = [2, 8]).result)
# 2.2
```

The mean of 2 and 8 is 5.0, its square root is about 2.236, and `round` keeps
one digit. The tool is called with the item as its first argument and the
parameters it accepts.

## 8. Save and load files

A project's `clerk` manages files. Pass the folder for the project's files as
`clerk`:

```python
import pathlib
import tempfile

root = pathlib.Path(tempfile.mkdtemp())
project = chrisjen.Project.create("report.ini", item = [1, 2, 3], clerk = root)
project.clerk.save(project.result, file_name = "result", file_format = "pickle")
print(project.clerk.load(file_name = "result", file_format = "pickle"))
# 12
```

The clerk is a `nagata.FileManager`. See the [nagata
documentation](https://WithPrecedent.github.io/nagata) for its file formats.
Settings in a "files" section of your settings that a `FileManager` accepts
(such as `output_folder`) are passed to it.

## 9. Draw the workflow

`to_dot` returns [Graphviz](https://graphviz.org/) text (and writes it to a file
if you pass `path`). `to_mermaid` returns [mermaid](https://mermaid.js.org/)
text, which many Markdown tools can draw. Both are made by `holden`:

```python
print(project.to_dot())
# digraph report {
# prepare -> summarize
# }
```

## Next steps

* The [advanced user guide](advanced.md) describes how settings are read, every
  design, criteria, building workflows in code, and adding your own designs.
* The [recipes](recipes.md) show complete examples.
