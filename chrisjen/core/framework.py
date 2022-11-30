"""
framework: essential classes for a chrisjen project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
License: Apache-2.0

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contents:
    Rules
    Keystones
    Keystone
    Project

To Do:

            
"""
from __future__ import annotations
import abc
from collections.abc import Hashable
import contextlib
import dataclasses
import inspect
import pathlib
from typing import Any, ClassVar, Optional, Type
import warnings

import ashford
import camina
import bobbie
import miller


@dataclasses.dataclass
class Rules(abc.ABC):
    """Default values and rules for building a chrisjen project.
    
    Every attribute in Rules should be a class attribute so that it is 
    accessible without instancing it (which it cannot be).

    Args:
        parsers (ClassVar[dict[str, tuple[str]]]): keys are the names of
            special categories of settings and values are tuples of suffixes or
            whole words that are associated with those special categories in
            user settings.
        default_settings (ClassVar[dict[Hashable, dict[Hashable, Any]]]):
            default settings for a chrisjen project's idea. 
        default_manager (ClassVar[str]): key name of the default manager.
            Defaults to 'publisher'.
        default_librarian (ClassVar[str]): key name of the default librarian.
            Defaults to 'as_needed'.
        default_task (ClassVar[str]): key name of the default task design.
            Defaults to 'technique'.
        default_workflow (ClassVar[str]): key name of the default worker design.
            Defaults to 'waterfall'.
        null_node_names (ClassVar[list[Any]]): lists of key names that indicate 
            a null node should be used. Defaults to ['none', 'None', None].   
        
    """
    parsers: ClassVar[dict[str, tuple[str, ...]]] = {
        'criteria': ('criteria',),
        'design': ('design', 'structure'),
        'manager': ('manager', 'project'),
        'files': ('filer', 'files', 'clerk'),
        'general': ('general',),
        'librarian': ('efficiency', 'librarian'),
        'parameters': ('parameters',), 
        'workers': ('workers',)}
    default_settings: ClassVar[dict[Hashable, dict[Hashable, Any]]] = {
        'general': {
            'verbose': False,
            'parallelize': False,
            'efficiency': 'up_front'},
        'files': {
            'file_encoding': 'windows-1252',
            'threads': -1}}
    default_manager: ClassVar[str] = 'publisher'
    default_librarian: ClassVar[str] = 'up_front'
    default_superviser: ClassVar[str] = 'copier'
    default_task: ClassVar[str] = 'technique'
    default_workflow: ClassVar[str] = 'waterfall'
    null_node_names: ClassVar[list[Any]] = ['none', 'None', None]

         
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        idea (Optional[Keystone]): configuration settings for the project. 
            Defaults to None.
        clerk (Optional[Keystone]): a filing clerk for loading and saving files 
            throughout a chrisjen project. Defaults to None.
        manager (Optional[Keystone]): constructor for a chrisjen project. 
            Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None. 
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
            
    Attributes:
        rules (ClassVar[Rules]): a class storing the default project options. 
            Defaults to Rules.
        library (ClassVar[Keystones]): library of nodes for executing a
            chrisjen project. Defaults to an instance of ProjectLibrary.
 
    """
    name: Optional[str] = None
    idea: Optional[bobbie.Settings] = None 
    manager: Optional[Keystone] = dataclasses.field(
        default = None, repr = False, compare = False)
    identification: Optional[str] = dataclasses.field(
        default = None, compare = False)
    automatic: Optional[bool] = dataclasses.field(
        default = True, compare = False)
    rules: ClassVar[Rules] = Rules
    library: ClassVar[ashford.Keystones] = ashford.Keystones
        
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self = Keystones.validate(item = self, attribute = 'manager')
       
    """ Public Class Methods """

    @classmethod
    def create(
        cls, 
        idea: pathlib.Path | str | bobbie.Settings,
        **kwargs) -> Project:
        """Returns a Project instance based on 'idea' and kwargs.

        Args:
            idea (pathlib.Path | str | bobbie.Settings): a path to a file 
                containing configuration settings, a python dict, or a Settings 
                instance.

        Returns:
            Project: an instance based on 'idea' and kwargs.
            
        """        
        return cls(idea = idea, **kwargs)   
        
    """ Dunder Methods """
    
    def __getattr__(self, item: str) -> Any:
        """Checks 'manager' for attribute named 'item'.

        Args:
            item (str): name of attribute to check.

        Returns:
            Any: contents of manager attribute named 'item'.
            
        """
        try:
            return getattr(self.manager, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project or its manager')
