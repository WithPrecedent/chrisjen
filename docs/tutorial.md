# Tutorial

This tutorial builds a small project in stages. It starts with a few lines of Python and ends with a project that compares alternatives, reads its settings from a file, and saves its results. Every example on this page is run by the `chrisjen` unit tests, so you can copy and paste them.

## The vocabulary

A `chrisjen` project has three levels:

| Level | What it is | In code |
| --- | --- | --- |
| Worker | A major part of a project, such as "prepare" or "model". | `chrisjen.Worker` |
| Step | A stage of a worker, such as "clean" or "scale". | `chrisjen.Step` |
| Technique | An action in a step, such as "drop_negatives". | `chrisjen.Technique` |

The **item** is the data (or any object) that the project works on. Each technique takes the item and returns the changed item, and the result of one becomes the input of the next.

## 1. Write techniques

A technique is an object that wraps a tool, and a tool is anything callable. The simplest tool is a function that takes the item as its first argument and returns the changed item. `Technique.register` creates a technique that wraps a function and registers it, so that it can be referred to by name:

```python
import chrisjen


def drop_negatives(item):
    return [x for x in item if x >= 0]


def scale(item, factor=2):
    return [x * factor for x in item]


def total(item):
    return sum(item)


for function in (drop_negatives, scale, total):
    chrisjen.Technique.register(function.__name__, function)
```

The functions are unchanged, so you can still call them yourself:

```python
print(scale([1, 2, 3]))
# [2, 4, 6]
```

## 2. Describe the project

Settings are a collection of sections. A project needs a section whose name ends in `_project`. The `{name}_workers` setting in that section lists the project's workers, and each worker has a section of its own:

```python
settings = {
    "report_project": {"report_workers": ["prepare", "summarize"]},
    "prepare": {
        "prepare_steps": ["clean", "resize"],
        "clean_techniques": "drop_negatives",
        "resize_techniques": "scale",
    },
    "summarize": {"summarize_techniques": "total"},
}
```

Here the "prepare" worker has two steps, "clean" and "resize". The `{step}_techniques` settings say which techniques each step uses. The "summarize" worker has no steps, so `{worker}_techniques` lists its techniques directly.

## 3. Create and run the project

```python
project = chrisjen.Project(settings, item=[3, -1, 4, -1, 5])
print(project.apply())
# 24
```

Creating a `Project` reads the settings and drafts an `outline`. The first call to `apply` builds the workflow (this is called publishing) and runs it. You can look at each stage:

```python
print(project.outline.summary)
# report (waterfall)
#   prepare (waterfall)
#     clean: drop_negatives
#     resize: scale
#   summarize (waterfall)
#     total
print(project.workflow.walk())
# [['prepare', 'summarize']]
```

`project.workflow` is a graph of the workers. Each worker is itself a node with its own workflow of steps:

```python
prepare = project.workflow.retrieve("prepare")
print(prepare.contents.walk())
# [['clean', 'resize']]
print(prepare.contents.results)
# {'clean': [3, 4, 5], 'resize': [6, 8, 10]}
```

Each workflow keeps the result of every node from its latest run in `results`.

## 4. Use a settings file

Settings can live in an ini, toml, json, yaml, xml, or Python file. Pass its path instead of a `dict`. In an ini file, `bobbie` (the settings package that `chrisjen` uses) turns text into numbers, `True` and `False`, and comma-separated lists automatically.

<!-- file: report.ini -->
```ini
[report_project]
report_workers = prepare, summarize

[prepare]
prepare_steps = clean, resize
clean_techniques = drop_negatives
resize_techniques = scale

[summarize]
summarize_techniques = total
```

```python
project = chrisjen.Project("report.ini", item=[3, -1, 4, -1, 5])
print(project.apply())
# 24
```

The same project can be run on other data. Pass a new item to `apply`:

```python
print(project.apply([10, -5, 20]))
# 60
```

## 5. Set parameters

A technique function's other arguments are parameters. Their values come from a section named `{name}_parameters`, where `name` is the name of the technique, step, or worker. Add one to the settings to change the `factor` of `scale`:

```python
settings["scale_parameters"] = {"factor": 10}
project = chrisjen.Project(settings, item=[3, -1, 4, -1, 5])
print(project.apply())
# 120
```

If a parameter section belongs to a step (here, "resize"), it applies to all the techniques of the step that accept the parameter. A technique's own parameters win over its step's. Parameters passed to `apply` win over both, and parameters in a worker's section are passed to everything in that worker.

```python
print(project.apply(factor=1))
# 12
```

Only parameters that a function accepts are passed to it. A parameter meant for one technique will not break the others.

## 6. Several techniques in a step

In the default `waterfall` design, every technique in a step is applied in order:

