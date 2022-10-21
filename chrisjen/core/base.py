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
class ProjectFactory(ProjectKeystone):
    """Stores and creates node classes instances and classes.
    
    Args:
        store (amos.Library): library of nodes.
                 
    """
    project: Project
    store: amos.Library = amos.Library()
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
            plurals = [k + 's' for k in getattr(self.store, catalog).keys()]
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

    def create(self, name: str, **kwargs) -> ProjectNode:
        """_summary_

        Args:
            name (str): _description_

        Returns:
            ProjectNode: _description_
            
        """
        keys = [name]
        if name in self.project.outline.designs:
            keys.append(self.project.outline.designs[name])
        if name in self.project.outline.kinds:
            keys.append(self.project.outline.kinds[name])
        node = self.library.withdraw(item = keys)
        return node.create(name = name, project = self.project, **kwargs)
           
         
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
        factory (ClassVar[ProjectFactory]): factory of nodes for executing a
            chrisjen project. 
    
    """
    name: Optional[str] = None
    settings: Optional[bobbie.Settings] = None
    clerk: Optional[ProjectKeystone] = None
    director: Optional[ProjectKeystone] = None
    identification: Optional[str] = None
    automatic: Optional[bool] = True
    factory: ClassVar[ProjectFactory] = ProjectFactory()
        
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
            workflow = self.project.factory.withdraw(item = design)
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
class Parameters(amos.Dictionary, ProjectKeystone):
    """Creates and stores parameters for part of a chrisjen project.
    
    The use of Parameters is entirely optional, but it provides a handy 
    tool for aggregating data from an array of sources, including those which 
    only become apparent during execution of a chrisjen project, to create a 
    unified set of implementation parameters.
    
    Parameters can be unpacked with '**', which will turn the contents of the
    'contents' attribute into an ordinary set of kwargs. In this way, it can 
    serve as a drop-in replacement for a dict that would ordinarily be used for 
    accumulating keyword arguments.
    
    If a chrisjen class uses a Parameters instance, the 'finalize' method should 
    be called before that instance's 'implement' method in order for each of the 
    parameter types to be incorporated.
    
    Args:
        contents (Mapping[str, Any]): keyword parameters for use by a chrisjen
            classes' 'implement' method. The 'finalize' method should be called
            for 'contents' to be fully populated from all sources. Defaults to
            an empty dict.
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. To properly match 
            parameters in a Settings instance, 'name' should be the prefix to 
            "_parameters" as a section name in a Settings instance. Defaults to 
            None. 
        default (Mapping[str, Any]): default parameters that will be used if 
            they are not overridden. Defaults to an empty dict.
        implementation (Mapping[str, str]): parameters with values that can only 
            be determined at runtime due to dynamic nature of chrisjen and its 
            workflows. The keys should be the names of the parameters and the 
            values should be attributes or items in 'contents' of 'project' 
            passed to the 'finalize' method. Defaults to an emtpy dict.
        selected (MutableSequence[str]): an exclusive list of parameters that 
            are allowed. If 'selected' is empty, all possible parameters are 
            allowed. However, if any are listed, all other parameters that are
            included are removed. This is can be useful when including 
            parameters in an Outline instance for an entire step, only some of
            which might apply to certain techniques. Defaults to an empty list.

    """
    contents: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    name: Optional[str] = None
    default: Mapping[str, Any] = dataclasses.field(default_factory = dict)
    implementation: Mapping[str, str] = dataclasses.field(
        default_factory = dict)
    selected: MutableSequence[str] = dataclasses.field(default_factory = list)
      
    """ Public Methods """

    def finalize(self, item: Any, **kwargs) -> None:
        """Combines and selects final parameters into 'contents'.

        Args:
            item (Project): instance from which implementation and 
                settings parameters can be derived.
            
        """
        # Uses kwargs and 'default' parameters as a starting amos.
        parameters = self.default
        # Adds any parameters from 'outline'.
        parameters.update(self._from_outline(item = item))
        # Adds any implementation parameters.
        parameters.update(self._at_runtime(item = item))
        # Adds any parameters already stored in 'contents'.
        parameters.update(self.contents)
        # Adds any passed kwargs, which will override any other parameters.
        parameters.update(kwargs)
        # Limits parameters to those in 'selected'.
        if self.selected:
            parameters = {k: parameters[k] for k in self.selected}
        self.contents = parameters
        return self

    """ Private Methods """
     
    def _from_outline(self, project: Project) -> dict[str, Any]: 
        """Returns any applicable parameters from 'outline'.

        Args:
            project (base.Project): project has parameters from 'outline.'

        Returns:
            dict[str, Any]: any applicable outline parameters or an empty dict.
            
        """
        keys = [self.name]
        keys.append(project.outline.kinds[self.name])
        try:
            keys.append(project.outline.designs[self.name])
        except KeyError:
            pass
        for key in keys:
            try:
                return project.outline.implementation[key]
            except KeyError:
                pass
        return {}
   
    def _at_runtime(self, item: Any) -> dict[str, Any]:
        """Adds implementation parameters to 'contents'.

        Args:
            item (Project): instance from which implementation 
                parameters can be derived.

        Returns:
            dict[str, Any]: any applicable settings parameters or an empty dict.
                   
        """    
        for parameter, attribute in self.implementation.items():
            try:
                self.contents[parameter] = getattr(item, attribute)
            except AttributeError:
                try:
                    self.contents[parameter] = (
                        item.settings['general'][attribute])
                except (KeyError, AttributeError):
                    pass
        return self
    
    
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
            empty Parameters instance.
              
    """
    name: Optional[str] = None
    contents: Optional[Any] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = Parameters)

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
        Project.factory.deposit(item = cls, name = key)
        if ProjectNode in cls.__bases__:
            Project.factory.add_kind(item = cls)
            
    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        key = amos.namify(item = self)
        # Removes 'project_' prefix if it exists.
        if key.startswith('project_'):
            key = key[8:]
        Project.factory.deposit(item = self, name = key)
                                      
    """ Required Subclass Methods """

    @abc.abstractclassmethod
    def create(cls, name: str, project: Project, **kwargs) -> ProjectNode:
        """Creates a ProjectNode instance based on passed arguments.

        Args:
            name (str): name of node instance to be created.
            project (Project): project with information to create a node
                instance.
                
        Returns:
            ProjectNode: an instance based on passed arguments.
            
        """
        pass
    
    @abc.abstractmethod
    def implement(self, item: Any, **kwargs: Any) -> Any:
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
