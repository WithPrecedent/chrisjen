"""
interface: primary access point and user interface for a chrisjen project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
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
    ProjectBases (object): contains base class for a chrisjen project. Users
        can set or pass different attributes to use different base classes.
    Project (object): primary user interface for chrisjen projects.

To Do:
    Improve validator methods in Project for certain attributes yo handle more
        cases and situations.
    Consider adding a 'deliverable' or 'dossier' attribute to store data, 
        nodes, and other information to pass to 'execute' methods.
    
"""
from __future__ import annotations
from collections.abc import MutableMapping
import dataclasses
import functools
import inspect
import pathlib
from typing import Any, Optional, Type, Union
import warnings

import amos

from . import bases
from . import configuration
from . import filing
from . import workshop
    
    
@dataclasses.dataclass
class ProjectBases(object):
    """Base classes for a chrisjen Project.
    
    Args:
        clerk (Type[Any]): base class for a project filing clerk. Defaults to
            filing.Clerk.
        settings (Type[Any]): base class for project configuration settings.
            Defaults to amos.Settings.
        workflow
        results
        node (Type[amos.LibraryFactory]): base class for nodes in a project
            workflow. Defaults to bases.Component.
        criteria
      
    """
    clerk: Type[Any] = filing.Clerk
    settings: Type[Any] = configuration.ProjectSettings
    outline: Type[Any] = bases.Outline
    workflow: Type[Any] = bases.Workflow
    results: Type[Any] = bases.Results
    node: Type[amos.LibraryFactory] = bases.Component
    criteria: Type[Any] = bases.Criteria

    
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[amos.Settings]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[filing.Clerk]): a filing clerk for loading and saving 
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
    
    Attributes:
        options (bases.ProjectCatalog): a catalog of all available node classes
            that can be used in a project workflow. By default, it is a
            property that points to 'bases.node.options'.
        results (amos.Composite): stored results from the execution of the
            project 'workflow'. It is created when the 'complete' method is
            called.
        workflow (amos.Composite): workflow process for executing the project.
            It is a cached property that calls the 'create_workflow' function
            the first time it is called and becomes an attribute with a 
            workflow after that.
            
    """
    name: Optional[str] = None
    settings: Optional[amos.Settings] = None
    clerk: Optional[filing.Clerk] = None
    bases: ProjectBases = ProjectBases()
    data: Optional[object] = None
    identification: Optional[str] = None
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
        self._validate_bases()
        self._validate_clerk()
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
    def options(self) -> bases.ProjectCatalog:
        """Returns the current options of available workflow components.

        Returns:
            bases.ProjectCatalog: options of workflow components.
            
        """        
        return self.bases.node.options
  
    @options.setter
    def options(self, value: bases.ProjectCatalog) -> None:
        """Sets the current options of available workflow components.

        Arguments:
            value (bases.ProjectCatalog): new options for workflow components.
            
        """        
        self.bases.node.options = value
        return self
     
    @functools.cached_property
    def workflow(self) -> bases.Workflow:
        """Returns workflow based on 'settings'

        Returns:
            bases.Workflow: the workflow derived from 'settings'.
            
        """        
        return workshop.create_workflow(project = self)
       
    """ Class Methods """

    @classmethod
    def create(
        cls, 
        settings: Union[pathlib.Path, str, amos.Settings],
        **kwargs) -> Project:
        """Returns a Project instance based on 'settings' and kwargs.

        Args:
            settings (Union[pathlib.Path, str, amos.Settings]): a path to a file
                containing configuration settings or a Settings instance.

        Returns:
            Project: an instance based on 'settings' and kwargs.
            
        """        
        return cls(settings = settings, **kwargs)
       
    """ Public Methods """
        
    def complete(self) -> None:
        """Iterates through all stages."""
        self.results = self.results.create(project = self)
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
                or not isinstance(self.settings, self.bases.settings)):
            self.settings = self.bases.settings.create(
                item = self.settings,
                project = self)
        elif isinstance(self.settings, self.bases.settings):
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
         
    def _validate_bases(self) -> None:
        """Creates or validates 'bases'."""
        if inspect.isclass(self.bases):
            self.bases = self.bases()
        if (not isinstance(self.bases, ProjectBases)
            or not amos.has_attributes(
                item = self,
                attributes = [
                    'clerk', 'component', 'director', 'settings', 'stage', 
                    'workflow'])):
            self.bases = ProjectBases()
        return self

    def _validate_clerk(self) -> None:
        """Creates or validates 'clerk'."""
        if inspect.isclass(self.clerk):
            self.clerk = self.clerk(settings = self.settings)
        if (self.clerk is None or 
                not isinstance(self.clerk, self.bases.clerk)):
            self.clerk = self.bases.clerk(settings = self.settings)
        else:
            self.clerk.settings = self.settings
        return self
    
    # def _validate_workflow(self) -> None:
    #     """Creates or validates 'workflow'."""
    #     if self.workflow is None:
    #         self.workflow = self.bases.workflow
    #     return self

    # def _validate_results(self) -> None:
    #     """Creates or validates 'results'."""
    #     if not hasattr(self, 'results'):
    #         self.results = self.bases.results
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
        if (
            'general' in self.settings
                and 'parallelize' in self.settings['general'] 
                and self.settings['general']['parallelize']):
            if not globals()['multiprocessing']:
                import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return self  