```python
settings = {
    "numbers_project": {"numbers_workers": "changer"},
    "changer": {
        "changer_steps": ["change"],
        "change_techniques": ["drop_negatives", "scale", "scale"],
    },
}
project = chrisjen.Project(settings, item=[1, -2, 3])
print(project.apply())
# [4, 12]
```

## 7. Compare alternatives

Some designs treat the techniques of a step as *alternatives* instead. `contest` tries every combination and keeps the result with the best score. It needs a **criterion**, a function that takes a result and returns a score (higher is better, unless you set `select = min`).

```python
def halve(item):
    return [x / 2 for x in item]

chrisjen.Technique.register("halve", halve)


@chrisjen.criterion
def smallest_spread(item):
    return -(max(item) - min(item))


settings = {
    "compare_project": {"compare_workers": "scaler"},
    "scaler": {
        "design": "contest",
        "criteria": "smallest_spread",
        "scaler_steps": ["shrink"],
        "shrink_techniques": ["scale", "halve", "none"],
    },
}
project = chrisjen.Project(settings, item=[1, 2, 3])
print(project.apply())
# [0.5, 1.0, 1.5]
contest = project.workflow.retrieve("scaler").contents
print(contest.winner, contest.scores)
# halve {'scale': -4, 'halve': -1.0, 'none': -2}
```

`none` is a built-in technique that does nothing. It is useful for testing whether a step helps at all.

With more than one step, a contest tries every combination of techniques. Each combination is labeled with the names of its techniques joined with ">":

```python
settings = {
    "compare_project": {"compare_workers": "scaler"},
    "scaler": {
        "design": "contest",
        "criteria": "smallest_spread",
        "scaler_steps": ["clean", "shrink"],
        "clean_techniques": ["drop_negatives", "none"],
        "shrink_techniques": ["scale", "halve"],
    },
}
project = chrisjen.Project(settings, item=[-8, 1, 2, 3])
project.apply()
contest = project.workflow.retrieve("scaler").contents
print(sorted(contest.scores))
# ['drop_negatives > halve', 'drop_negatives > scale', 'none > halve', 'none > scale']
print(contest.winner)
# drop_negatives > halve
```

The other designs are described in the [advanced user guide](advanced.md) and [recipes](recipes.md).

## 8. Write a technique as a class

When a technique needs more than a call, or you want to keep related code together, subclass `chrisjen.Technique` and write an `implement` method. The class is registered by its snake case name:

```python
import dataclasses


@dataclasses.dataclass
class KeepEvens(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return [x for x in item if x % 2 == 0]


settings = {
    "evens_project": {"evens_workers": "sorter"},
    "sorter": {"sorter_techniques": ["keep_evens", "total"]},
}
print(chrisjen.Project(settings, item=[1, 2, 3, 4]).apply())
# 6
```

## 9. Wrap tools from other packages

A technique wraps a tool, and the tool is anything callable. You can register a function from another package directly, or give its import path as a `str`. A path is only imported when the technique is used, so techniques can wrap optional packages, and a mistake in a path is reported when the technique is applied.

Here, three tools from the standard library are wrapped. The third argument of `register` sets default parameters, which are passed to the tool (and can be overridden in your settings):

```python
chrisjen.Technique.register("mean", "statistics.fmean")
chrisjen.Technique.register("root", "math.sqrt")
chrisjen.Technique.register("rounded", round, {"ndigits": 1})

settings = {
    "wrap_project": {"wrap_workers": "measure"},
    "measure": {
        "measure_steps": ["average", "finish"],
        "average_techniques": "mean",
        "finish_techniques": "root, rounded",
    },
}
project = chrisjen.Project(settings, item=[2, 8])
print(project.apply())
# 2.2
```

The mean of 2 and 8 is 5.0, its square root is about 2.236, and `round` keeps one digit. A `<name>_parameters` section in your settings changes the parameters:

```python
settings["rounded_parameters"] = {"ndigits": 3}
print(chrisjen.Project(settings, item=[2, 8]).apply())
# 2.236
```

Parameters that a tool does not accept are left out, so you can share parameters among the techniques of a step without breaking any of them.

A `Technique` calls its tool with the item as the first argument. Tools that need to be called differently (for example, a class that must be created from the parameters and then used, or a method of the item itself) are wrapped by a *type* of technique that says how, which is the next section.

## 10. Types of techniques

Different kinds of tools need to be called in different ways. A **type** of technique is a subclass of `Technique` and `abc.ABC`. Each type has its own registry, and it can override `implement` to change how its tools are called. This example has a type for cleaning data and a type for summarizing data with a distribution class:

