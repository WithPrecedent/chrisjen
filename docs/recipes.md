# Recipes

Short, complete examples for common jobs. Except where noted, they are run by the `chrisjen` unit tests. See the [tutorial](tutorial.md) for the basics and the [advanced user guide](advanced.md) for details.

## Pick the best of several methods

A forecast can be smoothed in different ways. A `contest` runs each way on the same data and keeps the one with the lowest error. The item here is a `dict`, and each technique adds a "prediction" to it. The criterion reads the prediction and returns its error, and `select = min` keeps the lowest.

```python
import dataclasses
import statistics

import chrisjen


def last_value(item):
    values = item["values"]
    return {**item, "prediction": values[-1]}

chrisjen.Technique.register("last_value", last_value)


def average(item):
    return {**item, "prediction": statistics.fmean(item["values"])}

chrisjen.Technique.register("average", average)


def recent_average(item, window=3):
    return {**item, "prediction": statistics.fmean(item["values"][-window:])}

chrisjen.Technique.register("recent_average", recent_average)


@chrisjen.criterion
def forecast_error(result):
    return abs(result["prediction"] - result["truth"])


settings = {
    "forecast_project": {"forecast_workers": "forecaster"},
    "forecaster": {
        "design": "contest",
        "criteria": "forecast_error",
        "select": "min",
        "forecaster_steps": ["predict"],
        "predict_techniques": ["last_value", "average", "recent_average"],
    },
}
data = {"values": [10, 12, 11, 13, 14, 15], "truth": 16}
project = chrisjen.Project(settings, item=data)
best = project.apply()
contest = project.workflow.retrieve("forecaster").contents
print(contest.winner, best["prediction"])
# last_value 15
print(contest.scores)
# {'last_value': 1, 'average': 3.5, 'recent_average': 2.0}
```

## Try several values of a parameter

Techniques are chosen by name, and a technique can be registered with default parameters. To compare parameter values, register the same tool once for each value:

```python
for window in (2, 3, 5):
    chrisjen.Technique.register(
        f"window_{window}", recent_average, {"window": window}
    )

settings["forecaster"]["predict_techniques"] = ["window_2", "window_3", "window_5"]
project = chrisjen.Project(settings, item=data)
project.apply()
contest = project.workflow.retrieve("forecaster").contents
print(contest.winner, contest.scores)
# window_2 {'window_2': 1.5, 'window_3': 2.0, 'window_5': 3.0}
```

## Average several approaches

`survey` runs every combination and averages the results, instead of choosing one. Here, two ways of estimating a total are averaged:

```python
def estimate_low(item):
    return sum(item) * 0.9

chrisjen.Technique.register("estimate_low", estimate_low)


def estimate_high(item):
    return sum(item) * 1.1

chrisjen.Technique.register("estimate_high", estimate_high)


settings = {
    "estimate_project": {"estimate_workers": "estimator"},
    "estimator": {
        "design": "survey",
        "estimator_techniques": ["estimate_low", "estimate_high"],
    },
}
print(chrisjen.Project(settings, item=[10, 20, 30]).apply())
# 60.0
```

## Repeat until the result is good enough

`agile` repeats a workflow until a criterion is satisfied. This example halves a step size until it is small enough, and `max_iterations` is a safety limit:

```python
def halve_step(item):
    return item / 2

chrisjen.Technique.register("halve_step", halve_step)


@chrisjen.criterion
def small_enough(result):
    return result < 0.01


settings = {
    "shrink_project": {"shrink_workers": "shrinker"},
    "shrinker": {
        "design": "agile",
        "criteria": "small_enough",
        "max_iterations": 50,
        "shrinker_techniques": "halve_step",
    },
}
project = chrisjen.Project(settings, item=1.0)
print(project.apply())
# 0.0078125
print(project.workflow.retrieve("shrinker").contents.iterations)
# 7
```

## Run one project on many inputs

A project's settings are read once. `apply` can be called again with new items, and the same workflow is reused. Use `automatic=True` for a one-shot run instead:

