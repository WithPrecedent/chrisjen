"""
keystones: base classes for a chrisjen project
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
    Criteria
    Librarian
    Manager
    Node
    Parameters
    View

To Do:

            
"""
from __future__ import annotations
import abc
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import contextlib
import dataclasses
import inspect
import itertools
import pathlib
from typing import Any, Callable, ClassVar, Optional, Type, TYPE_CHECKING

import amos
import bobbie
import holden
import miller
import nagata

from . import framework
 

@dataclasses.dataclass   
class Criteria(framework.ProjectKeystone):
    """Used for conditional nodes.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal and external referencing in a composite object.
            Defaults to None.
        contents (Optional[Any]): stored item(s) that has/have an 'implement' 
            method. Defaults to None.
        parameters (MutableMapping[Hashable, Any]): parameters to be attached to 
            'contents' when the 'implement' method is called. Defaults to an 
            empty dict.
            
    """
    name: Optional[str] = None
    contents: Optional[Callable] = None
    parameters: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)

    """ Public Methods """

    @classmethod
    def create(
        cls, 
        project: framework.Project,
        name: Optional[str] = None,
        **kwargs: Any) -> Criteria:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (framework.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            Criteria: subclass instance based on passed arguments.
            
        """
        return cls(name = name, **kwargs)
                

@dataclasses.dataclass
class Librarian(framework.ProjectKeystone, abc.ABC):
    """Stores, organizes, and builds nodes.
        
    Args:
        project (framework.Project): linked Project instance with a 'library'
            attribute containing ProjectKeystones.
             
    """
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)
    
    """ Public Methods """   
        
    def acquire(
        self, 
        name: str | tuple[str, str], 
        **kwargs: Any) -> Node:
        """Gets node from the project library and returns an instance.

        Args:
            name (str | tuple[str, str]): name of the node that should match
                a key in the project library.

        Returns:
            Node: a Node subclass instance based on passed arguments.
            
        """
        if isinstance(name, tuple):
            step = self.acquire(name = name[0])
            technique = self.acquire(name = name[1])
            return step.create(
                name = name[0], 
                technique = technique,
                project = self.project)
        else:
            lookups = self._get_lookups(name = name)
            # initialization = self._get_initialization(lookups = lookups)
            # initialization.update(**kwargs)
            node = self._get_node(lookups = lookups)
            return node.create(name = name, project = self.project, **kwargs)

    # def collect(
    #     self, 
    #     name: str, 
    #     **kwargs: Any) -> Node:
    #     """Gets node and all subnodes from project library.

    #     Args:
    #         name (str): name of the node that should match a key in the project
    #             library.

    #     Returns:
    #         keystones.Node: a Node subclass instance based on passed arguments.
            
    #     """
    #     lookups = self._get_lookups(name = name)
    #     initialization = self._get_initialization(lookups = lookups)
    #     initialization.update(**kwargs)
    #     node = self._get_node(lookups = lookups)
    #     return node.create(
    #         name = name, 
    #         project = self.project, 
    #         **initialization)
            
    @classmethod
    def create(
        cls, 
        project: framework.Project,
        name: Optional[str] = None,
        **kwargs: Any) -> Librarian:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (framework.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            Librarian: subclass instance based on passed arguments.
            
        """
        return cls(project = project, **kwargs)
    
    """ Private Methods """
    
    # def _get_implementation(self, lookups: list[str]) -> dict[str, Any]:
    #     """_summary_

    #     Args:
    #         lookups (list[str]): _description_

    #     Raises:
    #         TypeError: _description_

    #     Returns:
    #         dict[str, Any]: _description_
            
    #     """
    #     for key in lookups:
    #         try:
    #             return self.project.outline.implementation[key]
    #         except KeyError:
    #             pass
    #     return {}
        
    def _get_initialization(self, lookups: list[str]) -> dict[str, Any]:
        """_summary_

        Args:
            lookups (list[str]): _description_

        Raises:
            TypeError: _description_

        Returns:
            dict[str, Any]: _description_
        """
        for key in lookups:
            try:
                return self.project.outline.initialization[key]
            except KeyError:
                pass
        return {}
        
    def _get_lookups(self, name: str) -> list[str]:
        """_summary_

        Args:
            name (str): _description_

        Returns:
            list[str]: _description_
            
        """
        if name in framework.ProjectRules.null_names:
            return ['null_node']
        else:
            keys = [name]
            if name in self.project.outline.designs:
                keys.append(self.project.outline.designs[name])
            elif name is self.project.name:
                keys.append(framework.ProjectRules.default_worker)
            if name in self.project.outline.kinds:
                keys.append(self.project.outline.kinds[name])
            return keys
    
    def _get_node(self, lookups: list[str]) -> Node:
        """_summary_

        Args:
            lookups (list[str]): _description_

        Raises:
            KeyError: _description_

        Returns:
            Node: _description_
        """
        for key in lookups:
            try:
                return self.project.library.node[key]
            except KeyError:
                pass
        raise KeyError(f'No matching node found for these: {lookups}')  
              

@dataclasses.dataclass
class Manager(framework.ProjectKeystone, abc.ABC):
    """Controller for chrisjen projects.
        
    Args:
        project (framework.Project): linked Project instance to modify and 
            control.
             
    """
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)
    clerk: Optional[nagata.FileManager] = None
    librarian: Optional[Librarian] = None
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        # Validates core attributes.
        self.validate()
        if self.project.automatic:
            self.complete()

    """ Required Subclass Methods """

    @abc.abstractmethod   
    def complete(self) -> None:
        """Applies workflow to 'project'."""
        return
                                 
    """ Public Methods """   
    
    @classmethod
    def create(
        cls, 
        project: framework.Project,
        name: Optional[str] = None,
        **kwargs: Any) -> Manager:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (framework.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            Manager: subclass instance based on passed arguments.
            
        """
        return cls(project = project, **kwargs)
        
    def validate(self) -> None:
        """Validates or creates required portions of 'project'."""
        self._validate_idea()
        self._validate_name()
        self._validate_id()
        self._validate_clerk()
        self._set_parallelization()
        self = framework.ProjectKeystones.validate(
            item = self, 
            attribute = 'librarian')
        return
    
    """ Private Methods """ 
    
    def _validate_clerk(self) -> None:
        """Creates or validates 'project.clerk'.
        
        The default method performs no validation but is included as a hook for
        subclasses to override if validation of the 'data' attribute is 
        required.
        
        """
        try:
            defaults = self.project.rules.default_settings['files']
            nagata.FileFramework.settings.update(defaults)
        except KeyError:
            pass
        for key in self.project.rules.parsers['files']:
            try:
                project_settings = self.project.idea[key]
                nagata.FileFramework.settings.update(project_settings)
            except KeyError:
                pass
        root_folder = pathlib.Path('..').joinpath('data')
        root_folder = pathlib.Path(root_folder).joinpath(
            self.project.identification)
        self.clerk = nagata.FileManager(
            root_folder = root_folder,
            input_folder = 'input',
            interim_folder = 'interim',
            output_folder = 'output')
        return
        
    def _validate_id(self) -> None:
        """Creates unique 'project.identification' if one doesn't exist.
        
        By default, 'identification' is set to the 'name' attribute followed by
        an underscore and the date and time.

        Args:
            project (Project): project to examine and validate.
        
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
            idea_name = self._infer_project_name()
            if idea_name is None:
                self.project.name = amos.namify(item = self.project)
            else:
                self.project.name = idea_name
        if self.project.name.endswith('_project'):
            self.project.name = self.project.name[:-8]
        return  
        
    def _validate_idea(self) -> None:
        """Creates or validates 'project.idea'."""
        if inspect.isclass(self.project.idea):
            self.project.idea = self.project.idea()
        elif not isinstance(self.project.idea, bobbie.Settings):
            base = bobbie.Settings
            self.project.idea = base.create(
                source = self.project.idea,
                default = framework.ProjectRules.default_settings)        
        return

    def _infer_project_name(self) -> str:
        """Tries to infer project name from 'project.idea'."""
        name = None    
        for key in self.project.idea.keys():
            if key.endswith('_project'):
                name = key.removesuffix('_project')
                break
        return name
    
    def _validate_librarian(self) -> None:
        """Creates or validates 'librarian'."""
        if self.librarian is None:
            self.librarian = framework.ProjectKeystones.librarian[
                framework.ProjectRules.default_librarian]
        elif isinstance(self.manager, str):
            self.librarian = framework.ProjectKeystones.librarian[
                self.librarian]
        if inspect.isclass(self.librarian):
            self.librarian = self.librarian(project = self)
        else:
            self.librarian.project = self
        return

    def _set_parallelization(self) -> None:
        """Sets multiprocessing method based on 'settings'.
        
        Args:
            project (Project): project containing parallelization settings.
            
        """
        if ('general' in self.project.idea
                and 'parallelize' in self.project.idea['general'] 
                and self.project.idea['general']['parallelize']):
            if not globals()['multiprocessing']:
                import multiprocessing
            multiprocessing.set_start_method('spawn') 
        return 
        
    """ Dunder Methods """
    
    def __getattr__(self, item: str) -> Any:
        """Checks 'librarian' for attribute named 'item'.

        Args:
            item (str): name of attribute to check.

        Returns:
            Any: contents of librarian attribute named 'item'.
            
        """
        try:
            return getattr(self.librarian, item)
        except AttributeError:
            return AttributeError(
                f'{item} is not in the project manager or its librarian')


@dataclasses.dataclass
class Node(holden.Labeled, framework.ProjectKeystone, Hashable, abc.ABC):
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
        """Makes subclass instances hashable.

        This method forces subclasses to use the same hash methods as 
        Node. This is necessary because dataclasses, by design, do not 
        automatically inherit the hash and equivalance dunder methods from their 
        parent classes.        
        
        """
        # Because Node will be used as a mixin, it is important to 
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        # Copies hashing related methods to a subclass.
        cls.__hash__ = Node.__hash__ # type: ignore
        cls.__eq__ = Node.__eq__ # type: ignore
        cls.__ne__ = Node.__ne__ # type: ignore  
                                      
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
        with contextlib.suppress(AttributeError):
            self.parameters.finalize(item = item)
        return self.implement(item = item, **self.parameters, **kwargs)
    
    @classmethod
    def create(
        cls, 
        project: framework.Project,
        name: Optional[str] = None,
        **kwargs: Any) -> Node:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (framework.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            Node: subclass instance based on passed arguments.
            
        """
        return cls(name = name, **kwargs)
    
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
    
    def __hash__(self) -> int:
        """Makes Node hashable so that it can be used as a key in a dict.

        Rather than using the object ID, this method prevents two Nodes with
        the same name from being used in a graph object that uses a dict as
        its base storage type.
        
        Returns:
            int: hashable of 'name'.
            
        """
        return hash(self.name)


@dataclasses.dataclass   
class View(framework.ProjectKeystone, abc.ABC):
    """Organizes data in a related project to increase accessibility.
    
    View subclasses should emphasize the used of properties so that any changes
    to the related project are automatically reflected in the View subclass.
    
    Args:
        name
        project (framework.Project): a related project instance which has data 
            from which the properties of a View can be derived.
            
    """
    name: Optional[str] = None
    project: Optional[framework.Project] = dataclasses.field(
        default = None, repr = False, compare = False)
    
    """ Public Methods """

    @classmethod
    def create(
        cls, 
        project: framework.Project,
        name: Optional[str] = None,
        **kwargs: Any) -> View:
        """Returns a subclass instance based on passed arguments.

        Args:
            project (framework.Project): related Project instance.
            name (Optional[str]): name or key to lookup the subclass.

        Returns:
            View: subclass instance based on passed arguments.
            
        """
        return cls(name = name,project = project, **kwargs) 
    