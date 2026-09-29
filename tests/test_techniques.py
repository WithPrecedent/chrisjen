"""Tests technique types, registries, and wrapping of other tools."""

from __future__ import annotations

import abc
import dataclasses
import statistics
import threading
from typing import Any

import pytest

import chrisjen


class TtCleaner(chrisjen.Technique, abc.ABC):
    """Techniques that clean data."""


class TtMunger(chrisjen.Technique, abc.ABC):
    """Techniques that reshape data."""


class TtAnalyzer(chrisjen.Technique, abc.ABC):
    """Techniques that summarize data."""


@dataclasses.dataclass
class TtDropNegatives(TtCleaner):
    def implement(self, item: Any, **kwargs: Any) -> Any:
        return [x for x in item if x >= 0]


class TtBase(TtCleaner, abc.ABC):
    """An abstract subclass of a type is not a new type."""


@dataclasses.dataclass
class TtGeneral(chrisjen.Technique):
    def implement(self, item: Any, **kwargs: Any) -> Any:
        return "general"


@dataclasses.dataclass
class TtDistribution(chrisjen.Technique, abc.ABC):
    """Builds a distribution from parameters and calls a method on it."""

    method: str = "cdf"

    def implement(self, item: Any, **kwargs: Any) -> Any:
        tool = self.resolve()
        distribution = tool(**kwargs)
        return getattr(distribution, self.method)(item)


def clean(item: list[int]) -> list[int]:
    return [x for x in item if x is not None]


TtCleaner.register("tt_clean", clean)
TtCleaner.register("tt_shared", clean)
TtMunger.register("tt_shared", lambda item: item)
TtAnalyzer.register("tt_mean", "statistics.fmean")
chrisjen.Technique.register("tt_length", len)


""" Types and registries """


def test_types_are_direct_abstract_subclasses() -> None:
    types = chrisjen.Technique.types
    assert types["technique"] is chrisjen.Technique
    assert types["tt_cleaner"] is TtCleaner
    assert types["tt_munger"] is TtMunger
    assert types["tt_analyzer"] is TtAnalyzer
    assert "tt_base" not in types
    assert "tt_drop_negatives" not in types
    assert "tt_general" not in types
    assert "null_node" not in types


def test_each_type_has_its_own_registry() -> None:
    registries = [
        chrisjen.Technique.registry,
        TtCleaner.registry,
        TtMunger.registry,
        TtAnalyzer.registry,
    ]
    assert len({id(registry) for registry in registries}) == len(registries)
    assert "tt_mean" in TtAnalyzer.registry
    assert "tt_mean" not in TtCleaner.registry
    assert "tt_mean" not in chrisjen.Technique.registry
    assert "tt_length" in chrisjen.Technique.registry
    assert "tt_length" not in TtCleaner.registry


def test_subclasses_register_their_class_in_their_type() -> None:
    assert TtCleaner.registry["tt_drop_negatives"] is TtDropNegatives
    assert TtCleaner.registry["tt_base"] is TtBase
    assert "tt_drop_negatives" not in TtMunger.registry
    assert "tt_drop_negatives" not in chrisjen.Technique.registry
    assert chrisjen.Technique.registry["tt_general"] is TtGeneral
    # A subclass of a subclass shares the registry of the type.
    assert TtDropNegatives.registry is TtCleaner.registry


def test_the_null_node_is_registered_under_several_names() -> None:
    for name in ("none", "null", "null_node"):
        assert chrisjen.Technique.registry[name] is chrisjen.NullNode
    assert chrisjen.NullNode.registry is chrisjen.Technique.registry


def test_available() -> None:
    available = chrisjen.Technique.available()
    assert available["tt_analyzer"] == ["tt_mean"]
    assert available["tt_cleaner"] == sorted(TtCleaner.registry)
    assert available["technique"] == sorted(chrisjen.Technique.registry)
    assert available["tt_munger"] == sorted(TtMunger.registry)
    assert "tt_shared" in available["tt_munger"]
    assert all(names for names in available.values())


""" Registering """


def test_register_with_a_name_and_tool() -> None:
    technique = TtMunger.register("tt_registered", len, {"a": 1})
    assert isinstance(technique, TtMunger)
    assert technique.name == "tt_registered"
    assert technique.contents is len
    assert technique.parameters == {"a": 1}
    assert TtMunger.registry["tt_registered"] is technique


