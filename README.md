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

Named after Earth's unflappable leader in *The Expanse*, who knew how to get things done, `chrisjen` provides an accessible, stable foundation for designing pure Python project workflows with straight-forward configuration files or simple scripting. The primary goal of `chrisjen` is to provide a lightweight, intuitive, powerful, extensible framework for constructing and implementing Python project workflows. `chrisjen` understands that you want to start building your project without spending countless hours designing the framework for your project. Indeed, I created `chrisjen` so that I could skip the preliminaries in my own Python projects. File management, configuration settings, and workflow design are already implemented in `chrisjen`'s easy-to-use system.

## Why use chrisjen?

### Intuitive

`chrisjen` puts all of the essential components for a Python project under one roof, using consistent naming conventions and structures. You start with an `Architect` (typically in the form of a(n) ini, toml, json, or Python file, but you can use a Python dict as well). Then, the rest of the project is automatically created for you. If you want to manually change, iterate, or otherwise advance through the stages of your project, that can easily be done entirely through the `Project` class using intuitive attributes like `outline`, `workflow`, and `summary`.

All of the nitty-gritty details of a project are handled through the consistent interface of the project `Manager`. The `manager` attribute of a `Project` instance directs all file management through its filing `clerk` and asset access and creation through its `librarian`. And, if you include all of the necessary information in your initial `Architect`, you do not have to concern yourself with even those simple interfaces.

`chrisjen` strives to get out of your way and has an easy, short learning curve. Unlike most other workflow packages, `chrisjen` does not require learning a new scripting language and it mayb e used entirely from the command line without knowing any Python. For example, this is part of an .ini configuration file for a data science project derived from one used in `chrisjen`'s unit tests:

```ini
[general]
seed = 43
conserve_memory = True
parallelize = False
gpu = False

[files]
source_format = csv
interim_format = csv
final_format = csv
analysis_format = csv
test_data = True
test_chunk = 500
export_results = True

[wisconsin_cancer_project]
wisconsin_cancer_workers = analyst, critic
wisconsin_cancer_design = kanban

[analyst]
design = contest
analyst_steps = scale, split, encode, sample, model
scale_techniques = minmax, robust, normalize
split_techniques = stratified_kfold, train_test
encode_techniques = target, weight_of_evidence, one_hot, james_stein
sample_techniques = none, smote
model_techniques = xgboost, logit, random_forest
model_type = classify
label = target
default_package = sklearn

[critic]
design = waterfall
critic_steps = shap, sklearn
critic_techniques = explain, predict, report
data_to_review = test
```

You do not even have to worry about selecting all of the available options and specifications because `chrisjen` includes intellgent defaults and sometimes infers selctions from other options selected. For example, if one of your project workers did not have a "design" setting, `chrisjen` would use the [waterfall design](https://www.lucidchart.com/blog/waterfall-project-management-methodology), the basic sequential design pattern used in project management.

### Powerful

<p align="center">
<img src="https://media.giphy.com/media/69qwCZtG4arIgMuL6b/giphy.gif" width="300" height="300"/>
</p>

To faciliate workflow construction, `chrisjen` comes with the most common and useful workflow structures. While straightforward, some of these workflows are otherwise tedious and can be difficult to implement. `chrisjen` does all of that work for you. `chrisjen` is particularly well-suited for comparative and conditional projects where you want to identify the best strategy or average results among multiple options. Among the workflow designs provided out-of-the-box are:
* `Waterfall`: the simplest workflow in project management which follows a pre-planned rigid structure
* `Kanban`: a sequential workflow with isolated stages that produces deliverables for the following stage to use
* `Scrum`: flexible workflow structure that requires greater user control and intervention
* `Contest`: evaluates and selects the best workflow among several based on one or more criteria
* `Pert`: workflow that focuses on efficient use of parallel resources, including identifying the critical path
* `Agile`: a dynamic workflow structure that changes direction based on one or more criteria
* `Lean`: an iterative workflow that maximizes efficiency based on one or more criteria
* `Survey`: averages multiple workflows based on one or more criteria


### Flexible

<p align="center">
<img src="https://media.giphy.com/media/GnepwAlt5FG3ASUvRB/giphy.gif" />
</p>

`chrisjen` emphasizes letting users design their projects from a range of options. These choices can be provided in another package or added on the fly. The entire package is designed to allow users to alter the structure and framework if a user so desires.

`chrisjen`'s framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more functional approaching to programming.

## Getting started

### Requirements

[TODO: List any OS or other restrictions and pre-installation dependencies]

### Installation

To install `chrisjen`, use `pip`:

```sh
pip install chrisjen
```

### Usage

<p align="center">
<img src="https://media.giphy.com/media/3ohzdDJq6UvTpJDegM/giphy.gif?cid=ecf05e47exxatrd0hj3ath92evolpmg8qlq1e30zygvv1sb7&ep=v1_gifs_search&rid=giphy.gif&ct=g" />
</p>

[TODO: Describe common use cases, with possible example(s)]

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

[TODO: Mention any people or organizations that warrant a special acknowledgment]

## License

Use of this repository is authorized under the [Apache Software License 2.0](https://www.github.com/WithPrecedent/chrisjen/blog/main/LICENSE).
