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

Named after Earth's unflappable leader in *The Expanse*, who knew how to get
things done, `chrisjen` builds and runs project workflows from a plain settings
file (or a Python `dict`). You list the parts of your project and the
techniques that each part uses. `chrisjen` connects them into a workflow,
applies it to your data, and, if you ask it to, compares alternatives and picks
the best.

```python
import dataclasses

import chrisjen


@dataclasses.dataclass
class DropNegatives(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return [x for x in item if x >= 0]


@dataclasses.dataclass
class Double(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return [x * 2 for x in item]


@dataclasses.dataclass
class Total(chrisjen.Technique):
    def implement(self, item, **kwargs):
        return sum(item)


settings = {
    "report_project": {"report_workers": "prepare, summarize"},
    "prepare": {"techniques": "drop_negatives, double"},
    "summarize": {"techniques": "total"},
}

project = chrisjen.Project.create(settings, item = [3, -1, 4, -1, 5])
print(project.result)
# 24
```

## Why use chrisjen?

### Intuitive

A `chrisjen` project is made of **techniques**, the actual actions, which are
grouped into **workers**, the parts of a project (for example, "prepare" and
"summarize"). A worker can also have **steps**, each with techniques of its
own.

You describe them in an ini, toml, json, yaml, xml, or Python file (or a
`dict`), and a `Project` does the rest. The same example as a file:

<!-- file: report.ini -->
```ini
[report_project]
report_workers = prepare, summarize

[prepare]
techniques = drop_negatives, double

[summarize]
techniques = total
```

```python
project = chrisjen.Project.create("report.ini", item = [3, -1, 4, -1, 5])
print(project.result)
# 24
```

`chrisjen` has no scripting language to learn. The settings file only names
things. What those things do is plain Python.

### Powerful

<p align="center">
<img src="https://media.giphy.com/media/69qwCZtG4arIgMuL6b/giphy.gif" width="300" height="300"/>
</p>

Each worker (and the project itself) has a `design` that decides how its parts
are applied:

| Design | What it does |
| --- | --- |
| `flow` | Applies its parts one after another. This is the default. |
| `benchmark` | Repeats its parts until a criterion is met. |
| `contest` | Tries every combination of alternatives and keeps the best result. |
| `survey` | Tries every combination of alternatives and averages the results. |

For example, to try three ways of scaling and keep whichever has the smallest
spread, make the project a `contest` and name a criterion:

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
    "compare_project": {
        "design": "contest",
        "criterion": "smallest_spread",
        "techniques": "double, halve, none",
    },
}
project = chrisjen.Project.create(settings, item = [1, 2, 3])
print(project.result)
# [0.5, 1.0, 1.5]
print(project.workflow.winner)
# halve
```

`none` is a built-in technique that does nothing, which is useful for testing
whether a technique helps at all.

### Flexible

<p align="center">
<img src="https://media.giphy.com/media/GnepwAlt5FG3ASUvRB/giphy.gif" />
</p>

`chrisjen` is built from small libraries that each do one job, and you can use
any of them on its own:

| Library | What `chrisjen` uses it for |
| --- | --- |
| [bobbie](https://github.com/WithPrecedent/bobbie) | Loading settings from files and `dict` types. |
| [holden](https://github.com/WithPrecedent/holden) | The graph data structure of a workflow, including exports to Graphviz and mermaid. |
| [nagata](https://github.com/WithPrecedent/nagata) | Loading and saving a project's files. |
| [camina](https://github.com/WithPrecedent/camina) | Small helpers, such as naming each run of a project. |

A technique is an object that wraps any callable (or the import path of one),
so a single interface can drive tools from many packages. Every class you
define (techniques, designs, criteria, and reports) is added to a `library`
under its snake case name as soon as it is defined, so it can be used in
settings right away.

## Getting started

### Requirements

`chrisjen` requires Python 3.11 or later. It runs on Linux, macOS, and Windows.
Its dependencies are installed automatically. If you want to load `yaml` or
`xml` settings or use `pandas` file formats, also install the optional
dependencies of those packages (for example, `pip install pyyaml xmltodict
pandas`).

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

A technique is a subclass of `chrisjen.Technique`. Either write an `implement`
method, or set `contents` to the tool that the technique wraps: a callable, or
its import path (which is only imported when the technique is used). The item
is passed to the tool along with any keyword parameters that the tool accepts.
Parameters come from a `{name}_parameters` section of your settings:

```python
@dataclasses.dataclass
class Mean(chrisjen.Technique):
    contents: str = "statistics.fmean"


@dataclasses.dataclass
class Rounded(chrisjen.Technique):
    contents: object = round