def test_register_a_technique() -> None:
    technique = TtCleaner(name="tt_instance", contents=len)
    assert TtCleaner.register(technique) is technique
    assert TtCleaner.registry["tt_instance"] is technique
    assert TtCleaner.register(technique, name="tt_alias") is technique
    assert TtCleaner.registry["tt_alias"] is technique


def test_register_a_subclass_instance() -> None:
    technique = TtDropNegatives(name="tt_special")
    assert TtCleaner.register(technique) is technique
    assert TtCleaner.create("tt_special").complete([1, -1]) == [1]


def test_register_rejects_the_wrong_kind_of_item() -> None:
    with pytest.raises(TypeError, match="TtCleaner instance, not int"):
        TtCleaner.register(3)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="not TtMunger"):
        TtCleaner.register(TtMunger(name="tt_wrong"))
    assert "tt_wrong" not in TtCleaner.registry


def test_register_replaces_a_technique_with_the_same_name() -> None:
    TtMunger.register("tt_replaced", lambda item: "first")
    TtMunger.register("tt_replaced", lambda item: "second")
    assert TtMunger.create("tt_replaced").complete(0) == "second"


def test_register_in_the_general_registry() -> None:
    technique = chrisjen.Technique.register("tt_general_function", abs)
    assert chrisjen.Technique.registry["tt_general_function"] is technique
    assert chrisjen.Technique.create("tt_general_function").complete(-3) == 3


""" Creating and finding """


def test_create_returns_a_separate_copy() -> None:
    prototype = TtMunger.register("tt_copy", len, {"a": 1})
    created = TtMunger.create("tt_copy")
    assert created is not prototype
    assert created == prototype
    created.parameters["b"] = 2
    assert prototype.parameters == {"a": 1}
    assert TtMunger.create("tt_copy") is not created


def test_create_applies_parameters() -> None:
    TtMunger.register("tt_defaults", len, {"a": 1, "b": 2})
    created = TtMunger.create(
        "tt_defaults", {"name": "renamed", "parameters": {"b": 3, "c": 4}}
    )
    assert created.name == "renamed"
    assert created.parameters == {"a": 1, "b": 3, "c": 4}
    assert created.contents is len
    replaced = TtMunger.create("tt_defaults", {"contents": abs})
    assert replaced.contents is abs
    assert replaced.parameters == {"a": 1, "b": 2}


def test_created_techniques_are_named_for_the_name_asked_for() -> None:
    assert chrisjen.Technique.create("tt_length").name == "tt_length"
    assert chrisjen.Technique.create("none").name == "none"
    assert chrisjen.Technique.create("null").name == "null"
    assert TtCleaner.create("tt_drop_negatives").name == "tt_drop_negatives"


def test_create_from_a_registered_class() -> None:
    created = TtCleaner.create("tt_drop_negatives", {"parameters": {"a": 1}})
    assert isinstance(created, TtDropNegatives)
    assert created.parameters == {"a": 1}
    assert created.complete([1, -1, 2]) == [1, 2]


def test_names_are_found_in_every_type() -> None:
    assert isinstance(chrisjen.Technique.create("tt_mean"), TtAnalyzer)
    assert isinstance(chrisjen.Technique.create("tt_drop_negatives"), TtCleaner)
    assert isinstance(chrisjen.Technique.create("tt_general"), TtGeneral)
    assert chrisjen.Technique.create("tt_mean").complete([1, 2, 3]) == 2


def test_a_type_only_looks_in_its_own_registry() -> None:
    assert isinstance(TtCleaner.create("tt_clean"), TtCleaner)
    with pytest.raises(KeyError, match="'tt_mean' is not a known technique"):
        TtCleaner.create("tt_mean")
    with pytest.raises(KeyError, match="'tt_clean'"):
        TtAnalyzer.create("tt_clean")
    # A subclass of a type uses the registry of its type.
    assert isinstance(TtDropNegatives.create("tt_clean"), TtCleaner)


