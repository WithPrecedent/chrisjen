"""
base: base classes for a chrisjen project
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


To Do:

            
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import contextlib
import dataclasses
from email.policy import default
import inspect
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union
import warnings

import amos
import bobbie
import holden
import miller

from . import foundry


@dataclasses.dataclass
class ProjectKeystone(abc.ABC):
    """Mixin for required project base classes.
    
    Args:
        keystones (ClassVar[amos.Catalog]):
    
    """
    keystones: ClassVar[amos.Catalog] = amos.Catalog()

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because ProjectKeystone will be used as a mixin, it is important to 
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if ProjectKeystone in cls.__bases__:
            key = amos.namify(item = cls)
            # Removes 'project_' prefix if it exists.
            if key.startswith('project_'):
                key = key[8:]
            ProjectKeystone.keystones[key] = cls

        
@dataclasses.dataclass  # type: ignore
class ProjectLibrary(amos.Library):
    """Stores classes instances and classes in a chained mapping.
    
    When searching for matches, instances are prioritized over classes.
    
    Args:
        classes (amos.Catalog): a catalog of stored classes. Defaults to any 
            empty Catalog.
        instances (amos.Catalog): a catalog of stored class instances. Defaults 
            to an empty Catalog.
                 
    """
    classes: amos.Catalog[str, Type[ProjectKeystone]] = dataclasses.field(
        default_factory = amos.Catalog)
    instances: amos.Catalog[str, ProjectKeystone] = dataclasses.field(
        default_factory = amos.Catalog)
    kinds: MutableMapping[str, Type[ProjectKeystone]] = dataclasses.field(
        default_factory = dict)

    """ Properties """
    
    @property
    def plurals(self) -> tuple[str]:
        """Returns all stored subclass names as naive plurals of those names.
        
        Returns:
            tuple[str]: all names with an 's' added in order to create simple 
                plurals combined with the stored keys.
                
        """
        suffixes = []
        for catalog in ['classes', 'instances']:
            plurals = [k + 's' for k in getattr(self, catalog).keys()]
            suffixes.extend(plurals)
        return tuple(suffixes)
  
    """ Public Methods """
    
    def add_kind(self, item: Type[ProjectKeystone]) -> None:
        """Adds 'item' to 'kinds' dict.
        
        Args:
            item (Type[ProjectKeystone]
        """
        key = amos.namify(item = item)
        if key.startswith('project_'):
            key = key[8:]
        self.kinds[key] = item
        return
   
      
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[ProjectKeystone]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[ProjectKeystone]): a filing clerk for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        director (Optional[ProjectKeystone]): constructor for a chrisjen 
            project. Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None.   
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
        library (ClassVar[ProjectLibrary]): library of nodes for executing a
            chrisjen project. 
    
    """
    name: Optional[str] = None
    settings: Optional[bobbie.Settings] = None
    clerk: Optional[ProjectKeystone] = None
    director: Optional[ProjectKeystone] = None
    identification: Optional[str] = None
    automatic: Optional[bool] = True
    library: ClassVar[ProjectLibrary] = ProjectLibrary()
        
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self._validate_director()
       
    """ Public Class Methods """

    @classmethod
    def create(
        cls, 
        settings: Union[pathlib.Path, str, bobbie.Settings],
        **kwargs) -> Project:
        """Returns a Project instance based on 'settings' and kwargs.

        Args:
            settings (Union[pathlib.Path, str, bobbie.Settings]): a path to a 
                file containing configuration settings or a Settings instance.

        Returns:
            Project: an instance based on 'settings' and kwargs.
            
        """        
        return cls(settings = settings, **kwargs)   
    
    """ Private Methods """
    
    def _validate_director(self) -> None:
        """Creates or validates 'self.director'."""
        if self.director is None:
            self.director = ProjectKeystone.keystones['director']
        elif isinstance(self.director, str):
            self.director = ProjectKeystone.keystones[self.director]
        if inspect.isclass(self.director):
            self.director = self.director(project = self)
        else:
            self.director.project = self
        return
    
    """ Dunder Methods """
    
    def __getattr__(self, item: str) -> Any:
        """Checks 'director' for attribute named 'item'.

        Args:
            item (str): name of attribute to check.

        Returns:
            Any: contents of director attribute named 'item'.
            
        """
        try:
            return getattr(self.director, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project or its manager')
           

@dataclasses.dataclass
class ProjectDirector(ProjectKeystone, abc.ABC):
    """Constructor for chrisjen workflows.
        
    Args:
        project (Project): linked Project instance to modify and control.
             
    """
    project: Project
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # Validates core attributes.
        self.validate()
        # Completes 'project' if 'project.automatic' is True.
        self.draft()
        if self.project.automatic:
            self.complete()
                                 
    """ Required Subclass Methods """

    @abc.abstractmethod
    def complete(self) -> None:
        """Applies all workflow components to 'project'."""
        self.publish()
        self.execute()
        return

    """ Public Methods """       
    
    def draft(self) -> None:
        """Adds a project outline to 'project'."""
        self.project.outline = ProjectKeystone.keystones['outline'](
            project = self.project)
        return
    
    def publish(self) -> None:
        """Adds a project workflow to 'project'."""
        if self.project.name in self.project.outline.designs:
            design = self.project.outline.designs[self.project.name]
            workflow = self.project.library.withdraw(item = design)
        else:
            workflow = ProjectKeystone.keystones['workflow'](
                project = self.project)
        self.project.workflow = workflow
        self.project = foundry.complete_workflow(project = self.projectr)
        return
        
    def validate(self) -> None:
        """Validates or creates required portions of 'project'."""
        self._validate_settings()
        self._validate_name()
        self._validate_id()
        self._validate_filer()
        return
    
    """ Private Methods """ 
    
    def _validate_filer(self) -> None:
        """Creates or validates 'project.filer'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        return  
        
    def _validate_id(self) -> None:
        """Creates unique 'project.identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.

        Args:
            project (base.Project): project to examine and validate.
        
        """
        if self.project.identification is None:
            prefix = self.project.name + '_'
            self.project.identification = miller.how_soon_is_now(
                prefix = prefix)
        elif not isinstance(self.project.identification, str):
            raise TypeError('identification must be a str or None type')
        return
            
    def _validate_name(self) -> None:
        """Creates or validates 'project.name'."""
        if self.project.name is None:
            settings_name = self._infer_project_name()
            if settings_name is None:
                self.project.name = amos.namify(item = self.project)
            else:
                self.project.name = settings_name
        return  
        
    def _validate_settings(self) -> None:
        """Creates or validates 'project.settings'."""
        if inspect.isclass(self.project.settings):
            self.project.settings = self.project.settings()
        if self.project.settings is None:
            self.project.settings = self.project.settings.create(
                item = self.project.settings,
                default = {
                    'general': {
                        'verbose': False,
                        'parallelize': False,
                        'efficiency': 'up_front'},
                    'files': {
                        'file_encoding': 'windows-1252',
                        'threads': -1}})
        return

    def _infer_project_name(self) -> str:
        """Tries to infer project name from 'project.settings'."""
        suffixes = self.project.repository.nodes.plurals
        name = None    
        for key, section in self.project.settings.items():
            if (
                key not in ['general', 'files', 'filer', 'filer'] 
                    and any(k.endswith(suffixes) for k in section.keys())):
                name = key
                break
        return name


@dataclasses.dataclass
class ProjectNode(holden.Labeled, ProjectKeystone, abc.ABC):
    """Base class for nodes in a chrisjen project.

    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a project workflow.
            Defaults to None.
        contents (Optional[Any]): stored item(s) to be applied to 'item' passed 
            to the 'complete' method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an
            empty dict.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because ProjectNode will be used as a mixin, it is important to 
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        key = amos.namify(item = cls)
        # Removes 'project_' prefix if it exists.
        if key.startswith('project_'):
            key = key[8:]
        Project.library.deposit(item = cls, name = key)
        if ProjectNode in cls.__bases__:
            Project.library.add_kind(item = cls)
            
        
    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        key = amos.namify(item = self)
        # Removes 'project_' prefix if it exists.
        if key.startswith('project_'):
            key = key[8:]
        Project.library.deposit(item = self, name = key)
                                      
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(self, item: Any, *args: Any, **kwargs: Any) -> Any:
        """Applies 'contents' to 'item'.

        Subclasses must provide their own methods.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        pass

    """ Public Methods """
    
    def complete(self, item: Any, **kwargs: Any) -> Any:
        """Calls the 'implement' method after finalizing parameters.

        Args:
            item (Any): any item or data to which 'contents' should be applied, 
                but most often it is an instance of 'Project'.

        Returns:
            Any: any result for applying 'contents', but most often it is an
                instance of 'Project'.
            
        """
        if self.contents not in [None, 'None', 'none']:
            with contextlib.suppress(AttributeError):
                self.parameters.finalize(item = item)
            result = self.implement(item = item, **self.parameters, **kwargs)
        return result 
           
    """ Dunder Methods """

    def __eq__(self, other: object) -> bool:
        """Test eqiuvalence based on 'name' attribute.

        Args:
            other (object): other object to test for equivalance.
            
        Returns:
            bool: whether 'name' is the same as 'other.name'.
            
        """
        try:
            return str(self.name) == str(other.name) # type: ignore
        except AttributeError:
            return str(self.name) == other

    def __ne__(self, other: object) -> bool:
        """Completes equality test dunder methods.

        Args:
            other (object): other object to test for equivalance.
           
        Returns:
            bool: whether 'name' is not the same as 'other.name'.
            
        """
        return not(self == other)

    def __contains__(self, item: Any) -> bool:
        """Returns whether 'item' is in or equal to 'contents'.

        Args:
            item (Any): item to check versus 'contents'
            
        Returns:
            bool: if 'item' is in or equal to 'contents' (True). Otherwise, it
                returns False.

        """
        try:
            return item in self.contents
        except TypeError:
            try:
                return item is self.contents
            except TypeError:
                return item == self.contents 
