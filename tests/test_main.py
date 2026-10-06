"""Tests the package as a whole."""

from __future__ import annotations

import ast
import pathlib
import sys
import tomllib

import chrisjen

ROOT = pathlib.Path(__file__).parent.parent


def test_version_matches_the_package_settings_and_changelog() -> None:
    with (ROOT / 'pyproject.toml').open('rb') as file:
        project = tomllib.load(file)['project']
    assert project['version'] == chrisjen.__version__
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding = 'utf-8')
    assert f'## {chrisjen.__version__}\n' in changelog


def test_imported_packages_are_declared() -> None:
    with (ROOT / 'pyproject.toml').open('rb') as file:
        dependencies = tomllib.load(file)['project']['dependencies']
    declared = {d.split('>')[0].split('=')[0].strip() for d in dependencies}
    imported = set()
    for path in (ROOT / 'src' / 'chrisjen').glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding = 'utf-8'))):
            if isinstance(node, ast.Import):
                imported.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                imported.add(node.module.split('.')[0])
    third_party = imported - set(sys.stdlib_module_names) - {'chrisjen'}
    assert third_party <= declared


def test_public_names_exist() -> None:
    for name in chrisjen.__all__:
        assert hasattr(chrisjen, name), name
    assert len(set(chrisjen.__all__)) == len(chrisjen.__all__)


def test_all_designs_are_available_by_name() -> None:
    for name in ('flow', 'benchmark', 'contest', 'survey'):
        design = chrisjen.library.all[name]
        assert design.__name__.lower() == name
