# Changelog

All notable changes to this project will be documented in this file.

<!-- insertion marker -->

## Unreleased

* Added a `conserve_memory` option to `Contest` and `Survey` (and any design
  that mixes in `Comparator`), so that a worker with many paths does not keep
  every path's result in memory until the end. A contest scores each result as
  soon as its path is applied and keeps only the best so far (`results` then
  has only the winner), and a survey adds each result to a running total and
  keeps none. Added `Comparator.each_path`, which applies the paths one at a
  time without keeping their results; `Comparator._observe`, which a design
  can override to keep a summary of each result before it is dropped; and
  `Contest.scores`, the score of each path.
* Settings in the "general" section that are listed in
  `options._GENERAL_SETTINGS` (for now only `conserve_memory`) now reach every
  node with a field of the same name, unless the node's own section sets it.
* Added numbered names for techniques and steps. A name that ends in a number
  (such as "logit2", or "logit_2") and is not the name of a class itself is
  built with the class named without the number ("logit"), with its own
  settings and parameters (such as "logit2_parameters"). So one technique can
  be tried with several sets of parameters, as in
  "model_techniques = logit1, logit2, logit3".
* Updated to the `snickerdoodle` 0.5.0 template
* Added support for Python 3.15
* Ran the tests on Linux, macOS, and Windows (the `ci` Action only ran them on
  Linux) and uploaded their coverage to Codecov
* Ran the `pre-commit` hooks once instead of in every test job, ran the `ci`
  Action only on pushes to `main` and pull requests, and only deployed the
  documentation from `main`
* Replaced the deprecated release Action with the GitHub CLI, which uses the
  released version's entry in CHANGELOG.md as the release notes, and only made
  releases from `main` after the tests and linters pass
* Added a coverage report page to the documentation and a coverage badge to
  the README
* Read the version from `__version__` in `__init__.py` instead of repeating it
  in `pyproject.toml`, and used an SPDX license expression (PEP 639)
* Made `dependabot` update the `uv` dependencies and GitHub Actions weekly
* Renamed the misnamed `,python-version` file to `.python-version` and stopped
  ignoring it
* Added environment setup instructions to the contributing guide and fixed
  broken links in the README

## 0.3.0

* Renamed the method that every node writes from `implement` to `apply`. A
  subclass of `Vertex` now writes `apply`, which is wrapped when the subclass
  is defined, so that a call to it still adds the node's `parameters` to the
  keyword arguments (as `apply` did when it called `implement`). A call to
  the `apply` of a parent class through `super()` is not wrapped again, so it
  gets its keyword arguments exactly as they are passed. Subclasses can
  override `_call_apply` to change what happens around every `apply`. This
  is a breaking change: a subclass that wrote `implement` must rename it to
  `apply`.

## 0.2.1

* Updated to the `snickerdoodle` 0.4.0 template
* Made `ruff` prefer single quotes
* Made `ruff` ignore boolean default positional arguments (`FBT002`)
* Excluded `uv.lock` from the large file check
* Fixed typos in the contributing guide and noted that the project does not use a code formatter

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
