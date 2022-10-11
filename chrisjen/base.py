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
    Callable, Container, Hashable, Mapping, MutableMapping, Sequence, Set)
import copy
import dataclasses
import functools
import inspect
import itertools
import multiprocessing
import pathlib
from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union
import warnings

import amos
import bobbie
import nagata

if TYPE_CHECKING:
    from . import workshop
 

CONFIGURATION_SUFFIXES: MutableMapping[str, tuple[str]] = {
    'design': ('design',),
    'files': ('filer', 'files'),
    'general': ('general',),
    'parameters': ('parameters',),
    'structure': ('project',)}
    
FILER_SETTINGS: MutableMapping[str, Any] = {
    'file_encoding': 'windows-1252',
    'conserve_memory': False,
    'threads': -1}

""" 
Project Base Registry

Key names are str names of a subclass (snake_case by default) and values are the 
subclasses. Defaults to an empty dict.  

""" 
PROJECT_BASES: MutableMapping[str, Type[ProjectBase]] = {}


@dataclasses.dataclass
class ProjectBase(amos.Registrar, abc.ABC):
    """Mixin for all project base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in 'registry'."""
        # Because Registrar will often be used as a mixin, it is important to
        # call other base class '__init_subclass__' methods, if they exist.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        if ProjectBase in cls.__bases__:
            key = amos.namify(item = cls)
            PROJECT_BASES[key] = cls
        
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(cls, *args, **kwargs):
        """Creates a class instance."""
        pass


@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[bobbie.Settings]): configuration settings for the 
            project. Defaults to None.
        filer (Optional[filing.Filer]): a filing filer for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        bases (ProjectBases): base classes for a project. Users can set
            different bases that will automatically be used by the Project
            framework. Defaults to a ProjectBases instance with the default 
            base classes.
        data (Optional[object]): any data object for the project to be applied. 
            If it is None, an instance will still execute its workflow, but it 
            won't apply it to any external data. Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None.   
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
    
    """
    name: Optional[str] = None
    settings: Optional[bobbie.Settings] = None
    filer: Optional[nagata.FileManager] = None
    bases: MutableMapping[str, Type[Any]] = dataclasses.field(
        default_factory = lambda: PROJECT_BASES)
    data: Optional[object] = None
    identification: Optional[str] = None
    outline: Optional[object] = None
    workflow: Optional[object] = None
    summary: Optional[object] = None
    automatic: bool = True
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates core attributes.
        self._validate_settings()
        self._validate_name()
        self._validate_identification()
        # self._validate_bases()
        self._validate_filer()
        # self._validate_workflow()
        # self._validate_results()
        self._validate_data()
        # Sets multiprocessing technique, if necessary.
        self._set_parallelization()
        # Calls 'complete' if 'automatic' is True.
        if self.automatic:
            self.complete()
    
    """ Properties """
         
    @property
    def options(self) -> amos.Library:
        """Returns the current options of available workflow components.

        Returns:
            amos.Library: options of workflow components.
            
        """        
        return self.bases['component'].library
  
    # @options.setter
    # def options(self, value: amos.Library) -> None:
    #     """Sets the current options of available workflow components.

    #     Arguments:
    #         value (Options): new options for workflow components.
            
    #     """        
    #     self.node.library = value
    #     return self
    
    # @functools.cached_property
    # def outline(self) -> Container:
    #     """Returns project outline based on 'settings'

    #     Returns:
    #         Outline: the outline derived from 'settings'.
            
    #     """        
    #     return workshop.create_outline(project = self)
    
    # @functools.cached_property
    # def workflow(self) -> Container:
    #     """Returns workflow based on 'settings'

    #     Returns:
    #         Workflow: the workflow derived from 'settings'.
            
    #     """        
    #     return workshop.create_workflow(project = self)
       
    """ Class Methods """

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
       
    """ Public Methods """
        
    def complete(self) -> None:
        """Iterates through all stages."""
        if self.outline is None:
            self.outline = workshop.create_outline(project = self)
        if self.workflow is None:
            self.workflow = workshop.create_workflow(project = self)
        if self.result is None:
            self.results = workshop.create_results(project = self)
        return self
     
    # def draft(self) -> None:
    #     """Creates a workflow instance based on 'settings'."""
    #     self.workflow = self.workflow.create(project = self)
    #     return self
        
    # def execute(self) -> None:
    #     """Creates a results instance based on 'workflow'."""
    #     self.results = self.results.create(project = self)
    #     return self
          
    """ Private Methods """
            
    def _validate_settings(self) -> None:
        """Creates or validates 'settings'."""
        if inspect.isclass(self.settings):
            self.settings = self.settings(project = self)
        if (self.settings is None 
                or not isinstance(self.settings, self.settings)):
            self.settings = self.settings.create(
                item = self.settings,
                project = self)
        elif isinstance(self.settings, self.settings):
            self.settings.project = self
        return self
              
    def _validate_name(self) -> None:
        """Creates or validates 'name'."""
        if self.name is None:
            settings_name = workshop.infer_project_name(project = self)
            if settings_name is None:
                self.name = self.name or amos.get_name(item = self)
            else:
                self.name = settings_name
        return self  
         
    def _validate_identification(self) -> None:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
        Raises:
            TypeError: if the 'identification' attribute is neither a str nor
                None.
                
        """
        if self.identification is None:
            prefix = self.name + '_'
            self.identification = amos.datetime_string(prefix = prefix)
        elif not isinstance(self.identification, str):
            raise TypeError('identification must be a str or None type')
        return self
    
    def _validate_filer(self) -> None:
        """Creates or validates 'filer'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        return self
       
    # def _validate_bases(self) -> None:
    #     """Creates or validates 'bases'."""
    #     if inspect.isclass(self.bases):
    #         self.bases = self.bases()
    #     if (not isinstance(self.bases, ProjectBases)
    #         or not amos.has_attributes(
    #             item = self,
    #             attributes = [
    #                 'filer', 'component', 'director', 'settings', 'stage', 
    #                 'workflow'])):
    #         self.bases = ProjectBases()
    #     return self

    
    # def _validate_workflow(self) -> None:
    #     """Creates or validates 'workflow'."""
    #     if self.workflow is None:
    #         self.workflow = self.workflow
    #     return self

    # def _validate_results(self) -> None:
    #     """Creates or validates 'results'."""
    #     if not hasattr(self, 'results'):
    #         self.results = self.results
    #     return self
    
    def _validate_data(self) -> None:
        """Creates or validates 'data'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        return self
    
    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'settings'."""
        if ('general' in self.settings
                and 'parallelize' in self.settings['general'] 
                and self.settings['general']['parallelize']):
            if not globals()['multiprocessing']:
                import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return self  
   
    