```python
settings = {
    "clean_project": {"clean_workers": "cleaner"},
    "cleaner": {"cleaner_techniques": ["drop_negatives", "scale"]},
}


def drop_negatives(item):
    return [x for x in item if x >= 0]

chrisjen.Technique.register("drop_negatives", drop_negatives)


def scale(item, factor=2):
    return [x * factor for x in item]

chrisjen.Technique.register("scale", scale)


project = chrisjen.Project(settings)
for batch in ([1, -1], [2, 3], [-5]):
    print(project.apply(batch))
# [2]
# [4, 6]
# []

print(chrisjen.Project(settings, item=[4, -4], automatic=True).result)
# [8]
```

## Look inside a run

Every workflow keeps the result of each of its nodes from the latest run, and a project keeps its workers' workflows:

```python
project = chrisjen.Project(settings, item=[1, -2, 3])
project.apply()
cleaner = project.workflow.retrieve("cleaner").contents
print(cleaner.results)
# {'cleaner': [2, 6]}
```

To stop between nodes and look at (or change) the item, use the `scrum` design. See the [advanced user guide](advanced.md).

## Log every node

To add behavior to a design, subclass it. This one records the name of every node before applying it. The new design is available as `logged` in settings:

```python
@dataclasses.dataclass
class Logged(chrisjen.Waterfall):
    log: list = dataclasses.field(default_factory=list)

    def execute(self, item, **kwargs):
        self.log.clear()
        for node in self.sequence:
            self.log.append(node.name)
            item = node.complete(item, **kwargs)
        return item


settings = {
    "logging_project": {"logging_workers": "worker"},
    "worker": {
        "design": "logged",
        "worker_steps": ["clean", "resize"],
        "clean_techniques": "drop_negatives",
        "resize_techniques": "scale",
    },
}
project = chrisjen.Project(settings, item=[1, -1])
print(project.apply())
# [2]
print(project.workflow.retrieve("worker").contents.log)
# ['clean', 'resize']
```

## Use a data frame

The item can be any object. This example uses `pandas` (which you need to install yourself) and saves the result with the project's clerk. It is not run by the unit tests because `pandas` is an optional dependency.

```python
# skip
import pathlib
import tempfile

import pandas as pd

import chrisjen


def fill_missing(item, value=0):
    return item.fillna(value)

chrisjen.Technique.register("fill_missing", fill_missing)


def standardize(item):
    return (item - item.mean()) / item.std()

chrisjen.Technique.register("standardize", standardize)


def summarize_columns(item):
    return item.describe().loc[["mean", "std"]]

chrisjen.Technique.register("summarize_columns", summarize_columns)


settings = {
    "analysis_project": {"analysis_workers": ["prepare", "report"]},
    "prepare": {
        "prepare_steps": ["clean", "scale"],
        "clean_techniques": "fill_missing",
        "scale_techniques": "standardize",
    },
    "report": {"report_techniques": "summarize_columns"},
    "fill_missing_parameters": {"value": 0},
}
data = pd.DataFrame({"a": [1.0, None, 3.0], "b": [4.0, 5.0, 6.0]})
project = chrisjen.Project(settings, item=data, root=pathlib.Path(tempfile.mkdtemp()))
result = project.apply()
print(result.round(2))
#         a    b
# mean  0.0  0.0
# std   1.0  1.0
project.clerk.save(result, file_name="summary.csv")
```

Because the file name ends in ".csv", the clerk uses its CSV format, which writes the file to the project's `output` folder.

## Keep techniques in their own module

Techniques and criteria are registered when the module that defines them is imported. Put them in a module, import it before you create a project, and refer to them by name in a settings file. Nothing else needs to be passed to `Project`.

```python
# skip
# techniques.py
import chrisjen


def clean(item):
    ...

chrisjen.Technique.register("clean", clean)


# main.py
import chrisjen

import techniques  # noqa: F401  (registers the techniques)

project = chrisjen.Project("settings.ini", item=my_data)
project.apply()
```
