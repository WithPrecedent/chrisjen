# Recipes

Short, complete examples for common jobs. Except where noted, they are run by
the `chrisjen` unit tests. See the [tutorial](tutorial.md) for the basics and
the [advanced user guide](advanced.md) for details.

## Pick the best of several methods

A forecast can be made in different ways. A `contest` runs each way on the same
data and keeps the one with the best score. The item here is a `dict`, and each
technique adds a "prediction" to it. The criterion returns the negative error,
so that the smallest error has the highest score.

```python
import dataclasses
import statistics

import chrisjen


@dataclasses.dataclass
class LastValue(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return {**item, "prediction": item["values"][-1]}


@dataclasses.dataclass
class Average(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return {**item, "prediction": statistics.fmean(item["values"])}


@dataclasses.dataclass
class RecentAverage(chrisjen.Technique):
    def implement(self, item, window = 3, **kwargs):
        recent = item["values"][-window:]
        return {**item, "prediction": statistics.fmean(recent)}


@dataclasses.dataclass
class ForecastError(chrisjen.Criteria):
    def score(self, item):
        return -abs(item["prediction"] - item["truth"])


settings = {
    "forecast_project": {
        "design": "contest",
        "criterion": "forecast_error",
        "techniques": "last_value, average, recent_average",
    },
}
data = {"values": [10, 12, 11, 13, 14, 15], "truth": 16}
project = chrisjen.Project.create(settings, item = data)
print(project.workflow.winner, project.result["prediction"])
# last_value 15
```

## Try several values of a parameter

Parameters belong to names, so to compare parameter values, give each value a
name with a small subclass:

```python
@dataclasses.dataclass
class Window2(RecentAverage):
    parameters: dict = dataclasses.field(
        default_factory = lambda: {"window": 2})


@dataclasses.dataclass
class Window5(RecentAverage):
    parameters: dict = dataclasses.field(
        default_factory = lambda: {"window": 5})


settings["forecast_project"]["techniques"] = "window2, window5"
project = chrisjen.Project.create(settings, item = data)
scores = {
    name: project.workflow.criteria.score(result)
    for name, result in project.workflow.results.items()}
print(project.workflow.winner, scores)
# window2 {'window2': -1.5, 'window5': -3.0}
```

A `{name}_parameters` section in the settings is added to these defaults (and
replaces any with the same name).

## Average several approaches

`survey` runs every alternative and averages the results, instead of choosing
one:

```python
@dataclasses.dataclass
class EstimateLow(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return sum(item) * 0.9


@dataclasses.dataclass
class EstimateHigh(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return sum(item) * 1.1


settings = {
    "estimate_project": {
        "design": "survey",
        "techniques": "estimate_low, estimate_high",
    },
}
print(round(chrisjen.Project.create(settings, item = [10, 20, 30]).result, 6))
# 60.0
```

## Repeat until the result is good enough

`benchmark` repeats its sequence until its criteria's test passes:

```python
@dataclasses.dataclass
class HalveStep(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return item / 2


@dataclasses.dataclass
class SmallEnough(chrisjen.Criteria):
    def score(self, item):
        return item < 0.01


settings = {
    "shrink_project": {
        "design": "benchmark",
        "criterion": "small_enough",
        "techniques": "halve_step",
    },
}
project = chrisjen.Project.create(settings, item = 1.0)
print(project.result, project.workflow.iterations)
# 0.0078125 7
```

## Run one project on many inputs

A project's workflow is built once. `apply` can be called again with new items:

```python
@dataclasses.dataclass
class DropNegatives(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return [x for x in item if x >= 0]


@dataclasses.dataclass
class Scale(chrisjen.Technique):
    def implement(self, item, factor = 2, **kwargs):
        return [x * factor for x in item]


settings = {"clean_project": {"techniques": "drop_negatives, scale"}}
project = chrisjen.Project.create(settings, automatic = False)
for batch in ([1, -1], [2, 3], [-5]):
    print(project.apply(batch))
# [2]
# [4, 6]
# []
```

## Log every node

To add behavior to a design, subclass it. This one records the name of every
node before applying it. The new design is available as `logged` in settings:

```python
@dataclasses.dataclass
class Logged(chrisjen.Flow):
    log: list = dataclasses.field(default_factory = list)

    def implement(self, item, **kwargs):
        self.log.clear()
        for path in self.walk():
            for node in path:
                self.log.append(node.name)
                item = node.apply(item, **kwargs)
        return item


settings = {
    "logging_project": {
        "design": "logged",
        "techniques": "drop_negatives, scale",
    },
}
project = chrisjen.Project.create(settings, item = [1, -1])
print(project.result, project.workflow.log)
# [2] ['drop_negatives', 'scale']
```

## Use a data frame

The item can be any object. This example uses `pandas` (which you need to
install yourself) and saves the result with the project's clerk. It is not run
by the unit tests because `pandas` is an optional dependency.

```python
# skip
import dataclasses
import pathlib
import tempfile

import pandas as pd

import chrisjen


@dataclasses.dataclass
class FillMissing(chrisjen.Technique):
    def implement(self, item, value = 0, **kwargs):
        return item.fillna(value)


@dataclasses.dataclass
class Standardize(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return (item - item.mean()) / item.std()


@dataclasses.dataclass
class SummarizeColumns(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return item.describe().loc[["mean", "std"]]


settings = {
    "analysis_project": {"analysis_workers": "prepare, report"},
    "prepare": {"techniques": "fill_missing, standardize"},
    "report": {"techniques": "summarize_columns"},
    "fill_missing_parameters": {"value": 0},
}
data = pd.DataFrame({"a": [1.0, None, 3.0], "b": [4.0, 5.0, 6.0]})
project = chrisjen.Project.create(
    settings, item = data, clerk = pathlib.Path(tempfile.mkdtemp()))
print(project.result.round(2))
#         a    b
# mean  0.0  0.0
# std   1.0  1.0
project.clerk.save(project.result, file_name = "summary.csv")
```

Because the file name ends in ".csv", the clerk uses its CSV format.

## Keep techniques in their own module

Techniques, designs, and criteria are added to the library when the module that
defines them is imported. Put them in a module, import it before you create a
project, and refer to them by name in a settings file. Nothing else needs to be
passed to `Project.create`.

```python
# skip
# techniques.py
import dataclasses

import chrisjen


@dataclasses.dataclass
class Clean(chrisjen.Technique):
    def implement(self, item, **kwargs):
        ...


# main.py
import chrisjen

import techniques  # noqa: F401  (adds the techniques to the library)

project = chrisjen.Project.create("settings.ini", item = my_data)
```
