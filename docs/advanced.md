# Advanced User Guide

The [tutorial](tutorial.md) shows how to build a project. This guide describes
how `chrisjen` works and everything you can configure. Every example on this
page is run by the `chrisjen` unit tests.

## How the pieces fit together

```text
settings ──create──▶ Idea ──draft──▶ workflow ──apply──▶ result ──▶ report
(file or dict)     (bobbie        (holden graph of    (your item,
                    Settings)      Vertex objects)     changed)
```

1. **Settings** are loaded by [bobbie](https://github.com/WithPrecedent/bobbie)
   into an `Idea`, a `bobbie.Settings` (a `dict`-like collection of sections)
   with properties that read the parts of a workflow. This is `Project.idea`.
2. **Drafting** builds the workflow. The functions in `chrisjen.workshop` turn
   each name in the settings into a node, using the classes in
   `chrisjen.library`. This is `Project.workflow`.
3. **Applying** runs the workflow on an item. The result is stored in
   `Project.result`, and `Project.report` describes the run.

Files are managed by a [nagata](https://github.com/WithPrecedent/nagata)
`FileManager` (`Project.clerk`).

| Class | Description |
| --- | --- |
| `Project` | Interface for a project. Holds the settings, workflow, result, and report. |
| `Idea` | The settings of a project, with properties for its workers, steps, techniques, designs, criteria, and parameters. |
| `Library` | Stores every `Genre` class in the hierarchy of its subclasses. `chrisjen.library` is the one that projects use. |
| `Genre` | Base class for every class that is stored in the library. |
| `Vertex` | Base class for anything in a workflow. It is hashed and compared by `name` and applied to an item with `apply`. |
| `Technique` | A single action. It has an `implement` method or wraps a tool (a callable or the import path of one). |
| `NullVertex` | A technique that does nothing. It is called "none". |
| `Step` | Wraps one technique or worker, with `begin` and `end` hooks. |
| `Worker` | A node that is a graph of other nodes. Its subclasses are the designs: `Flow`, `Benchmark`, `Contest`, and `Survey`. |
| `Criteria` | Scores results, for the designs that need a score or a test. |
| `Report` | Describes a project after it is applied. `Summary` is the default. |

## The library

Every subclass of `Genre` is added to `chrisjen.library` when it is defined,
under its snake case name (`DropNegatives` is "drop_negatives"). A subclass
that also lists `abc.ABC` among its bases is a *genre*: it is a key in the
library whose value holds its subclasses, and the class itself is not stored.

```python
import abc
import dataclasses

import chrisjen

print(sorted(chrisjen.library["vertex"]))
# ['none', 'null_vertex', 'step', 'technique', 'worker']
print(chrisjen.library["vertex"]["worker"])
# {'flow': <class 'chrisjen.workers.Flow'>, 'benchmark': <class 'chrisjen.workers.Benchmark'>, 'contest': <class 'chrisjen.workers.Contest'>, 'survey': <class 'chrisjen.workers.Survey'>}
```

A package built on `chrisjen` can add genres of its own. Each is a new layer of
the library:

```python
class Cleaner(chrisjen.Technique, abc.ABC):
    """Techniques that clean data."""


@dataclasses.dataclass
class DropBlanks(Cleaner):
    def implement(self, item, **kwargs):
        return [x for x in item if x]


print(chrisjen.library["vertex"]["cleaner"])
# {'drop_blanks': <class 'docs_advanced.DropBlanks'>}
print(chrisjen.library.classify("drop_blanks"))
# cleaner
print("cleaner" in chrisjen.library.genres)
# True
```

`library.all` is a flat `dict` of every stored class, which is how names in
settings are found. Names should be unique across the library: if two classes
have the same name, the first one found is used.

## Settings reference

A project's settings need a section named `{name}_project` (or a `name` passed
to `Project.create`). Every other section is a worker, except sections that
end in `parameters` and the special sections "general" and "files". In each
worker section (and the project section, which is the worker for the whole
project), these settings can be written alone or after a name:

| Setting | Meaning |
| --- | --- |
| `steps` or `{name}_steps` | Names of the steps of the worker or of `name`. |
| `workers` or `{name}_workers` | The same as `steps`. The project section usually uses `{name}_workers`. |
| `techniques` or `{name}_techniques` | Names of the techniques of the worker or of `name`. These are used if there are no steps. |
| `design` or `{name}_design` | Design of the worker or of `name`. Defaults to `flow`. |
| `criterion` or `{name}_criterion` | Criteria of the worker or of `name`: the name of a `Criteria` subclass or the import path of a scoring function. |
| Any field of a class, or `{name}_{field}` | Passed to the class that `name` is built with, such as `max_iterations` for a `benchmark`. |

A setting written alone belongs to the worker of its section, and a setting
written after a name belongs to that name. Other sections:

| Section | Meaning |
| --- | --- |
| `{name}_parameters` | Keyword parameters for the worker, step, or technique called `name`. |
| `{technique}_{step}_parameters` | Keyword parameters for one technique in one step. |
| `files` | Arguments for the project's `nagata.FileManager`, such as `output_folder`. |
| `general` | Ignored by `chrisjen`, for your own use. |

## How a workflow is built

The functions in `chrisjen.workshop` turn the names in the settings into
nodes, starting from the project's worker:

* **Workers.** A name with a section of its own (or a list of steps) is a
  worker. Its class is the worker class with its name, if there is one (so a
  package can define an `Analyst` worker for "analyst"), and otherwise the
  class of its design.
* **Steps.** Each technique of a step is wrapped in a `Step` node named
  "{technique}_{step}". Its class is the `Step` subclass with the step's name,
  if there is one (such as a `Scale` step for "scale"), and otherwise `Step`.
  A step without techniques is a node itself.
* **Techniques.** Any other name is built with the class in the library that
  has its name, usually a `Technique` subclass.

Each class builds itself with its `build` class method, which passes the
settings that match its fields to its constructor and adds its parameters. A
worker's `populate` method then connects its nodes: one after another for a
`flow` or `benchmark`, or, for a `contest` or `survey`, so that every
combination of one technique from each step is a path through the graph. The
nodes in a worker must have unique names. `Library.borrow` finds classes by
name, with fallbacks:

```python
print(chrisjen.library.borrow(["analyst", "contest"], genre = "worker"))
# <class 'chrisjen.workers.Contest'>
```

`Project.idea` reads these settings with its properties:

```python
settings = {
    "demo_project": {"demo_workers": "prepare, model"},
    "prepare": {
        "steps": "clean, scale",
        "clean_techniques": "drop_blanks, none",
    },
    "model": {"design": "contest", "criterion": "statistics.fmean"},
    "scale_parameters": {"factor": 3},
}
idea = chrisjen.Idea.create(settings)
print(idea.workers.keys())
# dict_keys(['demo', 'prepare', 'model'])
print(idea.steps)
# {'demo': ['prepare', 'model'], 'prepare': ['clean', 'scale']}
print(idea.techniques)
# {'clean': ['drop_blanks', 'none']}
print(idea.designs)
# {'model': 'contest', 'demo': 'flow', 'prepare': 'flow'}
print(idea.criteria, idea.parameters)
# {'model': 'statistics.fmean'} {'scale': {'factor': 3}}
```

## Designs

Each design is a subclass of `Worker`, which is a
[holden](https://WithPrecedent.github.io/holden) `System`: a directed graph
whose nodes are the vertexes themselves. A design decides how its nodes are
applied. The examples below use these techniques:

```python
@dataclasses.dataclass
class AddOne(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return item + 1


@dataclasses.dataclass
class Triple(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return item * 3


@dataclasses.dataclass
class Largest(chrisjen.Criteria):
    def score(self, item):
        return item
```

### flow

The default. The nodes are connected in a sequence and applied one after
another.

```python
settings = {"chain_project": {"techniques": "add_one, triple"}}
print(chrisjen.Project.create(settings, item = 1).result)
# 6
```

### benchmark

Repeats the sequence until its criteria's `test` passes (that is, until the
score is true), or until `max_iterations` passes have been made (if it is set).
`iterations` is the number of passes made.

```python
@dataclasses.dataclass
class BigEnough(chrisjen.Criteria):
    def score(self, item):
        return item >= 100


settings = {
    "growth_project": {
        "design": "benchmark",
        "criterion": "big_enough",
        "techniques": "triple",
    },
}
project = chrisjen.Project.create(settings, item = 2)
print(project.result, project.workflow.iterations)
# 162 4
```

Set `max_iterations` in the settings to limit the number of passes:

```python
settings["growth_project"]["max_iterations"] = 2
project = chrisjen.Project.create(settings, item = 2)
print(project.result, project.workflow.iterations)
# 18 2
```

### contest

Tries every path through its graph and keeps the result with the highest
score. A worker without steps has one path for each of its techniques. With
steps, there is a path for every combination of one technique from each step.
Each path works on its own deep copy of the item, with its own copies of the
nodes. `results` has the result of each path, labeled with the names of its
nodes joined with " > ", and `winner` is the label of the best one. Ties go to
the first.

```python
settings = {
    "strategy_project": {
        "design": "contest",
        "criterion": "largest",
        "techniques": "add_one, triple",
    },
}
project = chrisjen.Project.create(settings, item = 10)
print(project.result, project.workflow.winner, project.workflow.results)
# 30 triple {'add_one': 11, 'triple': 30}

combinations = {
    "strategy_project": {
        "design": "contest",
        "criterion": "largest",
        "steps": "first, second",
        "first_techniques": "add_one, triple",
        "second_techniques": "add_one, triple",
    },
}
project = chrisjen.Project.create(combinations, item = 10)
print(len(project.workflow.results), project.workflow.winner)
# 4 triple_first > triple_second
```

To keep the lowest score instead, return a negative score.

### survey

Like `contest`, but returns the mean of the results (also stored in
`average`). The results must support addition and division by an integer
(numbers, `numpy` arrays, and `pandas` objects do).

```python
settings["strategy_project"]["design"] = "survey"
print(chrisjen.Project.create(settings, item = 10).result)
# 20.5
```

## Criteria

`Criteria` scores results. Subclass it and write a `score` method, or wrap a
scoring function (or its import path) in `contents`. `score` returns the score
(higher is better) and `test` returns whether the score is true.

```python
mean = chrisjen.Criteria(contents = "statistics.fmean")
print(mean.score([1, 2, 6]), mean.test([0, 0]))
# 3.0 False
```

In settings, `criterion` names a `Criteria` subclass in the library. Any other
name is used as the import path of a scoring function, which is wrapped in a
`Criteria`. Parameters for it come from a `{criterion}_parameters` section.

## Parameters and precedence

Keyword parameters come from `{name}_parameters` sections and from `apply`. A
node passes its parameters to everything inside it, so when the same parameter
is set in more than one place, the outer one wins:

1. The technique's parameters (lowest).
2. The parameters of the step that wraps it (`{step}_parameters`, updated with
   `{technique}_{step}_parameters`).
3. The parameters of the workers that contain it, from the innermost to the
   outermost.
4. Keyword arguments passed to `Project.apply` (highest).

```python
@dataclasses.dataclass
class AddAmount(chrisjen.Technique):
    def implement(self, item, amount = 0, **kwargs):
        return item + amount


settings = {
    "sum_project": {"sum_workers": "adder"},
    "adder": {"techniques": "add_amount"},
    "add_amount_parameters": {"amount": 1},
}
project = chrisjen.Project.create(settings, item = 0)
print(project.result)
# 1
settings["adder_parameters"] = {"amount": 2}
project = chrisjen.Project.create(settings, item = 0)
print(project.result, project.apply(0, amount = 5))
# 2 5
```

An `implement` method gets only the parameters it accepts (unless it takes
`**kwargs`). A wrapped tool gets only the parameters that it accepts.

## Techniques and steps

A `Technique` has three attributes:

| Attribute | Meaning |
| --- | --- |
| `name` | How the technique is referred to in a workflow. |
| `contents` | The tool: any callable, or its import path as a `str` (such as `"statistics.fmean"` or `"package.module:Class.method"`). |
| `parameters` | Keyword parameters for the tool. |

The default `implement` calls the tool with the item as the first argument. An
import path is only imported when the technique is used, so a technique can
wrap a package that might not be installed. A subclass can override
`implement` to call its tool differently.

```python
mean = chrisjen.Technique(name = "mean", contents = "statistics.fmean")
print(mean.apply([1, 2, 3, 6]))
# 3.0
rounded = chrisjen.Technique(
    name = "rounded", contents = round, parameters = {"ndigits": 1})
print(rounded.apply(3.14159))
# 3.1
```

A `Step` wraps one technique or worker and adds `begin` and `end` hooks, which
run before and after it:

```python
@dataclasses.dataclass
class Logged(chrisjen.Step):
    log: list = dataclasses.field(default_factory = list)

    def begin(self, item):
        self.log.append(f"before: {item}")
        return item

    def end(self, item):
        self.log.append(f"after: {item}")
        return item


step = Logged(name = "logged", contents = Triple(name = "triple"))
print(step.apply(2), step.log)
# 6 ['before: 2', 'after: 6']
```

A `Step` subclass named after a step in the settings is used for that step, so
a package can give a step code that all of its techniques share. A step also
returns the attributes of its technique that it does not have itself:

```python
@dataclasses.dataclass
class Grow(chrisjen.Step):
    def end(self, item):
        return item + 100


settings = {"growth_project": {"steps": "grow", "grow_techniques": "triple"}}
project = chrisjen.Project.create(settings, item = 1)
step = next(iter(project.workflow))
print(type(step).__name__, step.name, project.result)
# Grow triple_grow 103
```

## Building workflows in code

You do not have to use settings. Create a design and add nodes with
`populate`, which connects them in sequence. An item can also be a list of
alternatives: a `Flow` applies them one after another, and a `Contest` or
`Survey` tries every combination of one node from each list. Workers can be
nodes of other workers:

```python
inner = chrisjen.Flow(name = "inner")
inner.populate([AddOne(name = "add_one"), Triple(name = "triple")])
outer = chrisjen.Flow(name = "outer")
outer.populate([inner, AddOne(name = "add_one")])
print(outer.apply(1))
# 7

bench = chrisjen.Benchmark(
    name = "bench", criteria = BigEnough(), max_iterations = 2)
bench.populate([Triple(name = "triple")])
print(bench.apply(2), bench.iterations)
# 18 2

contest = chrisjen.Contest(name = "contest", criteria = Largest())
contest.populate([[AddOne(name = "add_one"), Triple(name = "triple")]])
print(contest.apply(10), contest.winner)
# 30 triple
```

## Custom designs

To add a design, subclass `Worker` (or one of the designs) and write an
`implement` method. `self.walk()` returns the paths through the graph, as lists
of nodes, and each node's `apply(item, **kwargs)` applies it. The class is
available in settings by its snake case name:

```python
@dataclasses.dataclass
class TwiceOver(chrisjen.Flow):
    """Applies the whole sequence two times."""

    def implement(self, item, **kwargs):
        for _ in range(2):
            item = super().implement(item, **kwargs)
        return item


settings = {
    "twice_project": {"twice_workers": "worker"},
    "worker": {"design": "twice_over", "techniques": "triple"},
}
print(chrisjen.Project.create(settings, item = 1).result)
# 9
```

To compare alternatives, mix `chrisjen.Comparator` into a design (before
`Worker`). Its `populate` method connects the alternatives so that every
combination is a path, `try_paths` applies every path to copies of the item and
the nodes, and `compare` scores the results with `criteria`.

## Custom reports

A report is a subclass of `Report` with a `generate` method, which is called
with the project after each `apply`. Pass an instance as `report`:

```python
@dataclasses.dataclass
class History(chrisjen.Report):
    contents: list = dataclasses.field(default_factory = list)

    def generate(self, project):
        self.contents.append(project.result)
        return self.contents


project = chrisjen.Project.create(
    {"chain_project": {"techniques": "triple"}},
    report = History(),
    automatic = False)
project.apply(1)
project.apply(2)
print(project.report.contents)
# [3, 6]
```

## Using the graph

A worker is a `holden.System`, so everything `holden` offers is available. Its
nodes are the vertexes themselves, and because vertexes are hashed and compared
by name, a node's name can be used in its place:

```python
print(inner.contents)
# {AddOne(contents=None, name='add_one', parameters={}): {Triple(contents=None, name='triple', parameters={})}, Triple(contents=None, name='triple', parameters={}): set()}
print([node.name for node in inner.root], "triple" in inner)
# ['add_one'] True
print(inner.to_dot(), end = "")
# digraph inner {
# add_one -> triple
# }
```

## Using the settings and the clerk

`Project.idea` is a `bobbie.Settings`. It is a `dict`, so you can read any
section, and its methods (such as `inject`, which adds settings to an object as
attributes) are available. You can pass an `Idea` to `Project.create` and it is
used as is.

`Project.clerk` is a `nagata.FileManager`. Its `save` and `load` methods take a
`file_name`, an optional `folder`, and an optional `file_format` (or use a file
name with an extension, such as "results.csv" if `pandas` is installed).
Without a `clerk` argument, `Project.create` uses `options._DEFAULT_ROOT` as the
folder.

## Errors you may see

| Error | Cause |
| --- | --- |
| `ValueError: A Project name was not given and could not be found in idea` | The settings have no worker sections and no `name` was passed. |
| `KeyError: no class named ... is in the library` | A technique or design name is not the snake case name of a class in the library. Check that the module that defines it has been imported. |
| `ValueError: ... is already in the composite data structure` | The same name is listed twice in one worker. |
| `ValueError: benchmark ... needs criteria` | A `benchmark` has no `criterion` setting. |
| `ValueError: ... needs criteria to compare results` | A `contest` has no `criterion` setting. |
| `ValueError: ... has no paths to compare` | A `contest` or `survey` has no techniques or steps. |
| `ImportError: cannot import ...` | The import path of a tool or criterion is wrong, or its package is not installed. This is raised when it is used. |
| `TypeError: technique ... wraps ..., which is not callable` | The tool is not callable. Wrap a callable, or override `implement`. |
| `NotImplementedError: technique ... has no tool` | A `Technique` has no `contents` and does not override `implement`. |
| `ValueError: step ... has no technique or workflow in contents` | A `Step` was applied without `contents`. |

Names in ini files that look like booleans or numbers (`yes`, `no`, `true`,
`false`, `1`) are converted by the ini loader before `chrisjen` sees them, so
avoid them as names of workers, steps, or techniques.
