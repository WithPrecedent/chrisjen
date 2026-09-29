# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.2.0

* Rebuilt the core of `chrisjen` on `bobbie` (settings), `holden` (workflow graphs), `nagata` (file management), and `wonka` (factories). The previous modules depended on APIs that no longer exist and could not be imported.
* `Project` drafts an `Outline` from settings, publishes a `Workflow`, and applies it to an item.
* Added the workflow designs `waterfall`, `kanban`, `scrum`, `pert`, `agile`, `lean`, `contest`, and `survey`. Custom designs are subclasses of `Workflow`.
* Added `Technique`, `Step`, `Worker`, and `NullNode` nodes, and `@chrisjen.criterion` to register functions that score results.
* A `Technique` is an object that wraps a tool: any callable, or the import path of one (imported only when it is used). `Technique.register` registers techniques by name, and a technique can have default parameters.
* Each type of technique has its own registry (a `wonka` `Registrar`). A type is a subclass of `Technique` and `abc.ABC`, and it can override `implement` to change how its tools are called. This is the foundation for packages that define types such as cleaners, mungers, analyzers, and visualizers. Steps can name the type of their techniques with `{step}_technique_type`, and names can be written as `type.name`. `Technique.available()` and `Technique.types` list what is registered.
* Added Graphviz and mermaid exports.
* Rewrote the README and documentation, with examples that are run by the unit tests.
* Removed the `options` package, `Architect`, `Manager`, `Engineer`, and the other classes of the earlier design.
* Moved to the `snickerdoodle` template based on `uv` and `hatchling`.

## 0.1.4

    * Converted to `snickerdoodle` template and started change tracking
