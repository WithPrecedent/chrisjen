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
| `{step}_technique_type` | `{worker}` | The type of technique to look in for the techniques of a step, such as `cleaner` (`{worker}_technique_type` for a worker with no steps). Optional. |
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
def drop_negatives(item):
    return [x for x in item if x >= 0]

chrisjen.Technique.register("drop_negatives", drop_negatives)


def scale(item, factor = 2):
    return [x * factor for x in item]

chrisjen.Technique.register("scale", scale)


def total(item):
    return sum(item)

chrisjen.Technique.register("total", total)
```

### waterfall

The default. Nodes are applied one after another, and every technique of a step is applied in order. `results` holds the result of each node.

### kanban

Like `waterfall`, but each stage gets a deep copy of the previous stage's result. A stage can change its input (for example, sort a list in place) without changing what an earlier stage delivered. Every deliverable is in `results`.

```python
def sort_in_place(item):
    item.sort()
    return item

chrisjen.Technique.register("sort_in_place", sort_in_place)


def add_zero(item):
    item.append(0)
    return item

chrisjen.Technique.register("add_zero", add_zero)


settings = {
    "board_project": {"board_workers": "team"},
    "team": {
        "design": "kanban",
        "team_steps": ["order", "extend"],
        "order_techniques": "sort_in_place",
        "extend_techniques": "add_zero",
    },
}
project = chrisjen.Project(settings, item = [3, 1, 2])
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
    Step(name = "plan", contents = [Technique(name = "plan", contents = lambda x: [*x, "plan"])]),
    Step(name = "build", contents = [Technique(name = "build", contents = lambda x: [*x, "build"])]),
    Step(name = "ship", contents = [Technique(name = "ship", contents = lambda x: [*x, "ship"])]),
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
    chrisjen.Technique.register(name, lambda item, name = name: [*item, name])

project = chrisjen.Project("build.ini", item = [])
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
def grow(item):
    return item * 2

chrisjen.Technique.register("grow", grow)


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
project = chrisjen.Project(settings, item = 3)
print(project.apply())
# 192
print(project.workflow.retrieve("grower").contents.iterations)
# 6
```

### lean

Repeats the sequence while the score keeps improving by more than `tolerance`, up to `max_iterations` passes, and returns the best result. The criterion returns a score (higher is better). `score` and `iterations` describe the last run.

```python
def newton_step(item):
    return (item + 10 / item) / 2

chrisjen.Technique.register("newton_step", newton_step)


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
project = chrisjen.Project(settings, item = 1.0)
print(round(project.apply(), 6))
# 3.162278
```

### contest

Tries every alternative and keeps the result with the best score. With several steps, an alternative is one technique from each step, so a contest between steps with two and three techniques runs six combinations. Each combination works on a deep copy of the item.

If a design's nodes are workers (for example, at the project level) instead of steps, each worker is an alternative:

```python
def cautious(item):
    return item + 1

chrisjen.Technique.register("cautious", cautious)


def bold(item):
    return item * 3

chrisjen.Technique.register("bold", bold)


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
project = chrisjen.Project(settings, item = 10)
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


def halve(item):
    return [x / 2 for x in item]

chrisjen.Technique.register("halve", halve)


def sum_all(item):
    return sum(item)

chrisjen.Technique.register("sum_all", sum_all)


def double_all(item):
    return [x * 2 for x in item]

chrisjen.Technique.register("enlarge", double_all)


