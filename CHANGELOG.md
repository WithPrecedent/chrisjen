# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## 0.2.0

* Rebuilt the core of `chrisjen` on `bobbie` (settings), `holden` (workflow
  graphs), `nagata` (file management), and `camina` (helpers). The previous
  modules depended on APIs that no longer exist and could not be imported.
* Added `Library` and `Genre`. Every subclass of `Genre` is added to
  `chrisjen.library` when it is defined, under its snake case name. Abstract
  subclasses (those that list `abc.ABC` among their bases) form nested genres.
  Names in settings are found in the library.
* `Project.create` loads settings into an `Idea` (a `bobbie.Settings` with
  properties for workers, steps, techniques, designs, criteria, and
  parameters), builds the workflow with `chrisjen.workshop`, applies it to an
  item, and generates a `Report` (`Summary` by default).
* Added the node types `Vertex`, `Technique`, `NullVertex`, `Step`, and
  `Worker`. A `Technique` has an `implement` method or wraps a tool: any
  callable, or the import path of one (imported only when it is used).
* Added the worker designs `Flow`, `Benchmark`, `Contest`, and `Survey`, and
  `Criteria` to score results. Workers are `holden.System` graphs, so they can
  be exported with `to_dot` and `to_mermaid`.
* Rewrote the README and documentation, with examples that are run by the unit
  tests.
* Removed `Architect`, `Manager`, `Engineer`, and the other classes of the
  earlier design.
* Moved to the `snickerdoodle` template based on `uv` and `hatchling`.

## 0.1.4

    * Converted to `snickerdoodle` template and started change tracking