settings = {
    "average_project": {"techniques": "mean, rounded"},
    "rounded_parameters": {"ndigits": 1},
}
print(chrisjen.Project.create(settings, item = [1, 2, 4]).result)
# 2.3
```

#### Workers and steps

A worker lists its techniques or its steps, and each step lists its techniques.
In the default `flow` design, they are applied in order. In a `contest` or a
`survey`, the techniques of each step are alternatives, and every combination of
one technique from each step is tried:

```python
settings = {
    "numbers_project": {"numbers_workers": "prepare"},
    "prepare": {
        "steps": "clean, resize",
        "clean_techniques": "drop_negatives",
        "resize_techniques": "double, halve",
    },
}
project = chrisjen.Project.create(settings, item = [1, -2, 3])
print(project.result)
# [1.0, 3.0]
```

#### Running a project

`Project.create` reads the settings, builds the `workflow`, and (unless
`automatic = False`) applies it to `item`. The result is stored in `result`,
and a `report` summarizes the run. `apply` runs the project again, on a new
item if you pass one. Each run has an `id`, which is the name of the project
and the date and time unless you pass one:

```python
project = chrisjen.Project.create(
    "report.ini", id = "first_run", automatic = False)
print(project.apply([3, -1, 4]))
# 14
print(project.report.contents)
# project: report
# id: first_run
# paths: prepare > summarize
# result: 14
```

#### Files

Every project has a `clerk`, a `nagata.FileManager`. Pass the folder for the
project's files as `clerk` (or pass a `FileManager` of your own):

```python
import pathlib
import tempfile

root = pathlib.Path(tempfile.mkdtemp())
project = chrisjen.Project.create("report.ini", item = [1, 2], clerk = root)
project.clerk.save(project.result, file_name = "total", file_format = "pickle")
print(project.clerk.load(file_name = "total", file_format = "pickle"))
# 6
```

#### Export a workflow

`Project.to_dot` and `Project.to_mermaid` describe the workflow in
[Graphviz](https://graphviz.org/) or [mermaid](https://mermaid.js.org/) text.
Both are made by [holden](https://github.com/WithPrecedent/holden).

```python
print(project.to_mermaid())
# ---
# title: report
# ---
# flowchart LR
#     prepare(prepare) --> summarize(summarize)
```

There is more to `chrisjen`, including criteria, custom designs, building
workflows in code, and how the pieces fit together. See the
[documentation](https://WithPrecedent.github.io/chrisjen), especially the
[tutorial](https://WithPrecedent.github.io/chrisjen/tutorial/) and the [advanced
user guide](https://WithPrecedent.github.io/chrisjen/advanced/).

## Contributing

<p align="center">
<img src="https://media.giphy.com/media/romyCgNP7rvHEg8YDy/giphy.gif?cid=ecf05e47exxatrd0hj3ath92evolpmg8qlq1e30zygvv1sb7&ep=v1_gifs_search&rid=giphy.gif&ct=g" />
</p>

Contributors are always welcome. Feel free to grab an
[issue](https://www.github.com/WithPrecedent/chrisjen/issues) to work on or make
a suggested improvement. If you wish to contribute, please read the
[Contribution
Guide](https://www.github.com/WithPrecedent/chrisjen/contributing.md) and [Code
of Conduct](https://www.github.com/WithPrecedent/chrisjen/code_of_conduct.md).

## Similar Projects

<p align="center">
<img src="https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWc4bHg3cXI4MHRwZmxvczc3NWJmdGoxbjRwbXYybzJsdmphdGVjbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/lVnvuUxN6D7bkXPPFm/giphy.gif" />
</p>

* [airflow](https://github.com/apache/airflow): Apache's workflow tool that is
  likely the market leader. It requires substantial overhead and has a learning
  curve but offers the greatest extensibility for non-Python workflow components
  and support for continuous, always-on workflows.
* [jetstream](https://github.com/tgen/jetstream): similar DAG workflow
  structures in pure Python with a greater emphasis on loading workflows from
  disk.
* [luigi](https://github.com/spotify/luigi): Spotify's workflow tool with much
  greater overhead and support for controlling workflow nodes outside of Python.
* [pathos](https://github.com/uqfoundation/pathos): supports parallel workflow
  construction with heterogenuous computing framework. Among other features, it
  includes drop-in replacements for Python's `pickle` and `multiprocess`, called
  `dill` and `multiprocessing`, respectively.

## License

Use of this repository is authorized under the [Apache Software License
2.0](https://www.github.com/WithPrecedent/chrisjen/blob/main/LICENSE).