def test_locate() -> None:
    assert chrisjen.Technique.locate("tt_mean") == (TtAnalyzer, "tt_mean")
    assert chrisjen.Technique.locate("tt_analyzer.tt_mean") == (
        TtAnalyzer,
        "tt_mean",
    )
    assert chrisjen.Technique.locate("tt_mean", kind="TT_ANALYZER") == (
        TtAnalyzer,
        "tt_mean",
    )
    assert TtCleaner.locate("tt_clean") == (TtCleaner, "tt_clean")


def test_ambiguous_names() -> None:
    with pytest.raises(KeyError, match="tt_cleaner, tt_munger"):
        chrisjen.Technique.create("tt_shared")
    with pytest.raises(KeyError, match="more than one type"):
        chrisjen.Technique.locate("tt_shared")
    assert isinstance(
        chrisjen.Technique.create("tt_cleaner.tt_shared"), TtCleaner
    )
    assert isinstance(
        chrisjen.Technique.create("tt_shared", kind="tt_munger"), TtMunger
    )
    assert isinstance(
        chrisjen.Technique.create("tt_shared", kind=TtCleaner), TtCleaner
    )
    assert isinstance(TtMunger.create("tt_shared"), TtMunger)


def test_kind_takes_a_name_or_a_class() -> None:
    for kind in ("tt_analyzer", "TT_Analyzer", TtAnalyzer):
        assert isinstance(
            chrisjen.Technique.create("tt_mean", kind=kind), TtAnalyzer
        )
    with pytest.raises(KeyError, match="not a type of technique.*tt_cleaner"):
        chrisjen.Technique.create("tt_mean", kind="nonsense")
    with pytest.raises(KeyError, match="'tt_mean' is not a known technique"):
        chrisjen.Technique.create("tt_mean", kind="tt_cleaner")


def test_qualified_names() -> None:
    assert isinstance(
        chrisjen.Technique.create("tt_analyzer.tt_mean"), TtAnalyzer
    )
    assert chrisjen.Technique.create("tt_analyzer.tt_mean").name == "tt_mean"
    with pytest.raises(KeyError, match="not a known technique"):
        chrisjen.Technique.create("tt_analyzer.tt_missing")
    # A name with a dot that does not start with a type is looked up as is.
    with pytest.raises(KeyError, match="not a known technique"):
        chrisjen.Technique.create("nothing.tt_mean")


def test_unknown_technique_error_lists_the_known_ones() -> None:
    with pytest.raises(KeyError) as error:
        chrisjen.Technique.create("tt_nothing")
    message = str(error.value)
    assert "not a known technique" in message
    assert "Technique.register" in message
    assert "tt_analyzer: tt_mean" in message
    assert "technique:" in message


def test_produce() -> None:
    technique = TtMunger(name="a", parameters={"x": 1})
    result = TtMunger.produce(technique, {"parameters": {"y": 2}, "name": "b"})
    assert result is technique
    assert technique.name == "b"
    assert technique.parameters == {"x": 1, "y": 2}
    assert TtMunger.produce(technique, None) is technique
    made = TtMunger.produce(TtDropNegatives, {"name": "c"})
    assert isinstance(made, TtDropNegatives)
    assert made.name == "c"


""" Wrapping other tools """


def test_wrap_a_callable() -> None:
    technique = chrisjen.Technique("length", contents=len)
    assert technique.complete([1, 2, 3]) == 3


def test_wrap_an_import_path() -> None:
    technique = chrisjen.Technique("mean", contents="statistics.fmean")
    assert technique.resolve() is statistics.fmean
    assert technique.complete([1, 2, 3, 4]) == 2.5
    colon = chrisjen.Technique("mean", contents="statistics:fmean")
    assert colon.complete([2, 4]) == 3.0
    method = chrisjen.Technique("upper", contents="builtins.str.upper")
    assert method.complete("abc") == "ABC"


def test_import_paths_are_not_imported_until_they_are_used() -> None:
    technique = TtMunger.register("tt_lazy", "tt_no_such_package.tool")
    assert technique.contents == "tt_no_such_package.tool"
    with pytest.raises(ImportError, match="tt_no_such_package.tool"):
        technique.complete(1)
    with pytest.raises(ImportError, match="no_attribute"):
        chrisjen.Technique("x", contents="statistics.no_attribute").complete(1)


