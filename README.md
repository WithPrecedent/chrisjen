[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![PyPI Latest Release](https://img.shields.io/pypi/v/chrisjen.svg)](https://pypi.org/project/chrisjen/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/chrisjen/badge/?version=latest)](http://chrisjen.readthedocs.io/?badge=latest)


<p align="center">
<img src="https://media.giphy.com/media/EUdtBgPPKP3F7U6yBh/giphy.gif" height="300"/>
</p>

# Why chrisjen?
Named after the biggest badass in *The Expanse*, who knew how to get things done, **chrisjen** provides an accessible, stable foundation for designing pure Python project workflows with straight-forward configuration files or simple scripting. The primary goal of **chrisjen** is to provide a lightweight, intuitive, powerful, extensible framework for constructing and implementing Python project workflows. **chrisjen** understands that you want to start designing your project without spending countless hours designing the framework for your project. Indeed, I created **chrisjen** so that I could skip the preliminaries in my own Python projects. File management, configuration settings, and workflow design are already implemented in **chrisjen**'s easy-to-use system.

## Intuitive 
**chrisjen** puts all of the essential components for a Python project under one roof, using consistent naming conventions and structures. You start with an `Idea` (typically in the form of a(n) ini, toml, json, or Python file, but you can use a Python dict as well). Then, the rest of the project is automatically created for you. If you want to manually change, iterate, or otherwise advance through the stages of your project, that can easily be done entirely through the `Project` class using intuitive attributes like `outline`, `workflow`, and `summary`. 

All of the nitty-gritty details of a project are handled through the consistent interface of the project `Manager`. The `manager` attribute of a `Project` instance directs all file management through its filing `clerk` and asset access and creation through its `librarian`. And, if you include all of the necessary information in your initial `Idea`, you do not have to concern yourself with even those simple interfaces.

**chrisjen** strives to get out of your way and has an easy, short learning curve. Unlike most other workflow packages, **chrisjen** does not require learning a new scripting language and it mayb e used entirely from the command line without knowing any Python. For example, this is part of an .ini configuration file for a data science project derived from one used in **chrisjen**'s unit tests:

```
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

You do not even have to worry about selecting all of the available options and specifications because **chrisjen** includes intellgent defaults and sometimes infers selctions from other options selected. For example, if one of your project workers did not have a "design" setting, **chrisjen** would use the [waterfall design](https://www.lucidchart.com/blog/waterfall-project-management-methodology), the basic sequential design pattern used in project management.

## Powerful 
<p align="center">
<img src="https://media.giphy.com/media/69qwCZtG4arIgMuL6b/giphy.gif" width="300" height="300"/>
</p>

To faciliate workflow construction, **chrisjen** comes with the most common and useful workflow structures. While straightforward, some of these workflows are otherwise tedious and can be difficult to implement. **chrisjen** does all of that work for you. **chrisjen** is particularly well-suited for comparative and conditional projects where you want to identify the best strategy or average results among multiple options. Among the workflow designs provided out-of-the-box are:
* `Waterfall`: the simplest workflow in project management which follows a pre-planned rigid structure
* `Kanban`: a sequential workflow with isolated stages that produces deliverables for the following stage to use
* `Scrum`: flexible workflow structure that requires greater user control and intervention
* `Contest`: evaluates and selects the best workflow among several based on one or more criteria
* `Pert`: workflow that focuses on efficient use of parallel resources, including identifying the critical path
* `Agile`: a dynamic workflow structure that changes direction based on one or more criteria
* `Lean`: an iterative workflow that maximizes efficiency based on one or more criteria
* `Survey`: averages multiple workflows based on one or more criteria
  
## Flexible
<p align="center">
<img src="https://media.giphy.com/media/GnepwAlt5FG3ASUvRB/giphy.gif" />
</p>

**chrisjen** emphasizes letting users design their projects from a range of options. These choices can be provided in another package or added on the fly. The entire package is designed to allow users to alter the structure and framework if a user so desires. 

**chrisjen**'s framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more functional approaching to programming.

# Contributing 
The project is highly documented so that users and developers can make **chrisjen** work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.

# Similar Projects
* [airflow](https://github.com/apache/airflow): Apache's workflow tool that is likely the market leader. It requires substantial overhead and has a learning curve but offers the greatest extensibility for non-Python workflow components and support for continuous, always-on workflows.
* [jetstream](https://github.com/tgen/jetstream): similar DAG workflow structures in pure Python with a greater emphasis on loading workflows from disk.
* [luigi](https://github.com/spotify/luigi): Spotify's workflow tool with much greater overhead and support for controlling workflow nodes outside of Python.
* [pathos](https://github.com/uqfoundation/pathos): supports parallel workflow construction with heterogenuous computing framework. Among other features, it includes drop-in replacements for Python's `pickle` and `multiprocess`, called `dill` and `multiprocessing`, respectively.