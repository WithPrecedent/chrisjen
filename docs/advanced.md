# Advanced User Guide

The [tutorial](tutorial.md) shows how to build a project. This guide describes how `chrisjen` works and everything you can configure. Every example on this page is run by the `chrisjen` unit tests.

## How the pieces fit together

```text
settings ──draft──▶ Outline ──publish──▶ Workflow ──apply──▶ result
(bobbie)           (the plan)            (holden graph        (your item,
                                          of Node objects)     changed)
```

1. **Settings** are loaded by [bobbie](https://github.com/WithPrecedent/bobbie) into a `bobbie.Settings` (a `dict`-like collection of sections). This is `Project.idea`.
2. **Drafting** turns the settings into an `Outline`, a plain record of the workers, steps, techniques, designs, and parameters. This is `Project.outline`. Nothing has been created yet, and any mistakes in the settings that can be found without running code are reported here.
3. **Publishing** creates the objects: `Technique`, `Step`, and `Worker` nodes, and a `Workflow` for each worker and for the project. Names are turned into classes and functions by [wonka](https://github.com/WithPrecedent/wonka) factories. This is `Project.workflow`.
4. **Applying** runs the workflow on an item. The result is stored in `Project.result`.

Files are managed by a [nagata](https://github.com/WithPrecedent/nagata) `FileManager` (`Project.clerk`).

| Class | Description |
| --- | --- |
| `Project` | Interface for a project. Holds the settings, outline, workflow, and result. |
| `Outline` | The plan for a project, derived from its settings. |
| `Workflow` | A directed graph of nodes and the rules for applying them. Its subclasses are the designs. |
| `Node` | Base class for anything in a workflow. It is hashed and compared by `name`. |
| `Worker` | A node with a workflow of its own (of steps). |
| `Step` | A node with techniques. |
| `Technique` | A single action. It is a function or a subclass with an `implement` method. |
| `NullNode` | A technique that does nothing. It is called "none". |

## Settings reference

A project's settings need a section named `{name}_project`. The names of workers, steps, and techniques are used to build the names of settings:

| Setting | Section | Meaning |
| --- | --- | --- |
| `{name}_workers` | `{name}_project` | Names of the workers. Required. |
| `design` or `{name}_design` | `{name}_project` | Design that combines the workers. Defaults to `waterfall`. |
| `design` or `{worker}_design` | `{worker}` | Design that combines the worker's steps. Defaults to `waterfall`. |
| `{worker}_steps` | `{worker}` | Names of the worker's steps. |
| `{step}_techniques` | `{worker}` | Names of the techniques of a step. If there is none, the step is its own technique (a technique with the step's name is used). |
| `{worker}_techniques` | `{worker}` | Techniques of a worker that has no steps. |
| `{step}_requires` | `{worker}` | Names of steps that must come before a step. See `pert`. |
| `{worker}_requires` | `{name}_project` | Names of workers that must come before a worker. See `pert`. |
| `criteria` | project or worker | Name of a criterion (see `@chrisjen.criterion`). Used by `agile`, `lean`, and `contest`. |
| `max_iterations` | project or worker | The most passes for `agile` and `lean`. Defaults to 10. |
| `tolerance` | project or worker | The smallest improvement that `lean` counts. Defaults to 0. |
| `select` | project or worker | `max` (default) or `min`. Whether `contest` keeps the highest or lowest score. |
| `{name}_parameters` | its own section | Keyword parameters for the worker, step, or technique called `name`. A `duration` parameter is used by `pert`. |
| `files` | its own section | Settings for the project's file manager. |

Lists are separated by commas (with or without a space after each one). Design names are not case sensitive. Workers, and steps within a worker, must have unique names. Two different workers can each have a step called "clean", with their own techniques. (Parameters are shared by name, so both would use the same `clean_parameters`.) A technique can be listed more than once in a step, in which case it is applied more than once in a sequential design.

Any other setting in a project or worker section is kept in `Outline.initialization` under the name of the section, for your own use:

```python
import chrisjen

settings = {
    "example_project": {"example_workers": "worker", "author": "me"},
    "worker": {"worker_techniques": "none", "model_type": "classify"},
}
outline = chrisjen.Project(settings).outline
print(outline.initialization["worker"])
# {'model_type': 'classify'}
print(outline.initialization["example"])
# {'author': 'me'}
```

The outline records everything it read, and the [`Outline`](reference/chrisjen/outline.md) reference lists all of its attributes. A few useful ones (`techniques` is a `dict` of each worker's steps and their techniques, and a worker with no steps has one entry named for the worker):

```python
print(outline.workers, outline.designs)
# ['worker'] {'worker': 'waterfall'}
print(outline.techniques)
# {'worker': {'worker': ['none']}}
print(outline.kinds)
# {'worker': 'worker', 'none': 'technique'}
```

## Designs

Each design is a subclass of `Workflow`. A design decides in what order the nodes are applied and whether the techniques of a step are applied one after another or are alternatives to each other.

The examples in this guide use these techniques, in addition to the ones defined in each example:

```python
@chrisjen.technique
def drop_negatives(item):
    return [x for x in item if x >= 0]


@chrisjen.technique
def scale(item, factor=2):
    return [x * factor for x in item]


@chrisjen.technique
def total(item):
    return sum(item)
```

### waterfall

The default. Nodes are applied one after another, and every technique of a step is applied in order. `results` holds the result of each node.

### kanban

Like `waterfall`, but each stage gets a deep copy of the previous stage's result. A stage can change its input (for example, sort a list in place) without changing what an earlier stage delivered. Every deliverable is in `results`.

```python
@chrisjen.technique
def sort_in_place(item):
    item.sort()
    return item


@chrisjen.technique
def add_zero(item):
    item.append(0)
    return item


settings = {
    "board_project": {"board_workers": "team"},
    "team": {
        "design": "kanban",
        "team_steps": ["order", "extend"],
        "order_techniques": "sort_in_place",
        "extend_techniques": "add_zero",
    },
}
project = chrisjen.Project(settings, item=[3, 1, 2])
print(project.apply())
# [1, 2, 3, 0]
team = project.workflow.retrieve("team").contents
print(team.results)
# {'order': [1, 2, 3], 'extend': [1, 2, 3, 0]}
print(project.item)
# [3, 1, 2]
```

### scrum

Like `waterfall`, but you control the pace. `advance` applies the next node and returns the result, so you can look at it (or change it) first. `upcoming` is the name of the next node and `done` says whether any remain. `execute` finishes whatever is left.

```python
from chrisjen import Scrum, Step, Technique

sprint = Scrum()
sprint.populate([
    Step(name="plan", contents=[Technique(name="plan", contents=lambda x: [*x, "plan"])]),
    Step(name="build", contents=[Technique(name="build", contents=lambda x: [*x, "build"])]),
    Step(name="ship", contents=[Technique(name="ship", contents=lambda x: [*x, "ship"])]),
])
item = sprint.advance([])
print(sprint.upcoming, item)
# build ['plan']
item = sprint.advance(item)
print(sprint.execute(item))
# ['plan', 'build', 'ship']
```

### pert

Steps can depend on several other steps. List a step's prerequisites in `{step}_requires`. At the project level, where the nodes are workers, list a worker's prerequisites in `{worker}_requires` in the project section. Once any step lists requirements, only the listed requirements connect the steps, so steps with none can start together. If no step lists requirements, the steps run in sequence.

`Workflow.critical_path()` returns the longest chain of steps and its length. A step's length is its `duration` parameter (1 if it has none). The critical path is the shortest time in which the whole project could finish if independent steps ran in parallel. `chrisjen` applies the steps one at a time, in an order that respects the requirements.

<!-- file: build.ini -->
```ini
[build_project]
build_workers = pipeline

[pipeline]
design = pert
pipeline_steps = fetch, parse_a, parse_b, merge
parse_a_requires = fetch
parse_b_requires = fetch
merge_requires = parse_a, parse_b

[fetch_parameters]
duration = 2

[parse_a_parameters]
duration = 5

[parse_b_parameters]
duration = 3
```

```python
for name in ["fetch", "parse_a", "parse_b", "merge"]:
    chrisjen.technique(lambda item, name=name: [*item, name], name=name)

project = chrisjen.Project("build.ini", item=[])
print(project.apply())
# ['fetch', 'parse_a', 'parse_b', 'merge']
pipeline = project.workflow.retrieve("pipeline").contents
print(sorted(pipeline.walk()))
# [['fetch', 'parse_a', 'merge'], ['fetch', 'parse_b', 'merge']]
print(pipeline.critical_path())
# (['fetch', 'parse_a', 'merge'], 8.0)
```

### agile

Repeats the whole sequence until the criterion returns a true value, or `max_iterations` passes have been made. `iterations` is the number of passes used.

```python
@chrisjen.technique
def grow(item):
    return item * 2


@chrisjen.criterion
def big_enough(result):
    return result >= 100


settings = {
    "growth_project": {"growth_workers": "grower"},
    "grower": {
        "design": "agile",
        "criteria": "big_enough",
        "max_iterations": 20,
        "grower_techniques": "grow",
    },
}
project = chrisjen.Project(settings, item=3)
print(project.apply())
# 192
print(project.workflow.retrieve("grower").contents.iterations)
# 6
```

### lean

Repeats the sequence while the score keeps improving by more than `tolerance`, up to `max_iterations` passes, and returns the best result. The criterion returns a score (higher is better). `score` and `iterations` describe the last run.

```python
@chrisjen.technique
def newton_step(item):
    return (item + 10 / item) / 2


@chrisjen.criterion
def closeness_to_root(result):
    return -abs(result * result - 10)


settings = {
    "root_project": {"root_workers": "refiner"},
    "refiner": {
        "design": "lean",
        "criteria": "closeness_to_root",
        "tolerance": 1e-9,
        "refiner_techniques": "newton_step",
    },
}
project = chrisjen.Project(settings, item=1.0)
print(round(project.apply(), 6))
# 3.162278
```

### contest

Tries every alternative and keeps the result with the best score. With several steps, an alternative is one technique from each step, so a contest between steps with two and three techniques runs six combinations. Each combination works on a deep copy of the item.

If a design's nodes are workers (for example, at the project level) instead of steps, each worker is an alternative:

```python
@chrisjen.technique
def cautious(item):
    return item + 1


@chrisjen.technique
def bold(item):
    return item * 3


@chrisjen.criterion
def largest(result):
    return result


settings = {
    "strategy_project": {
        "strategy_workers": ["slow", "fast"],
        "design": "contest",
        "criteria": "largest",
    },
    "slow": {"slow_techniques": "cautious"},
    "fast": {"fast_techniques": "bold"},
}
project = chrisjen.Project(settings, item=10)
print(project.apply())
# 30
print(project.workflow.winner, project.workflow.scores)
# fast {'slow': 11, 'fast': 30}
```

`Contest` records `results` (every combination's result), `scores`, and `winner`. Ties go to the first combination.

### survey

Like `contest`, but instead of choosing one result it returns the mean of all of them. The results must support addition and division by an integer (numbers, `numpy` arrays, and `pandas` objects do).

```python
settings = {
    "average_project": {"average_workers": "averager"},
    "averager": {
        "design": "survey",
        "averager_steps": ["scale", "combine"],
        "scale_techniques": ["enlarge", "halve"],
        "combine_techniques": "sum_all",
    },
}


@chrisjen.technique
def halve(item):
    return [x / 2 for x in item]


@chrisjen.technique
def sum_all(item):
    return sum(item)


@chrisjen.technique(name="enlarge")
def double_all(item):
    return [x * 2 for x in item]


project = chrisjen.Project(settings, item=[1, 2, 3])
print(project.apply())
# 7.5
```

### Design names

`compete` and `competition` are also accepted for `contest`, and `sequential` for `waterfall`.

## Techniques

A technique can be created in three ways:

1. **A registered function.** Use `@chrisjen.technique` (or `@chrisjen.technique(name="other_name")`). The function's first argument is the item. It must return the changed item. Other arguments are parameters and only those that the function accepts are passed (unless it takes `**kwargs`, in which case all parameters are passed).
2. **A subclass of `Technique`.** Override `implement(self, item, **kwargs)`. The name of the technique is the snake case name of the class. The subclass must be defined (or imported) before a project uses it. Subclasses receive all of the parameters.
3. **An instance built by hand,** with a function as `contents`: `chrisjen.Technique(name="x", contents=some_function)`.

`Technique.create(name)` finds a technique by name. It looks at registered functions first, then aliases, then subclasses. `none`, `null`, and `null_node` all name the built-in `NullNode`. A name that matches nothing raises a `KeyError` that lists the names that exist.

## Criteria

A criterion is a function that takes a result and returns a score (or, for `agile`, a `bool`). Register it with `@chrisjen.criterion` and refer to it with the `criteria` setting. When you build a workflow yourself, you can also pass the function directly:

```python
workflow = chrisjen.Workflow.design(
    "contest",
    [chrisjen.Step(name="s", contents=[chrisjen.Technique(name="up", contents=lambda x: x + 1)])],
    criteria=lambda result: result,
)
print(workflow.execute(1))
# 2
```

## Parameters and precedence

Keyword parameters can come from four places. When the same parameter is set in more than one place, the later item in this list wins:

1. The step's parameters (a `{step}_parameters` section).
2. The technique's parameters (a `{technique}_parameters` section).
3. The worker's parameters (a `{worker}_parameters` section), which are passed to everything the worker does.
4. Keyword arguments passed to `Project.apply` (or `Workflow.execute`).

```python
@chrisjen.technique
def add_amount(item, amount=0):
    return item + amount


settings = {
    "sum_project": {"sum_workers": "adder"},
    "adder": {"adder_steps": ["add"], "add_techniques": "add_amount"},
    "add_parameters": {"amount": 1},
    "add_amount_parameters": {"amount": 2},
}
project = chrisjen.Project(settings, item=0)
print(project.apply())
# 2
print(project.apply(amount=5))
# 5
```

## Building workflows in code

You do not have to use settings. Every part can be created directly. `Workflow.design(name, nodes, **options)` creates a design by name and connects the nodes (in the order given, or according to `requirements`).

```python
steps = [
    chrisjen.Step(
        name="clean",
        contents=[chrisjen.Technique(name="drop_negatives", contents=drop_negatives)],
    ),
    chrisjen.Step(
        name="resize",
        contents=[chrisjen.Technique(name="scale", contents=scale, parameters={"factor": 3})],
    ),
]
workflow = chrisjen.Workflow.design("waterfall", steps, name="prepare")
print(workflow.execute([1, -1, 2]))
# [3, 6]
```

A `Worker` puts a workflow inside another workflow:

```python
prepare = chrisjen.Worker(name="prepare", contents=workflow)
summarize = chrisjen.Step(
    name="summarize",
    contents=[chrisjen.Technique(name="total", contents=total)],
)
project_workflow = chrisjen.Workflow.design("waterfall", [prepare, summarize])
print(project_workflow.execute([1, -1, 2]))
# 9
```

## Custom designs

To add a design, subclass `Workflow` and write an `execute` method. The subclass is found by its snake case class name. `self.sequence` is the list of nodes in the order they should run, and each node's `complete(item, **kwargs)` applies it.

```python
import dataclasses


@dataclasses.dataclass
class TwiceOver(chrisjen.Workflow):
    """Applies the whole sequence two times."""

    def execute(self, item, **kwargs):
        self.results.clear()
        for _ in range(2):
            for node in self.sequence:
                item = node.complete(item, **kwargs)
                self.results[node.name] = item
        return item


settings = {
    "twice_project": {"twice_workers": "worker"},
    "worker": {"design": "twice_over", "worker_techniques": "scale"},
}
print(chrisjen.Project(settings, item=[1, 2]).apply())
# [4, 8]
```

If your design needs criteria, iterations, or a `select` rule, use the attributes that `Workflow` already has: `criteria`, `max_iterations`, `tolerance`, `select`, and `durations`. The `_criteria()` method returns the criteria function (looking up a name if needed). To compare alternatives, subclass `chrisjen.workflows.Comparative` and use its `compare` method, which returns a `dict` of a label and result for every alternative.

## Using the graph

A `Workflow` is a [holden](https://WithPrecedent.github.io/holden) `System`, a directed graph, so everything `holden` offers is available. The graph holds only node *names*. The nodes themselves are in `library` and are found with `retrieve`.

```python
workflow = chrisjen.Workflow.design("waterfall", steps, name="prepare")
print(workflow.contents)
# {'clean': {'resize'}, 'resize': set()}
print(workflow.root, workflow.endpoint)
# ['clean'] ['resize']
print(workflow.edges.contents)
# [('clean', 'resize')]
print(workflow.retrieve("clean").name)
# clean
print(workflow.to_dot(name="prepare"), end="")
# digraph prepare {
# clean -> resize
# }
```

## Using the settings and the clerk

`Project.idea` is a `bobbie.Settings`. It is a `dict`, so you can read any section, and its methods (such as `inject`, which adds settings to an object as attributes) are available. If you already have a `bobbie.Settings`, pass it to `Project` and it is used as is.

`Project.clerk` is a `nagata.FileManager`. Its `save` and `load` methods take a `file_name`, an optional `folder` (`input`, `interim`, or `output`), and an optional `file_format` (or use a file name with an extension, such as "results.csv" if `pandas` is installed). The folders are inside `root / identification`, so each run of a project has its own folders.

## Errors you may see

| Error | Cause |
| --- | --- |
| `ValueError: the settings have no section ... "_project"` | The settings need a section named `{name}_project`. |
| `ValueError: section ... must list workers` | The project section needs a `{name}_workers` setting. |
| `ValueError: the settings have no section for worker ...` | A worker named in `{name}_workers` has no section. |
| `ValueError: worker ... needs steps ... or techniques ...` | A worker's section has neither a `{worker}_steps` nor a `{worker}_techniques` setting. |
| `ValueError: the workers of ... must be unique` | A worker (or step) name is listed twice in the same list. |
| `TypeError: section ... must be a mapping of settings` | A section in the settings is a single value instead of a group of settings. |
| `KeyError: ... is not a known technique` | No function is registered, and no `Technique` subclass exists, with that name. Check that the module that defines it has been imported. |
| `KeyError: ... is not a known workflow design` | The design name is misspelled, or the custom design has not been defined. |
| `ValueError: the ... design needs a criteria function` | `agile`, `lean`, and `contest` need a `criteria` setting. |
| `KeyError: ... is not a registered criterion` | The `criteria` setting names a function that was not registered with `@chrisjen.criterion`. |
| `ValueError: workflow has a cycle` | The `{step}_requires` settings of a `pert` workflow point in a circle. This is found when the workflow is published. |

Names in ini files that look like booleans or numbers (`yes`, `no`, `true`, `false`, `1`) are converted by the ini loader before `chrisjen` sees them, so avoid them as names of workers, steps, or techniques.
