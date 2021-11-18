"""
interface: primary access point and interface for a chrisjen project
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
    Project (amos.Node, Iterator): primary interface for chrisjen projects.

"""
from __future__ import annotations
from collections.abc import Iterable, Iterator, Sequence
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type, Union
import warnings

import amos

from . import bases
from . import configuration
from . import filing

    
@dataclasses.dataclass
class ProjectDefaults(object):
    """Base classes for a chrisjen Project.
    
    Args:
        clerk (Type[Any]): base class for a project filing clerk. Defaults to
            filing.Clerk.
        settings (Type[Any]): base class for project configuration settings.
            Defaults to amos.Settings.
        node (Type[amos.LibraryFactory]): base class for nodes in a project
            workflow. Defaults to bases.ProjectNode.
      
    """
    clerk: Type[Any] = filing.Clerk
    settings: Type[Any] = configuration.ProjectSettings
    node: Type[amos.LibraryFactory] = bases.ProjectNode
    stage: Type[Any] = bases.Stage
    default_stages: list[str] = dataclasses.field(
        default_factory = lambda: ['workflow', 'results'])
    
    
@dataclasses.dataclass
class Project(Iterator):
    """Interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        settings (Optional[amos.Settings]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[filing.Clerk]): a filing clerk for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        data (Optional[object]): any data object for the project to be applied. 
            If it is None, an instance will still execute its workflow, but it 
            won't apply it to any external data. Defaults to None.
        bases (ProjectDefaults): base classes for a project. Users can set
            different bases that will automatically be used by the Project
            framework. Defaults to a ProjectDefaults instance with the default 
            base classes.
        stages (Optional[Sequence[Union[str, Type[Any]]]]): stage nodes or node
            names for creation of the project. Defaults to None.
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
    settings: Optional[amos.Settings] = None
    clerk: Optional[filing.Clerk] = None
    data: Optional[object] = None
    bases: ProjectDefaults = ProjectDefaults()
    stages: Optional[Sequence[Union[str, Type[Any]]]] = None
    identification: Optional[str] = None
    automatic: bool = True
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Validates core attributes.
        self._validate_name()
        self._validate_identification()
        self._validate_bases()
        self._validate_settings()
        self._validate_clerk()
        self._validate_stages()
        self._validate_data()
        # Sets multiprocessing technique, if necessary.
        self._set_parallelization()
        # Sets index for iteration.
        self.index = 0
        # Calls 'complete' if 'automatic' is True.
        if self.automatic:
            self.complete()
    
    """ Properties """
    
    @property
    def current(self) -> str:
        """Returns name of the active node.

        Returns:
            str: name of a node.
            
        """    
        return amos.get_name(item = self.stages[self.index])
         
    @property
    def nodes(self) -> bases.NodeLibrary:
        """Returns the current library of available workflow components.

        Returns:
            bases.NodeLibrary: library of workflow components.
            
        """        
        return self.bases.node.library

    @property
    def previous(self) -> str:
        """Returns name of the previous node.
        
        If a previous node doesn't exist, 'settings' is returned.

        Returns:
            str: name of a node.
            
        """  
        if self.index == 0:
            return 'settings'        
        else:
            return amos.get_name(item = self.stages[self.index - 1])
        
    @property
    def subsequent(self) -> Optional[str]:
        """Returns name of the next node.
        
        If no subsequent node exists, None is returned.
        
        Returns:
            str: name of a node.
            
        """        
        if self.index == len(self.stages) - 1:
            return None
        else:
            return amos.get_name(item = self.stages[self.index + 1])
        
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through the next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for _ in self:
            self.advance()
        return self

    # def get_base(self, base_type: str) -> None:
    #     """[summary]

    #     Args:
    #         base_type (str): [description]

    #     Returns:
    #         [type]: [description]
            
    #     """        
    #     return getattr(self.bases, base_type)

    # def set_base(self, base_type: str, base: Type[Any]) -> None:
    #     """[summary]

    #     Args:
    #         base_type (str): [description]
    #         base (Type[Any]): [description]
            
    #     """        
    #     setattr(self.bases, base_type, base)
    #     return self
                        
    """ Private Methods """
    
    def _validate_name(self) -> None:
        """Creates or validates 'name'."""
        self.name = self.name or amos.get_name(item = self)
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
        if (not isinstance(self.bases, ProjectDefaults)
            or not amos.has_attributes(
                item = self,
                attributes = [
                    'clerk', 'component', 'director', 'settings', 'stage', 
                    'workflow'])):
            self.bases = ProjectDefaults()
        return self
            
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
       
    def _validate_stages(self) -> None:
        """Creates or validates 'stages' and sets iterator index."""
        # Sets index for iteration.
        self.index = 0
        if not self.stages:
            try:
                self.stages = self.settings[self.name]['stages']
            except KeyError:
                try:
                    self.stages = self.settings[self.name][f'{self.name}_stages']
                except KeyError:
                    self.stages = self.bases.default_stages
        validated_stages = [self._validate_stage(s) for s in self.stages]
        self.stages = amos.Pipeline(contents = validated_stages)
        return self
    
    def _validate_stage(self, stage: Any) -> object:
        """Validates or converts a stage to a stage node instance.

        Args:
            stage (Any): [description]

        Raises:
            KeyError: [description]

        Returns:
            object: [description]
            
        """        
        if isinstance(stage, str):
            try:
                stage = self.bases.stage.create(item = stage)
            except KeyError:
                raise KeyError(f'{stage} was not found in the node library')
        if inspect.isclass(stage):
            stage = stage()
        return stage
    
    def _validate_data(self) -> None:
        """Creates or validates 'data'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        return self
    
    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'settings'."""
        if self.settings['general']['parallelize']:
            if not globals()['multiprocessing']:
                import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return self
         
    """ Dunder Methods """
      
    def __iter__(self) -> Iterable:
        """Returns iterable of 'stages'.
        
        Returns:
            Iterable: of 'stages'.
            
        """
        return self
 
    def __next__(self) -> None:
        """Completes a Stage instance."""
        if self.index < len(self.stages):
            source = self.previous or 'settings'
            product = self.current
            if self.settings['general']['verbose']:
                print(f'Creating {product} from {source}')
            stage = self.stages[self.index]
            stage.create(project = self)
            if self.settings['general']['verbose']:
                print(f'Completed {product}')
            self.index += 1
        else:
            raise StopIteration
        return self
