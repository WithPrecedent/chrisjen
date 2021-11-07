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
import functools
import inspect
from typing import Any, ClassVar, Optional, Type, Union
import warnings

import amos

from . import bases
from . import workshop


@dataclasses.dataclass
class Project(Iterator):
    """Interface for a chrisjen project.
    
    Args:
        name (str): designates the name of a class instance that is used for 
            internal referencing throughout chrisjen. For example, if a chrisjen 
            instance needs outline from an Outline instance, 'name' should 
            match the appropriate section name in an Outline instance. Defaults 
            to None. 
        settings
        clerk (ClerkSources): a Clerk-compatible class or a str or pathlib.Path 
            containing the full path of where the root folder should be located 
            for file input and output. A 'clerk' must contain all file path and 
            import/export methods for use throughout chrisjen. Defaults to the 
            default Clerk instance. 
        stages  
        bases
        data (object): any data object for the project to be applied. If it is 
            None, an instance will still execute its workflow, but it won't
            apply it to any external data. Defaults to None.
        identification (str): a unique identification name for a chrisjen 
            Project. The name is used for creating file folders related to the 
            project. If it is None, a str will be created from 'name' and the 
            date and time. Defaults to None.   
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
            
    """
    name: Optional[str] = None
    settings: Optional[amos.Settings] = None
    stages: Sequence[Union[str, Type[bases.ProjectStage]]] = dataclasses.field(
        default_factory = lambda: ['workflow', 'results'])
    bases: bases.ProjectBases = bases.ProjectBases()
    clerk: Optional[amos.Clerk] = None
    data: Optional[object] = None
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
        """[summary]

        Returns:
            str: [description]
            
        """    
        try:    
            return amos.get_name(item = self.stages[self.index])
        except IndexError:
            return 'settings'
    
    @property
    def previous(self) -> str:
        """[summary]

        Returns:
            str: [description]
            
        """        
        try:
            return amos.get_name(item = self.stages[self.index - 1])
        except IndexError:
            return 'settings'
    
    @property
    def subsequent(self) -> Optional[str]:
        """[summary]

        Returns:
            str: [description]
            
        """        
        try:
            return amos.get_name(item = self.stages[self.index + 1])
        except IndexError:
            return None
               
    @functools.cached_property
    def connections(self) -> dict[str, list[str]]:
        """Returns raw connections between nodes from 'settings'.

        Returns:
            dict[str, list[str]]: keys are node names and values are lists of
                nodes to which the key node is connection. These connections
                do not include any structure or design.
            
        """
        return workshop.get_connections(project = self)

    @functools.cached_property
    def designs(self) -> dict[str, str]:
        """Returns structural designs of nodes based on 'settings'.

        Returns:
            dict[str, str]: keys are node names and values are design names.
            
        """
        return workshop.get_designs(project = self)

    @functools.cached_property
    def initialization(self) -> dict[str, dict[str, Any]]:
        """Returns initialization arguments and attributes for nodes.
        
        These values will be parsed into arguments and attributes once the nodes
        are instanced. They are derived from 'settings'.

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of the initialization arguments and attributes.
            
        """
        return workshop.get_initialization(project = self)
        
    @functools.cached_property
    def kinds(self) -> dict[str, str]:
        """Returns kinds based on 'settings'.

        Returns:
            dict[str, str]: keys are names of nodes and values are names of the
                associated base kind types.
            
        """
        return workshop.get_kinds(project = self)
    
    @functools.cached_property
    def labels(self) -> list[str]:
        """Returns names of nodes based on 'settings'.

        Returns:
            list[str]: names of all nodes that are listed in 'settings'.
            
        """
        return workshop.get_labels(project = self)

    @functools.cached_property
    def runtime(self) -> dict[str, dict[str, Any]]:
        """Returns runtime parameters based on 'settings'

        Returns:
            dict[str, dict[str, Any]]: keys are node names and values are dicts
                of runtime parameters.
            
        """
        return workshop.get_runtime(project = self)
                
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for _ in self.stages:
            self.advance()
        return self

    def get_base(self, base_type: str) -> None:
        """[summary]

        Args:
            base_type (str): [description]

        Returns:
            [type]: [description]
            
        """        
        return getattr(self.bases, base_type)

    def set_base(self, base_type: str, base: Type[Any]) -> None:
        """[summary]

        Args:
            base_type (str): [description]
            base (Type[Any]): [description]
            
        """        
        setattr(self.bases, base_type, base)
        return self
                        
    """ Private Methods """
    
    def _validate_name(self) -> None:
        """Creates or validates 'name'."""
        self.name = self.name or amos.get_name(item = self)
        return self  
         
    def _validate_identification(self) -> None:
        """Creates unique 'identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.
        
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
        if (
            not isinstance(self.bases, bases.ProjectBases)
            or not amos.has_attributes(
                item = self,
                attributes = [
                    'clerk', 'component', 'parameters', 'settings', 'stage'])):
            self.bases = bases.ProjectBases()
        return self
            
    def _validate_settings(self) -> None:
        """Creates or validates 'settings'."""
        if not isinstance(self.settings, self.bases.settings):
            self.settings = self.bases.settings.create(item = self.settings)
        return self
          
    def _validate_clerk(self) -> None:
        """Creates or validates 'clerk'."""
        if not isinstance(self.clerk, self.bases.clerk):
            self.clerk = self.bases.clerk(settings = self.settings)
        else:
            self.clerk.settings = self.settings
        return self
          
    def _validate_stages(self) -> None:
        """Validates and/or converts 'stages' attribute."""
        new_stages = [self.settings]
        for stage in self.stages:
            new_stages.append(self._validate_stage(stage = stage))
        self.stages = new_stages
        return self

    def _validate_stage(self, stage: Any) -> object:
        """[summary]

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
                raise KeyError(f'{stage} was not found in the stage library')
        elif inspect.isclass(stage):
            stage = stage()
        return stage

    def _validate_data(self) -> None:
        """Creates or validates 'data'."""
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
        print('test stages', self.index, self.stages)
        print('test previous', self.previous)
        if self.index < len(self.stages):
            source = self.previous
            product = self.current
            print('test source, product', source, product)
            if source != product:
                stage = self.stages[self.index]
                if self.settings['general']['verbose']:
                    print(f'Creating {product} from {source}')
                kwargs = {'project': self}
                setattr(self, product, stage.create(item = self, **kwargs))
            if self.settings['general']['verbose']:
                print(f'Completed {product}')
            self.index += 1
        else:
            raise StopIteration
        return self