project = chrisjen.Project(settings, item = [1, 2, 3])
print(project.apply())
# 7.5
```

### Design names

`compete` and `competition` are also accepted for `contest`, and `sequential` for `waterfall`.

## Techniques

A `Technique` is an object that wraps a tool. It has three attributes:

| Attribute | Meaning |
| --- | --- |
| `name` | How the technique is referred to in settings and workflows. |
| `contents` | The tool: any callable, or its import path as a `str` (such as `"statistics.fmean"`, or `"package.module:Class.method"`). |
| `parameters` | Keyword parameters for the tool. |

When a technique is applied, its `implement` method is called with the item and all of the parameters. The default `implement` calls the tool with the item as the first argument and passes only the parameters that the tool accepts (unless it takes `**kwargs`, in which case it gets all of them). An import path is only imported when the technique is used (`Technique.resolve()` returns the tool), so a technique can wrap a package that might not be installed, and a mistake in the path raises an `ImportError` when the technique is applied.

```python
mean = chrisjen.Technique("mean", contents = "statistics.fmean")
print(mean.complete([1, 2, 3, 6]))
# 3.0
rounded = chrisjen.Technique("rounded", contents = round, parameters = {"ndigits": 1})
print(rounded.complete(3.14159))
# 3.1
```

### Registering

Techniques are found by name in registries. `Technique.register` creates a technique and registers it, or registers a technique you have built. It returns the technique, and a technique with the same name is replaced.

```python
chrisjen.Technique.register("square_root", "math.sqrt")
chrisjen.Technique.register("one_digit", round, {"ndigits": 1})
chrisjen.Technique.register(chrisjen.Technique("length", contents = len))
print(chrisjen.Technique.create("square_root").complete(16))
# 4.0
```

The techniques in `Technique.registry` are the general ones. Subclasses of `Technique` are registered too, by their snake case class name. To use one, define (or import) it before creating a project.

### Types

Each **type** of technique has its own registry. A type is a subclass of `Technique` that also inherits from `abc.ABC`:

```python
import abc


class Cleaner(chrisjen.Technique, abc.ABC):
    """Techniques that clean data."""


class Analyzer(chrisjen.Technique, abc.ABC):
    """Techniques that analyze data."""


