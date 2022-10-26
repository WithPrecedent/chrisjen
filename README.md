[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Documentation Status](https://readthedocs.org/projects/chrisjen/badge/?version=latest)](http://chrisjen.readthedocs.io/?badge=latest)

<p align="center">
<img src="https://media.giphy.com/media/EUdtBgPPKP3F7U6yBh/giphy.gif" />
</p>
Named after the biggest badass in The Expanse, who knew how to get things done, chrisjen provides a solid foundation for designing internal project workflows with simple configuration files or scripting. chrisjen understands that you want to start designing your project and not spend countless hours designing the framework for your project. The primary goal of chrisjen is provide a simple, intuitive, powerful, extensible framework for constructing and implementing Python project workflows.

## Intuitive 

chrisjen locates all of the essential parts of a python workflow under one roof, using consistent naming conventions and structures. You start with an "idea" (typically in the form of a(n) ini, toml, json, or python file, but you can use a python dict as well) and the rest of the project is created for you. If you want to manually change, iterate, or otherwise advance through the stages of your project, that is done entirely through the Project class using intuitive attributes like "outline", "workflow", and "summary". All the file management is performed through the consistent interface of the filing "clerk".

<p align="center">
<img src="https://media.giphy.com/media/69qwCZtG4arIgMuL6b/giphy.gif" width="250" height="250"/>
</p>

chrisjen strives to get out of your way and has an easy learning curve. Importantly, unlike most other workflow packages, chrisjen does not require learning a new scripting language. Even the initial idea is created with a file or dictionary that is easy to read. For example, this is part of an .ini. configuration file for a data science project used in chrisjen's unit tests:

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
wisconsin_cancer_design = waterfall

[analyst]
design = contest
analyst_steps = scale, split, encode, sample, model
fill_techniques = none
categorize_techniques = none
scale_techniques = minmax, robust, normalize
split_techniques = stratified_kfold, train_test
encode_techniques = target, weight_of_evidence, one_hot, james_stein
mix_techniques = none
cleave_techniques = none
sample_techniques = none
reduce_techniques = none
model_techniques = xgboost, logit, random_forest
search_method = random
model_type = classify
label = target
default_package = sklearn

[critic]
design = waterfall
critic_steps = shap, sklearn
critic_techniques = explain, predict, report
data_to_review = test
join_predictions = True
```

You do not even half to select all of the options and specifications because chrisjen includes intellgent defaults. For example, if one of your project workers did not have a "design" setting, chrisjen would use the [waterfall design](https://www.lucidchart.com/blog/waterfall-project-management-methodology), the basic sequential design pattern in project management.

## Flexible
<p align="center">
<img src="https://media.giphy.com/media/GnepwAlt5FG3ASUvRB/giphy.gif"/>
</p>
chrisjen emphasizes letting users design their projects from a range of options. These choices can be provided in another package or added on the fly.

## Powerful 

To faciliate workflow construction, chrisjen comes with several common workflow designs. While straightforward, these workflows are otherwise tedious and sometimes difficult to implement. chrisjen does all of that work for you. chrisjen is particularly powerful for comparative and conditional projectrs where you want to identify the best strategy or average results among multiple iterations. Among the structures provided out-of-the-box are:
* Contest: evaluates and selects the best workflow among several based on one or more criteria
* Waterfall: the most basic workflow in project management which follows a pre-planned rigid workflow structure
* Kanban: a sequential workflow with isolated stages that produces deliverables for the following stage
* Scrum: flexible workflow structure that requires greater user control and intervention
* Pert: workflow that focuses on efficient use of parallel resources, including identifying the critical path
* Agile: a dynamic workflow structure that changes direction based on one or more criteria
* Lean: an iterative workflow that maximizes efficiency based on one or more criteria
* Survey: averages multiple workflows based on one or more criteria

## Extensible

chrisjen's framework supports a wide range of coding styles. You can create complex multiple inheritance structures with mixins galore or simpler, compositional objects. Even though the data structures are necessarily object-oriented, all of the tools to modify them are also available as functions, for those who prefer a more functional approaching to programming.

## Contributing 

The project is also highly documented so that users and developers and make chrisjen work with their projects. It is designed for Python coders at all levels. Beginners should be able to follow the readable code and internal documentation to understand how it works. More advanced users should find complex and tricky problems addressed through efficient code.
