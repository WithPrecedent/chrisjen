# chrisjen

| | |
| --- | --- |
| Version | [![PyPI Latest Release](https://img.shields.io/pypi/v/chrisjen.svg?style=flat-square&color=steelblue&label=PyPI&logo=PyPI&logoColor=yellow)](https://pypi.org/project/chrisjen/) [![GitHub Latest Release](https://img.shields.io/github/v/tag/WithPrecedent/chrisjen?style=flat-square&color=navy&label=GitHub&logo=github)](https://github.com/WithPrecedent/chrisjen/releases)
| Status | [![Build Status](https://img.shields.io/github/actions/workflow/status/WithPrecedent/chrisjen/ci.yml?branch=main&style=flat-square&color=cadetblue&label=Tests&logo=pytest)](https://github.com/WithPrecedent/chrisjen/actions/workflows/ci.yml?query=branch%3Amain) [![Development Status](https://img.shields.io/badge/Development-Active-seagreen?style=flat-square&logo=git)](https://www.repostatus.org/#active) [![Project Stability](https://img.shields.io/pypi/status/chrisjen?style=flat-square&logo=pypi&label=Stability&logoColor=yellow)](https://pypi.org/project/chrisjen/)
| Documentation | [![Hosted By](https://img.shields.io/badge/Hosted_by-Github_Pages-blue?style=flat-square&color=navy&logo=github)](https://WithPrecedent.github.io/chrisjen)
| Tools | [![Documentation](https://img.shields.io/badge/MkDocs-magenta?style=flat-square&color=deepskyblue&logo=markdown&labelColor=gray)](https://squidfunk.github.io/mkdocs-material/) [![Linter](https://img.shields.io/endpoint?style=flat-square&url=https://raw.githubusercontent.com/charliermarsh/Ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/Ruff) [![Dependency Manager](https://img.shields.io/badge/uv-mediumpurple?style=flat-square&logo=uv&labelColor=gray)](https://docs.astral.sh/uv/) [![Pre-commit](https://img.shields.io/badge/pre--commit-darkolivegreen?style=flat-square&logo=pre-commit&logoColor=white&labelColor=gray)](https://github.com/TezRomacH/python-package-template/blob/master/.pre-commit-config.yaml) [![CI](https://img.shields.io/badge/GitHub_Actions-navy?style=flat-square&logo=githubactions&labelColor=gray&logoColor=white)](https://github.com/features/actions) [![Editor Settings](https://img.shields.io/badge/Editor_Config-paleturquoise?style=flat-square&logo=editorconfig&labelColor=gray)](https://editorconfig.org/) [![Repository Template](https://img.shields.io/badge/snickerdoodle-bisque?style=flat-square&logo=cookiecutter&labelColor=gray)](https://www.github.com/WithPrecedent/chrisjen) [![Dependency Maintainer](https://img.shields.io/badge/dependabot-navy?style=flat-square&logo=dependabot&logoColor=white&labelColor=gray)](https://github.com/dependabot)
| Compatibility | [![Compatible Python Versions](https://img.shields.io/pypi/pyversions/chrisjen?style=flat-square&color=steelblue&label=Python&logo=python&logoColor=yellow)](https://pypi.python.org/pypi/chrisjen/) [![Linux](https://img.shields.io/badge/Linux-lightseagreen?style=flat-square&logo=linux&labelColor=gray&logoColor=white)](https://www.linux.org/) [![MacOS](https://img.shields.io/badge/MacOS-snow?style=flat-square&logo=apple&labelColor=gray)](https://www.apple.com/macos/) [![Windows](https://img.shields.io/badge/Windows-blue?style=flat-square&logo=Windows&labelColor=gray&color=orangered)](https://www.microsoft.com/en-us/windows?r=1)
| Stats | [![PyPI Download Rate (per month)](https://img.shields.io/pypi/dm/chrisjen?style=flat-square&color=steelblue&label=Downloads%20💾&logo=pypi&logoColor=yellow)](https://pypi.org/project/chrisjen) [![GitHub Stars](https://img.shields.io/github/stars/WithPrecedent/chrisjen?style=flat-square&color=navy&label=Stars%20⭐&logo=github)](https://github.com/WithPrecedent/chrisjen/stargazers) [![GitHub Contributors](https://img.shields.io/github/contributors/WithPrecedent/chrisjen?style=flat-square&color=navy&label=Contributors%20🙋&logo=github)](https://github.com/WithPrecedent/chrisjen/graphs/contributors) [![GitHub Issues](https://img.shields.io/github/issues/WithPrecedent/chrisjen?style=flat-square&color=navy&label=Issues%20📘&logo=github)](https://github.com/WithPrecedent/chrisjen/graphs/contributors) [![GitHub Forks](https://img.shields.io/github/forks/WithPrecedent/chrisjen?style=flat-square&color=navy&label=Forks%20🍴&logo=github)](https://github.com/WithPrecedent/chrisjen/forks)
| | |



## What is chrisjen?

<p align="center">
<img src="https://media.giphy.com/media/EUdtBgPPKP3F7U6yBh/giphy.gif" height="300"/>
</p>

Named after Earth's unflappable leader in *The Expanse*, who knew how to get things done, `chrisjen` builds and runs project workflows from a plain settings file (or a Python `dict`). You list the steps of your project and the techniques for each step. `chrisjen` connects them into a workflow, applies it to your data, and, if you ask it to, compares alternatives and picks the best.

```python
import chrisjen


@chrisjen.technique
def drop_negatives(item):
    return [x for x in item if x >= 0]


@chrisjen.technique
def double(item):
    return [x * 2 for x in item]


@chrisjen.technique
def total(item):
    return sum(item)


settings = {
    "report_project": {"report_workers": ["prepare", "summarize"]},
    "prepare": {
        "prepare_steps": ["clean", "scale"],
        "clean_techniques": "drop_negatives",
        "scale_techniques": "double",
    },
    "summarize": {"summarize_techniques": "total"},
}

project = chrisjen.Project(settings, item=[3, -1, 4, -1, 5])
print(project.apply())
# 24
```

## Why use chrisjen?

### Intuitive

A `chrisjen` project has three parts, which are named the same way in every project:

* **Workers** are the big parts of a project (for example, "prepare" and "summarize").
* **Steps** are the stages of a worker (for example, "clean" and "scale").
* **Techniques** are the actual actions in a step. They are ordinary Python functions.

You describe them in an ini, toml, json, yaml, xml, or Python file (or a `dict`), and a `Project` does the rest. The same example as a file:

<!-- file: report.ini -->
```ini
[report_project]
report_workers = prepare, summarize

[prepare]
prepare_steps = clean, scale
clean_techniques = drop_negatives
scale_techniques = double

[summarize]
summarize_techniques = total
```

```python
project = chrisjen.Project("report.ini", item=[3, -1, 4, -1, 5])
print(project.outline.summary)
# report (waterfall)
#   prepare (waterfall)
#     clean: drop_negatives
#     scale: double
#   summarize (waterfall)
#     total
print(project.apply())
# 24
```

`chrisjen` has no scripting language to learn. The settings file only names things. What those things do is plain Python.

### Powerful

<p align="center">
<img src="https://media.giphy.com/media/69qwCZtG4arIgMuL6b/giphy.gif" width="300" height="300"/>
</p>

Each worker (and the project itself) has a `design` that decides how its parts are put together. The default is the sequential `waterfall`. The other designs are especially useful for projects where you want to find the best strategy, or average across several:

| Design | What it does |
| --- | --- |
| `waterfall` | Applies nodes one after another. This is the default. |
| `kanban` | Like `waterfall`, but each stage works on an isolated copy and leaves a deliverable. |
| `scrum` | Like `waterfall`, but you advance one node at a time and can step in between. |
| `pert` | Nodes can depend on more than one other node, and the critical path is calculated. |
| `agile` | Repeats the sequence until a criterion is met. |
| `lean` | Repeats the sequence for as long as the result keeps improving. |
| `contest` | Tries every combination of the techniques and keeps the best result. |
| `survey` | Tries every combination of the techniques and averages the results. |

For example, to try three ways of scaling and keep whichever has the smallest spread, list the techniques and change the design to `contest`:

```python
@chrisjen.technique
def halve(item):
    return [x / 2 for x in item]


@chrisjen.criterion
def smallest_spread(item):
    return -(max(item) - min(item))


settings = {
    "compare_project": {"compare_workers": "scaler"},
    "scaler": {
        "design": "contest",
        "criteria": "smallest_spread",
        "scaler_steps": ["scale"],
        "scale_techniques": ["double", "halve", "none"],
    },
}
project = chrisjen.Project(settings, item=[1, 2, 3])
print(project.apply())
# [0.5, 1.0, 1.5]
contest = project.workflow.retrieve("scaler").contents
print(contest.winner)
# halve
print(contest.scores)
# {'double': -4, 'halve': -1.0, 'none': -2}
```

### Flexible

<p align="center">
<img src="https://media.giphy.com/media/GnepwAlt5FG3ASUvRB/giphy.gif" />
</p>

`chrisjen` is built from small libraries that each do one job, and you can use any of them on its own:

| Library | What `chrisjen` uses it for |
| --- | --- |
| [bobbie](https://github.com/WithPrecedent/bobbie) | Loading settings from files and `dict` types. |
| [holden](https://github.com/WithPrecedent/holden) | The graph data structure of a workflow, including exports to Graphviz and mermaid. |
| [nagata](https://github.com/WithPrecedent/nagata) | Loading and saving a project's files. |
| [wonka](https://github.com/WithPrecedent/wonka) | Creating techniques and workflow designs from their names. |

Techniques can be functions or classes, and you can add your own workflow designs. Everything is found by name, so a new technique or design is available in settings files as soon as it is defined.

## Getting started

### Requirements

`chrisjen` requires Python 3.11 or later. It runs on Linux, macOS, and Windows. Its dependencies (`bobbie`, `holden`, `nagata`, and `wonka`) are installed automatically. If you want to load `yaml` or `xml` settings or use `pandas` file formats, also install the optional dependencies of those packages (for example, `pip install pyyaml xmltodict pandas`).

### Installation

To install `chrisjen`, use `pip`:

```sh
pip install chrisjen
```

### Usage

<p align="center">
<img src="https://media.giphy.com/media/3ohzdDJq6UvTpJDegM/giphy.gif?cid=ecf05e47exxatrd0hj3ath92evolpmg8qlq1e30zygvv1sb7&ep=v1_gifs_search&rid=giphy.gif&ct=g" />
</p>

#### Techniques

A technique is a function that takes the item being worked on and returns the changed item. Register it with `@chrisjen.technique` and refer to it by name. A function can also take keyword parameters, which are filled from a `<name>_parameters` section of your settings:

```python
@chrisjen.technique
def keep_above(item, minimum=0):
    return [x for x in item if x > minimum]


settings = {
    "filter_project": {"filter_workers": "filterer"},
    "filterer": {"filterer_techniques": "keep_above"},
    "keep_above_parameters": {"minimum": 2},
}
print(chrisjen.Project(settings, item=[1, 2, 3, 4]).apply())
# [3, 4]
```

For techniques that need more than a function, subclass `chrisjen.Technique` and write an `implement` method. The subclass is found by its snake case name (`RunningTotal` is "running_total").

```python
import dataclasses
import itertools


@dataclasses.dataclass
class RunningTotal(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return list(itertools.accumulate(item))


settings = {
    "accumulate_project": {"accumulate_workers": "accumulator"},
    "accumulator": {"accumulator_techniques": "running_total"},
}
print(chrisjen.Project(settings, item=[1, 2, 3]).apply())
# [1, 3, 6]
```

#### The three stages of a project

A project moves through three stages. Creating a `Project` *drafts* it (turns the settings into an `outline`). `publish` builds the `workflow`, and `apply` runs it. Set `automatic=True` to do all three when the project is created.

```python
project = chrisjen.Project("report.ini", item=[3, -1, 4, -1, 5])
project.publish()
print(project.workflow.walk())
# [['prepare', 'summarize']]
print(project.apply())
# 24
print(project.result)
# 24
```

You can pass a different item (and keyword parameters for your techniques) to `apply`, so one project can be run on many inputs:

```python
print(project.apply([1, 2, 3]))
# 12
```

#### Files

Every project has a `clerk`, a `nagata.FileManager` with `input`, `interim`, and `output` folders. They are created in a folder named for the project's `identification` (its name plus the date and time) inside `root`, which is "data" by default. Any settings in a "files" section, such as `file_encoding`, are applied to the clerk.

```python
import pathlib
import tempfile

root = pathlib.Path(tempfile.mkdtemp())
project = chrisjen.Project("report.ini", item=[1, 2], root=root)
project.clerk.save(project.apply(), file_name="total", file_format="pickle")
print(project.clerk.load(file_name="total", file_format="pickle", folder="output"))
# 6
```

#### Export a workflow

`Project.to_dot` and `Project.to_mermaid` describe a workflow in [Graphviz](https://graphviz.org/) or [mermaid](https://mermaid.js.org/) text. In the dot export, each worker is drawn as a cluster of its steps.

```python
print(project.to_mermaid())
# ---
# title: report
# ---
# flowchart LR
#     prepare(prepare) --> summarize(summarize)
```

There is much more to `chrisjen`, including all eight designs, custom designs, parameters, and how the pieces fit together. See the [documentation](https://WithPrecedent.github.io/chrisjen), especially the [tutorial](https://WithPrecedent.github.io/chrisjen/tutorial/) and the [advanced user guide](https://WithPrecedent.github.io/chrisjen/advanced/).

## Contributing

<p align="center">
<img src="https://media.giphy.com/media/romyCgNP7rvHEg8YDy/giphy.gif?cid=ecf05e47exxatrd0hj3ath92evolpmg8qlq1e30zygvv1sb7&ep=v1_gifs_search&rid=giphy.gif&ct=g" />
</p>

Contributors are always welcome. Feel free to grab an [issue](https://www.github.com/WithPrecedent/chrisjen/issues) to work on or make a suggested improvement. If you wish to contribute, please read the [Contribution Guide](https://www.github.com/WithPrecedent/chrisjen/contributing.md) and [Code of Conduct](https://www.github.com/WithPrecedent/chrisjen/code_of_conduct.md).

## Similar Projects

<p align="center">
<img src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWc4bHg3cXI4MHRwZmxvczc3NWJmdGoxbjRwbXYybzJsdmphdGVjbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lVnvuUxN6D7bkXPPFm/giphy.gif" />
</p>

* [airflow](https://github.com/apache/airflow): Apache's workflow tool that is likely the market leader. It requires substantial overhead and has a learning curve but offers the greatest extensibility for non-Python workflow components and support for continuous, always-on workflows.
* [jetstream](https://github.com/tgen/jetstream): similar DAG workflow structures in pure Python with a greater emphasis on loading workflows from disk.
* [luigi](https://github.com/spotify/luigi): Spotify's workflow tool with much greater overhead and support for controlling workflow nodes outside of Python.
* [pathos](https://github.com/uqfoundation/pathos): supports parallel workflow construction with heterogenuous computing framework. Among other features, it includes drop-in replacements for Python's `pickle` and `multiprocess`, called `dill` and `multiprocessing`, respectively.

## Acknowledgments

`chrisjen` is built on the author's other packages, [bobbie](https://github.com/WithPrecedent/bobbie), [holden](https://github.com/WithPrecedent/holden), [nagata](https://github.com/WithPrecedent/nagata), and [wonka](https://github.com/WithPrecedent/wonka).

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/chrisjen/blob/main/LICENSE).