```python
import abc


class Cleaner(chrisjen.Technique, abc.ABC):
    """Techniques that clean data."""


class Modeler(chrisjen.Technique, abc.ABC):
    """Techniques that build an object from parameters and then use it."""

    method = "cdf"

    def implement(self, item, **kwargs):
        model = self.resolve()(**kwargs)
        return getattr(model, self.method)(item)


Cleaner.register("filter", lambda item: [x for x in item if x != 0])
Modeler.register("normal", "statistics.NormalDist", {"mu": 0, "sigma": 1})
```

Then a step can name the type of its techniques with `{step}_technique_type` (or `{worker}_technique_type`, for a worker without steps). With settings like these, the "tidy" worker only looks in the `Cleaner` registry:

```python
settings = {
    "types_project": {"types_workers": ["tidy", "summarize", "model"]},
    "tidy": {
        "tidy_techniques": "filter",
        "tidy_technique_type": "cleaner",
    },
    "summarize": {"summarize_techniques": "mean"},
    "model": {
        "model_techniques": "normal",
        "model_technique_type": "modeler",
    },
    "normal_parameters": {"mu": 2, "sigma": 2},
}
print(chrisjen.Project(settings, item=[0, 2, 0, 2]).apply())
# 0.5
```

The item `[0, 2, 0, 2]` is cleaned to `[2, 2]` and averaged (with the `mean` technique from the previous section) to `2.0`. The normal distribution with a mean of 2 then gives `cdf(2.0) == 0.5`. Parameters in `normal_parameters` are combined with the parameters registered with the technique.

Naming the type is optional. Without it, a name is looked up in every type, and a name that is registered in more than one type (like `filter` above) raises a `KeyError` that tells you to name the type. You can also write the type in the name, as `cleaner.filter`. `Technique.available()` lists everything that is registered, by type:

```python
class Analyzer(chrisjen.Technique, abc.ABC):
    """Techniques that analyze data."""


Analyzer.register("filter", lambda item: [x for x in item if x > 0])
print(chrisjen.Technique.create("cleaner.filter").complete([0, 1, -1]))
# [1, -1]
print(chrisjen.Technique.create("filter", kind="analyzer").complete([0, 1, -1]))
# [1]
print(sorted(chrisjen.Technique.available()["cleaner"]))
# ['filter']
```

A technique can also be defined by subclassing a type. The class is registered under its snake case name in the registry of its type:

```python
import dataclasses


@dataclasses.dataclass
class DropNones(Cleaner):
    def implement(self, item, **kwargs):
        return [x for x in item if x is not None]


print(chrisjen.Technique.create("drop_nones").complete([1, None, 2]))
# [1, 2]
print(sorted(Cleaner.registry))
# ['drop_nones', 'filter']
```

`chrisjen` does not define any types beyond the general `Technique`. It is meant to be the foundation for packages that do (a data science package could have `Cleaner`, `Munger`, `Analyzer`, and `Visualizer` types that wrap `pandas`, `scikit-learn`, `matplotlib`, and so on). The [advanced user guide](advanced.md) describes how registries and lookups work.

## 11. Save and load files

A project's `clerk` manages files. It creates `input`, `interim`, and `output` folders when it is first used:

```python
import pathlib
import tempfile

root = pathlib.Path(tempfile.mkdtemp())
project = chrisjen.Project("report.ini", item=[1, 2, 3], root=root)
result = project.apply()
project.clerk.save(result, file_name="result", file_format="pickle")
print(project.clerk.load(file_name="result", file_format="pickle", folder="output"))
# 12
```

The clerk is a `nagata.FileManager`. See the [nagata documentation](https://WithPrecedent.github.io/nagata) for its file formats. Settings in a "files" section of your settings apply to it:

```python
settings = {
    "report_project": {"report_workers": "worker"},
    "worker": {"worker_techniques": "total"},
    "files": {"file_encoding": "utf-8"},
}
project = chrisjen.Project(settings, root=root)
print(project.clerk.framework.settings["file_encoding"])
# utf-8
```

## 12. Draw the workflow

`to_dot` returns [Graphviz](https://graphviz.org/) text (and writes it to a file if you pass `path`). `to_mermaid` returns [mermaid](https://mermaid.js.org/) text, which many Markdown tools can draw.

```python
project = chrisjen.Project("report.ini")
print(project.to_dot())
# digraph "report" {
#   subgraph "cluster_prepare" {
#     label = "prepare (waterfall)";
#     "prepare..clean" [label = "clean\ndrop_negatives"];
#     "prepare..resize" [label = "resize\nscale"];
#     "prepare..clean" -> "prepare..resize";
#   }
#   subgraph "cluster_summarize" {
#     label = "summarize (waterfall)";
#     "summarize..summarize" [label = "summarize\ntotal"];
#   }
#   "prepare..resize" -> "summarize..summarize";
# }
```

## Next steps

* The [advanced user guide](advanced.md) describes every design, how techniques are registered and found, how settings are read, and how to add your own designs.
* The [recipes](recipes.md) show complete examples of each design.
