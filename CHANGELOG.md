# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.2.0

* Rebuilt the core of `chrisjen` on `bobbie` (settings), `holden` (workflow graphs), `nagata` (file management), and `wonka` (factories). The previous modules depended on APIs that no longer exist and could not be imported.
* `Project` drafts an `Outline` from settings, publishes a `Workflow`, and applies it to an item.
* Added the workflow designs `waterfall`, `kanban`, `scrum`, `pert`, `agile`, `lean`, `contest`, and `survey`. Custom designs are subclasses of `Workflow`.
* Added `@chrisjen.technique` and `@chrisjen.criterion` to register functions, and `Technique`, `Step`, `Worker`, and `NullNode` nodes.
* Added Graphviz and mermaid exports.
* Rewrote the README and documentation, with examples that are run by the unit tests.
* Removed the `options` package, `Architect`, `Manager`, `Engineer`, and the other classes of the earlier design.
* Moved to the `snickerdoodle` template based on `uv` and `hatchling`.

## 0.1.4

    * Converted to `snickerdoodle` template and started change tracking