def test_parameters_are_filtered_for_the_wrapped_tool() -> None:
    technique = chrisjen.Technique(
        "round", contents=round, parameters={"ndigits": 1, "unused": True}
    )
    assert technique.complete(3.14159) == 3.1
    assert chrisjen.Technique("round", contents=round).complete(3.6) == 4
    assert technique.complete(3.14159, ndigits=3, other=1) == 3.142


def test_wrapped_tools_that_are_not_callable_or_missing() -> None:
    with pytest.raises(TypeError, match="technique 'constant' wraps 5, which"):
        chrisjen.Technique("constant", contents=5).complete(1)
    with pytest.raises(TypeError, match="technique 'path' wraps 3.14"):
        chrisjen.Technique("path", contents="math.pi").complete(1)
    with pytest.raises(NotImplementedError, match="no tool"):
        chrisjen.Technique("empty").complete(1)


def test_a_type_can_change_how_tools_are_called() -> None:
    distribution = TtDistribution(
        name="normal",
        contents="statistics.NormalDist",
        parameters={"mu": 10, "sigma": 2},
    )
    assert distribution.complete(10) == 0.5
    assert distribution.complete(10, mu=0, sigma=1) == pytest.approx(
        1.0, abs=1e-6
    )
    cdf = TtDistribution(
        name="pdf",
        contents=statistics.NormalDist,
        method="pdf",
        parameters={"mu": 0, "sigma": 1},
    )
    assert cdf.complete(0) == pytest.approx(0.3989422804)
    TtDistribution.register(distribution)
    assert TtDistribution.create("normal").complete(10) == 0.5


def test_copies_share_a_tool_that_cannot_be_copied() -> None:
    class Guarded:
        def __init__(self) -> None:
            self.lock = threading.Lock()

        def __call__(self, item: Any) -> Any:
            return item + 1

    tool = Guarded()
    TtMunger.register("tt_guarded", tool)
    created = TtMunger.create("tt_guarded", {"parameters": {"a": 1}})
    assert created.contents is tool
    assert created.complete(1) == 2
    assert created.parameters == {"a": 1}
    assert TtMunger.registry["tt_guarded"].parameters == {}


def test_copies_do_not_share_a_tool_with_state() -> None:
    class Counter:
        def __init__(self) -> None:
            self.count = 0

        def __call__(self, item: Any) -> Any:
            self.count += 1
            return self.count

    TtMunger.register("tt_counter", Counter())
    first = TtMunger.create("tt_counter")
    second = TtMunger.create("tt_counter")
    assert first.complete(0) == 1
    assert first.complete(0) == 2
    assert second.complete(0) == 1
    assert TtMunger.registry["tt_counter"].contents.count == 0


def test_the_same_technique_in_two_steps_is_independent() -> None:
    class Counter:
        def __init__(self) -> None:
            self.count = 0

        def __call__(self, item: Any) -> Any:
            self.count += 1
            return item + [self.count]

    TtMunger.register("tt_stateful", Counter())
    settings = {
        "x_project": {"x_workers": "w"},
        "w": {
            "w_steps": ["one", "two"],
            "one_techniques": "tt_stateful",
            "two_techniques": "tt_stateful",
        },
    }
    assert chrisjen.Project(settings, item=[]).apply() == [1, 1]


""" In projects """


def project_settings(**worker: Any) -> dict[str, Any]:
    return {"x_project": {"x_workers": ["w"]}, "w": worker}


def test_projects_find_techniques_in_any_type() -> None:
    settings = project_settings(
        w_steps=["clean", "summarize"],
        clean_techniques="tt_drop_negatives",
        summarize_techniques="tt_mean",
    )
    project = chrisjen.Project(settings, item=[4, -1, 2])
    assert project.apply() == 3
    assert project.outline.types == {}
    steps = project.workflow.retrieve("w").contents
    assert isinstance(steps.retrieve("clean").contents[0], TtCleaner)
    assert isinstance(steps.retrieve("summarize").contents[0], TtAnalyzer)


