"""
bases: base classes for a chrisjen project
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
    ProjectNode (amos.Node, abc.ABC):
    ProjectComponent (amos.LibraryFactory, ProjectNode, abc.ABC):
    ProjectStage (amos.LibraryFactory, ProjectNode, abc.ABC):
    ProjectDirector (amos.LibraryFactory, Iterator):

To Do:
    Make ProjectNode a subclass of amos.Node by fixing the proxy access methods
        that currently return errors.
            
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Iterable, Iterator, Mapping, MutableMapping, Sequence)
import copy
import dataclasses
import inspect
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos

if TYPE_CHECKING:
    from . import interface


@dataclasses.dataclass
class NodeLibrary(amos.Library):
    """Stores project classes and class instances.
    
    When searching for matches, instances are prioritized over classes.
    
    Args:
        classes (Catalog): a catalog of stored classes. Defaults to any empty
            Catalog.
        instances (Catalog): a catalog of stored class instances. Defaults to an
            empty Catalog.
                 
    """
    classes: amos.Catalog[str, Type[Any]] = dataclasses.field(
        default_factory = amos.Catalog)
    instances: amos.Catalog[str, object] = dataclasses.field(
        default_factory = amos.Catalog)

    """ Properties """
    
    @property
    def suffixes(self) -> tuple[str]:
        """Returns all stored names and naive plurals of those names.
        
        Returns:
            tuple[str]: all names with an 's' added in order to create simple 
                plurals combined with the stored keys.
                
        """
        plurals = [key + 's' for key in self.instances.keys()] 
        return tuple(plurals + [key + 's' for key in self.classes.keys()])

             
@dataclasses.dataclass
class ProjectNode(amos.LibraryFactory, abc.ABC):
    """Base class for nodes in a chrisjen project.

    Args:
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
        iterations (Union[int, str]): number of times the 'implement' method 
            should  be called. If 'iterations' is 'infinite', the 'implement' 
            method will continue indefinitely unless the method stops further 
            iteration. Defaults to 1.
        library (ClassVar[NodeLibrary]): a NodeLibrary instance storing both 
            subclasses and instances. 
              
    """
    contents: Optional[Any] = None
    name: Optional[str] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    iterations: Union[int, str] = 1
    library: ClassVar[NodeLibrary] = NodeLibrary() 
    
    """ Initialization Methods """
    
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Forces subclasses to use the same hash methods as ProjectNode.
        
        This is necessary because dataclasses, by design, do not automatically 
        inherit the hash and equivalance dunder methods from their super 
        classes.
        
        """
        # Calls other '__init_subclass__' methods for parent and mixin classes.
        try:
            super().__init_subclass__(*args, **kwargs) # type: ignore
        except AttributeError:
            pass
        # Copies hashing related methods to a subclass.
        cls.__hash__ = ProjectNode.__hash__ # type: ignore
        cls.__eq__ = ProjectNode.__eq__ # type: ignore
        cls.__ne__ = ProjectNode.__ne__ # type: ignore

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Sets 'name' attribute if 'name' is None.
        self.name = self.name or amos.get_name(item = self)
        # Calls other '__post_init__' methods for parent and mixin classes.
        try:
            super().__post_init__() # type: ignore
        except AttributeError:
            pass
        
    """ Required Subclass Methods """

    @abc.abstractmethod
    def implement(
        self, 
        project: interface.Project, 
        **kwargs) -> interface.Project:
        """Applies 'contents' to 'project'.

        Subclasses must provide their own methods.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        pass

    """ Public Methods """
    
    def execute(self, 
        project: interface.Project, 
        iterations: Optional[Union[int, str]] = None, 
        **kwargs) -> interface.Project:
        """Calls the 'implement' method the number of times in 'iterations'.

        Args:
            project (interface.Project): instance from which data needed for 
                implementation should be derived and all results be added.

        Returns:
            interface.Project: with possible changes made.
            
        """
        iterations = iterations or self.iterations
        if self.contents not in [None, 'None', 'none']:
            if self.parameters:
                if hasattr(self.parameters, 'finalize'):
                    self.parameters.finalize(project = project)
                parameters = self.parameters
                parameters.update(kwargs)
            else:
                parameters = kwargs
            if iterations in ['infinite']:
                while True:
                    project = self.implement(project = project, **parameters)
            else:
                for _ in range(iterations):
                    project = self.implement(project = project, **parameters)
        return project
            
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return issubclass(subclass, Hashable) and hasattr(subclass, 'name')
               
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        """Returns whether 'instances' is an instance of this class.

        Args:
            instance (object): item to test as an instance.

        Returns:
            bool: whether 'instance' is an instance of this class.
            
        """
        return amos.is_node(item = instance)
    
    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a composite object that uses a dict as
        its base storage type.
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Makes Node hashable so that it can be used as a key in a dict.

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


@dataclasses.dataclass
class ProjectDirector(amos.LibraryFactory, amos.Dictionary):
    """Iterator for a chrisjen Project.
    
    
    """
    contents: Sequence[Union[str, Type[ProjectNode]]] = dataclasses.field(
        default_factory = lambda: ['outline', 'workflow', 'results'])
    project: interface.Project = None
    library: ClassVar[amos.Library] = amos.Library()
   
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Calls parent and/or mixin initialization method(s).
        try:
            super().__post_init__()
        except AttributeError:
            pass
        # Sets index for iteration.
        self.index = 0
        # Validate stages
        self._validate_stages()
        
    """ Properties """
    
    @property
    def current(self) -> str:
        """[summary]

        Returns:
            str: [description]
            
        """    
        return amos.get_name(item = self.stages[self.index])
    
    @property
    def previous(self) -> str:
        """[summary]

        Returns:
            str: [description]
            
        """
        if self.index == 0:
            return 'settings'        
        else:
            return amos.get_name(item = self.stages[self.index - 1])
    
    @property
    def stages(self) -> Sequence[Union[str, Type[ProjectNode]]]:
        """[summary]

        Returns:
            Sequence[Union[str, Type[ProjectNode]]]: [description]
            
        """
        return self.contents
    
    @property
    def subsequent(self) -> Optional[str]:
        """[summary]

        Returns:
            str: [description]
            
        """        
        if self.index == len(self.stages) - 1:
            return None
        else:
            return amos.get_name(item = self.stages[self.index + 1])
 
    """ Public Methods """
    
    def advance(self) -> None:
        """Iterates through next stage."""
        return self.__next__()

    def complete(self) -> None:
        """Iterates through all stages."""
        for _ in self.stages:
            self.advance()
        return self    
    
    """ Private Methods """
    
    def _validate_stages(self) -> None:
        """Validates and/or converts 'stages' attribute."""
        self.stages = [self._validate_stage(stage) for stage in self.stages]
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
                stage = self.project.bases.node.create(item = stage)
            except KeyError:
                raise KeyError(f'{stage} was not found in the node library')
        if inspect.isclass(stage):
            stage = stage()
        return stage
            
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
            if self.project.settings['general']['verbose']:
                print(f'Creating {product} from {source}')
            stage = self.stages[self.index]
            self.project = stage.execute(project = self)
            if self.project.settings['general']['verbose']:
                print(f'Completed {product}')
            self.index += 1
        else:
            raise StopIteration
        return self
    