Cleaner.register("drop_blanks", lambda item: [x for x in item if x])
Analyzer.register("count", len)
print(chrisjen.Technique.types["cleaner"] is Cleaner)
# True
print(chrisjen.Technique.available()["cleaner"])
# ['drop_blanks']
```

`Technique.types` is a `dict` of the names of all of the types and the types. (The general `Technique` is one of them, called "technique".) `Technique.available()` lists the registered names of each type. Every other subclass of a type is registered in the registry of that type. A subclass of `Technique` that does not inherit from `abc.ABC` is registered in the general registry.

### Finding techniques

| You write | It looks in |
| --- | --- |
| `Technique.create("name")` | Every type. The name must be registered in only one, or a `KeyError` says which types have it. |
| `Technique.create("cleaner.name")` or `Technique.create("name", kind="cleaner")` | Only the `Cleaner` type. `kind` can be the name or the class. |
| `Cleaner.create("name")` | Only the `Cleaner` type. |
| `clean_technique_type = cleaner` in settings | Only the `Cleaner` type, for the techniques of the step "clean". Use `{worker}_technique_type` for a worker with no steps. |

In settings, a name may also include its type, as in `clean_techniques = cleaner.drop_blanks`.

```python
Analyzer.register("drop_blanks", lambda item: [x for x in item if not x])
print(chrisjen.Technique.create("cleaner.drop_blanks").complete([0, 1, 2]))
# [1, 2]
print(chrisjen.Technique.create("drop_blanks", kind = "analyzer").complete([0, 1, 2]))
# [0]
```

`create` returns a *copy* of the registered technique, so techniques in different steps never share their parameters or state. The `parameters` from your settings are combined with the parameters that the technique was registered with (your settings win). The tool in `contents` is copied too, so a tool with state of its own (such as a model) is not shared, unless the tool cannot be copied (because it holds a lock or a connection, for example), in which case the copies share it.

`none`, `null`, and `null_node` are three names in the general registry for the built-in `NullNode`, which returns its item unchanged.

### Calling tools differently

The default `implement` fits functions. A type can override it to fit other kinds of tools. This is how one interface wraps many packages: each type of technique knows how to call the tools of its type, and everything else (the settings, the workflows, the designs) treats them the same. The next section has a complete example.

## Criteria

A criterion is a function that takes a result and returns a score (or, for `agile`, a `bool`). Register it with `@chrisjen.criterion` and refer to it with the `criteria` setting. When you build a workflow yourself, you can also pass the function directly:

```python
workflow = chrisjen.Workflow.design(
    "contest",
    [chrisjen.Step(name = "s", contents = [chrisjen.Technique(name = "up", contents = lambda x: x + 1)])],
    criteria = lambda result: result,
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
def add_amount(item, amount = 0):
    return item + amount

chrisjen.Technique.register("add_amount", add_amount)


settings = {
    "sum_project": {"sum_workers": "adder"},
    "adder": {"adder_steps": ["add"], "add_techniques": "add_amount"},
    "add_parameters": {"amount": 1},
    "add_amount_parameters": {"amount": 2},
}
project = chrisjen.Project(settings, item = 0)
print(project.apply())
# 2
print(project.apply(amount = 5))
# 5
```

## Building workflows in code

You do not have to use settings. Every part can be created directly. `Workflow.design(name, nodes, **options)` creates a design by name and connects the nodes (in the order given, or according to `requirements`).

```python
steps = [
    chrisjen.Step(
        name = "clean",
        contents = [chrisjen.Technique(name = "drop_negatives", contents = drop_negatives)],
    ),
    chrisjen.Step(
        name = "resize",
        contents = [chrisjen.Technique(name = "scale", contents = scale, parameters = {"factor": 3})],
    ),
]
workflow = chrisjen.Workflow.design("waterfall", steps, name = "prepare")
print(workflow.execute([1, -1, 2]))
# [3, 6]
```

A `Worker` puts a workflow inside another workflow:

```python
prepare = chrisjen.Worker(name = "prepare", contents = workflow)
summarize = chrisjen.Step(
    name = "summarize",
    contents = [chrisjen.Technique(name = "total", contents = total)],
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
print(chrisjen.Project(settings, item = [1, 2]).apply())
# [4, 8]
```

If your design needs criteria, iterations, or a `select` rule, use the attributes that `Workflow` already has: `criteria`, `max_iterations`, `tolerance`, `select`, and `durations`. The `_criteria()` method returns the criteria function (looking up a name if needed). To compare alternatives, subclass `chrisjen.workflows.Comparative` and use its `compare` method, which returns a `dict` of a label and result for every alternative.

## Building a package on chrisjen

`chrisjen` provides the structure of a project: settings, workflows, designs, and a registry for each type of technique. A package built on it (for example, a data science package) supplies the types of techniques and the tools that they wrap. The pattern is:

1. **Define a type for each kind of work.** Give each an `implement` method that calls the tools of that type the way they need to be called.
2. **Register the tools.** Use import paths for tools from packages that may not be installed. Register default parameters with them.
3. **Register everything when your package is imported,** so that a user only needs to import it and write settings.

This example has three types. Each calls a different kind of tool: a `Cleaner` calls a function, a `Munger` calls a method of the item itself (the tool is the name of the method), and an `Analyzer` builds an object from the item and then calls one of its methods. All of the tools are from the standard library:

```python
import dataclasses

from chrisjen import utilities


class Cleaner(chrisjen.Technique, abc.ABC):
    """Calls a function with the item."""


@dataclasses.dataclass
class Munger(chrisjen.Technique, abc.ABC):
    """Calls the method of the item that is named in `contents`."""

    def implement(self, item, **kwargs):
        method = getattr(item, self.contents)
        return method(**utilities.accepted_arguments(method, kwargs))


@dataclasses.dataclass
class Analyzer(chrisjen.Technique, abc.ABC):
    """Builds an object from the item and calls one of its methods."""

    method: str = "most_common"

    def implement(self, item, **kwargs):
        summary = self.resolve()(item.split())
        method = getattr(summary, self.method)
        return method(**utilities.accepted_arguments(method, kwargs))


Cleaner.register("squeeze", lambda item: " ".join(item.split()))
Munger.register("strip", "strip")
Munger.register("lowercase", "lower")
Analyzer.register("frequencies", "collections.Counter")
```

The settings say which type each step uses, so all of the `chrisjen` designs and features work with them:

```python
settings = {
    "words_project": {"words_workers": ["prepare", "analyze"]},
    "prepare": {
        "prepare_steps": ["tidy", "simplify", "spacing"],
        "tidy_techniques": "strip",
        "tidy_technique_type": "munger",
        "simplify_techniques": "lowercase",
        "simplify_technique_type": "munger",
        "spacing_techniques": "squeeze",
        "spacing_technique_type": "cleaner",
    },
    "analyze": {
        "analyze_techniques": "frequencies",
        "analyze_technique_type": "analyzer",
    },
    "frequencies_parameters": {"n": 1},
}
text = "  The  cat and THE hat and the bat "
project = chrisjen.Project(settings, item = text)
print(project.apply())
# [('the', 3)]
```

Because every tool is a registered technique, the same workflow can compare them. This contest between two ways of counting the words is set up with a change of design and a criterion:

```python
Analyzer.register("top_two", "collections.Counter", {"n": 2})


@chrisjen.criterion
def most_words_covered(result):
    return sum(count for _, count in result)


settings["analyze"] = {
    "design": "contest",
    "criteria": "most_words_covered",
    "analyze_steps": ["count"],
    "count_techniques": "frequencies, top_two",
    "count_technique_type": "analyzer",
}
project = chrisjen.Project(settings, item = text)
print(project.apply())
# [('the', 3), ('and', 2)]
print(project.workflow.retrieve("analyze").contents.winner)
# top_two
```

A few practical points for packages:

* Keep types abstract (inherit from `abc.ABC`), and register tools with `register`, not as subclasses, unless a tool needs its own code. Subclasses are found by their snake case names, and a name must be unique within a type.
* Use import paths (`"package.module.tool"`) for optional packages. A missing package only raises an `ImportError` if the technique is used.
* Give tools the parameters they usually need as registered defaults, so that a settings file only lists the changes.
* Use `Technique.available()` to show users what is registered, and `Technique.types` to find the types.
* `chrisjen.utilities.accepted_arguments(tool, parameters)` returns the parameters that a tool accepts. Use it in `implement` so that parameters shared by the techniques of a step do not break tools that do not take them.

## Using the graph

A `Workflow` is a [holden](https://WithPrecedent.github.io/holden) `System`, a directed graph, so everything `holden` offers is available. The graph holds only node *names*. The nodes themselves are in `library` and are found with `retrieve`.

```python
workflow = chrisjen.Workflow.design("waterfall", steps, name = "prepare")
print(workflow.contents)
# {'clean': {'resize'}, 'resize': set()}
print(workflow.root, workflow.endpoint)
# ['clean'] ['resize']
print(workflow.edges.contents)
# [('clean', 'resize')]
print(workflow.retrieve("clean").name)
# clean
print(workflow.to_dot(name = "prepare"), end = "")
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
| `KeyError: ... is not a known technique` | Nothing is registered with that name (in that type, if the type was named). The message lists what is registered. Check that the module that registers it has been imported. |
| `KeyError: ... is registered in more than one type of technique` | Name the type: `{step}_technique_type`, or write the name as `type.name`. |
| `KeyError: ... is not a type of technique` | The type named in a `..._technique_type` setting (or `kind`) does not exist. Types are the subclasses of `Technique` that inherit from `abc.ABC`. |
| `ImportError: cannot import ...` | The import path of a technique's tool is wrong, or its package is not installed. This is raised when the technique is used. |
| `TypeError: technique ... wraps ..., which is not callable` | The tool is not callable. Wrap a callable, or override `implement` in the type of technique. |
| `NotImplementedError: technique ... has no tool` | A `Technique` has no `contents` and its type does not override `implement`. |
| `KeyError: ... is not a known workflow design` | The design name is misspelled, or the custom design has not been defined. |
| `ValueError: the ... design needs a criteria function` | `agile`, `lean`, and `contest` need a `criteria` setting. |
| `KeyError: ... is not a registered criterion` | The `criteria` setting names a function that was not registered with `@chrisjen.criterion`. |
| `ValueError: workflow has a cycle` | The `{step}_requires` settings of a `pert` workflow point in a circle. This is found when the workflow is published. |

Names in ini files that look like booleans or numbers (`yes`, `no`, `true`, `false`, `1`) are converted by the ini loader before `chrisjen` sees them, so avoid them as names of workers, steps, or techniques.
