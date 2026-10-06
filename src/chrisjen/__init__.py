"""Dynamically creates and implements workflows"""

from __future__ import annotations

__version__ = '0.2.0'

__author__: str = 'Corey Rayburn Yung'

__all__: list[str] = [
    'Benchmark',
    'Comparator',
    'Contest',
    'Criteria',
    'Flow',
    'Genre',
    'Idea',
    'Library',
    'NullVertex',
    'Project',
    'Report',
    'Step',
    'Summary',
    'Survey',
    'Technique',
    'Vertex',
    'Worker',
    'library',
]

from .base import Criteria, Genre, Idea, Library, Report, Vertex, library
from .interface import Project
from .nodes import NullVertex, Step, Technique, Worker
from .reports import Summary
from .workers import Benchmark, Comparator, Contest, Flow, Survey
