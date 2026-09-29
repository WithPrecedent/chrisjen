"""Branching workflow designs

Contents:
    Compare (workers.Research): uses a Research workflow with parallel branches that
        applies crtieria to reduce the number of branches.
    Observe (workers.Research): uses a Research workflow with parallel branches but
        has no reduction or criteria.
    Agile (Compare): a dynamic workflow structure that changes direction based
        on one or more criteria.
    Contest (Compare): evaluates and selects best workflow among several based
        on one or more criteria.
    Lean (Compare): an iterative workflow that maximizes efficiency based on
        one or more criteria.
    Survey (Compare): averages multiple workflows based on one or more
        criteria.

To Do:


"""
from __future__ import annotations

import collections
import dataclasses
from collections.abc import Hashable, MutableMapping
from collections.abc import Set as AbstractSet
from typing import Any

import camina
import holden

from .. import base, nodes
from . import tasks, workflows


@dataclasses.dataclass
class Compare(workflows.Research):
    """Workflow that branches and appplies criteria to eliminate branches.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[structure.Project]): related Project instance.

    """
    name: str | None = None
    contents: MutableMapping[Hashable, AbstractSet[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: base.Project | None = None
    superviser: tasks.Contractor | None = None


@dataclasses.dataclass
class Observe(workflows.Research):
    """Workflow that branches but does not reduce.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[structure.Project]): related Project instance.

    """
    name: str | None = None
    contents: MutableMapping[Hashable, AbstractSet[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: base.Project | None = None
    superviser: tasks.Contractor | None = None

    """ Public Methods """

    def implement(self, item: Any, **kwargs: base.Kwargs) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied,
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.

        """
        results = super().implement(item = item, **kwargs)
        return self.judge.complete(projects = results)


@dataclasses.dataclass
class Compete(Compare):
    """Base class for tests that returns fewer paths from more.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[structure.Project]): related Project instance.

    """
    name: str | None = None
    contents: MutableMapping[Hashable, AbstractSet[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: base.Project | None = None
    superviser: tasks.Contractor | None = None
    judge: tasks.Judge | None = None

    """ Properties """

    @property
    def graph(self) -> holden.System:
        """Returns direct graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.

        """
        graph = super().graph
        endpoints = camina.iterify(graph.endpoint)
        scorer = 'scorer'
        graph.add(scorer)
        for endpoint in endpoints:
            graph.connect((endpoint, scorer))
        return graph

    """ Public Methods """

    def implement(self, item: Any, **kwargs: base.Kwargs) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied,
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.

        """
        results = super().implement(item = item, **kwargs)
        return self.judge.complete(projects = results)


@dataclasses.dataclass
class Lean(Compare):
    """Iterative workflow that maximizes efficiency based on criteria.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[structure.Project]): related Project instance.

    """
    name: str | None = None
    contents: MutableMapping[Hashable, AbstractSet[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: base.Project | None = None
    superviser: tasks.Contractor | None = None
    judge: tasks.Judge | None = None


@dataclasses.dataclass
class Survey(Compare):
    """Base class for research that averages results among several paths.

    Args:
        name (Optional[str]): designates the name of a class instance that is
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to
            'contents' when the 'implement' method is called. Defaults to an
            empty Parameters instance.
        project (Optional[structure.Project]): related Project instance.

    """
    name: str | None = None
    contents: MutableMapping[Hashable, AbstractSet[Hashable]] = (
        dataclasses.field(
            default_factory = lambda: collections.defaultdict(set)))
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = nodes.Parameters)
    project: base.Project | None = None
    superviser: tasks.Contractor | None = None
    judge: tasks.Judge | None = None


    """ Properties """

    @property
    def graph(self) -> holden.System:
        """Returns direct graph of the project workflow.

        Returns:
            holden.System: direct graph of the project workflow.

        """
        graph = super().graph
        endpoints = camina.iterify(graph.endpoint)
        averager = 'averager'
        graph.add(averager)
        for endpoint in endpoints:
            graph.connect((endpoint, averager))
        return graph