def test_projects_can_name_the_type_of_each_step() -> None:
    settings = project_settings(
        w_steps=["clean", "munge"],
        clean_techniques="tt_shared",
        clean_technique_type="TT_Cleaner",
        munge_techniques="tt_shared",
        munge_technique_type="tt_munger",
    )
    project = chrisjen.Project(settings, item=[1])
    assert project.outline.types == {
        "w": {"clean": "tt_cleaner", "munge": "tt_munger"}
    }
    project.publish()
    steps = project.workflow.retrieve("w").contents
    assert isinstance(steps.retrieve("clean").contents[0], TtCleaner)
    assert isinstance(steps.retrieve("munge").contents[0], TtMunger)
    assert project.apply() == [1]


def test_ambiguous_names_need_a_type_in_a_project() -> None:
    settings = project_settings(w_techniques="tt_shared")
    project = chrisjen.Project(settings, item=[1])
    with pytest.raises(KeyError, match="more than one type"):
        project.publish()
    settings = project_settings(
        w_techniques="tt_shared", w_technique_type="tt_munger"
    )
    assert chrisjen.Project(settings, item=[1]).apply() == [1]
    assert chrisjen.Project(settings, item=[1]).outline.types == {
        "w": {"w": "tt_munger"}
    }


def test_projects_accept_qualified_names() -> None:
    settings = project_settings(w_techniques="tt_munger.tt_shared, tt_length")
    project = chrisjen.Project(settings, item=[1, 2])
    assert project.apply() == 2
    step = project.workflow.retrieve("w").contents.retrieve("w")
    assert [t.name for t in step.contents] == [
        "tt_munger.tt_shared",
        "tt_length",
    ]


def test_a_technique_type_restricts_the_lookup() -> None:
    settings = project_settings(
        w_techniques="tt_mean", w_technique_type="tt_cleaner"
    )
    with pytest.raises(KeyError, match="'tt_mean' is not a known technique"):
        chrisjen.Project(settings).publish()
    settings = project_settings(
        w_techniques="tt_mean", w_technique_type="nonsense"
    )
    with pytest.raises(KeyError, match="not a type of technique"):
        chrisjen.Project(settings).publish()


def test_technique_type_settings_are_not_kept_as_initialization() -> None:
    settings = project_settings(
        w_techniques="tt_mean",
        w_technique_type="tt_analyzer",
        model_type="classify",
    )
    outline = chrisjen.Project(settings).outline
    assert outline.initialization["w"] == {"model_type": "classify"}


def test_parameters_reach_typed_techniques() -> None:
    TtDistribution.register(
        "tt_normal", "statistics.NormalDist", {"mu": 0, "sigma": 1}
    )
    settings = project_settings(
        w_techniques="tt_normal", w_technique_type="tt_distribution"
    )
    settings["tt_normal_parameters"] = {"mu": 5, "sigma": 5}
    assert chrisjen.Project(settings, item=5).apply() == 0.5
    # The registered defaults are used if the settings have nothing.
    del settings["tt_normal_parameters"]
    assert chrisjen.Project(settings, item=0).apply() == 0.5


def test_project_techniques_do_not_change_the_registry() -> None:
    TtMunger.register("tt_registry_check", len, {"a": 1})
    settings = project_settings(w_techniques="tt_registry_check")
    settings["tt_registry_check_parameters"] = {"b": 2}
    chrisjen.Project(settings, item=[1]).apply()
    assert TtMunger.registry["tt_registry_check"].parameters == {"a": 1}
    assert TtMunger.registry["tt_registry_check"].name == "tt_registry_check"


def test_only_the_tool_may_be_shared_when_it_cannot_be_copied() -> None:
    # Parameters must be copyable, because sharing them would let one use of a
    # technique change another.
    TtMunger.register("tt_bad_parameters", len, {"lock": threading.Lock()})
    with pytest.raises(TypeError, match="pickle"):
        TtMunger.create("tt_bad_parameters")


def test_a_redundant_type_in_a_name_is_accepted_with_kind() -> None:
    created = chrisjen.Technique.create(
        "tt_cleaner.tt_clean", kind="tt_cleaner"
    )
    assert isinstance(created, TtCleaner)
    assert created.name == "tt_clean"
    assert chrisjen.Technique.locate(
        "tt_analyzer.tt_mean", kind=TtAnalyzer
    ) == (TtAnalyzer, "tt_mean")
