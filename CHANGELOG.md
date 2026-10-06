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
  Names in settings are found in the library, and `Library.borrow` finds a
  class by name with fallbacks (for example, a worker's own class before the
  class of its design).
* `Project.create` loads settings into an `Idea` (a `bobbie.Settings` with
  properties for workers, steps, techniques, designs, criteria, and
  parameters), builds the workflow with `chrisjen.workshop`, applies it to an
  item, and generates a `Report` (`Summary` by default). Its arguments after
  the settings are keyword-only.
* Added the node types `Vertex`, `Technique`, `NullVertex`, `Step`, and
  `Worker`. A `Technique` has an `implement` method or wraps a tool: any
  callable, or the import path of one (imported only when it is used). Each
  node builds itself from the settings with `Vertex.build`, which passes
  settings that match its fields (such as `max_iterations`) to its
  constructor.
* Added the worker designs `Flow`, `Benchmark`, `Contest`, and `Survey`, and
  `Criteria` to score results. Workers are `holden.System` graphs, so they can
  be exported with `to_dot` and `to_mermaid`.
* Workflows are built the way they were in `simplify`: each technique of a
  step is wrapped in a `Step` node named "{technique}_{step}" (using a `Step`
  subclass named after the step, if there is one), and a `Contest` or
  `Survey` tries every combination of one technique from each step, with its
  own copies of the item and the nodes for each combination. Parameters can
  be set for a step (`{step}_parameters`) or for one technique in one step
  (`{technique}_{step}_parameters`).
* Rewrote the README and documentation, with examples that are run by the unit
  tests.
* Removed `Architect`, `Manager`, `Engineer`, and the other classes of the
  earlier design.
* Moved to the `snickerdoodle` template based on `uv` and `hatchling`, and
  maintained the Python dependencies with dependabot's `uv` ecosystem.

## 0.1.4

    * Converted to `snickerdoodle` template and started change tracking
