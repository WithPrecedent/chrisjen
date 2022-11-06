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
    ProjectRules
    ProjectKeystones
    ProjectKeystone
    ProjectLibrary
    Project
    set_parallelization

To Do:

            
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, MutableMapping
import contextlib
import dataclasses
import inspect
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING
import warnings

import amos
import bobbie
import holden


@dataclasses.dataclass
class ProjectRules(abc.ABC):
    """Default values and classes for a chrisjen project.
    
    Every attribute in ProjectRules should be a class attribute so that it
    is accessible without instancing it (which it cannot be).

    Args:
        default_settings (ClassVar[dict[Hashable, dict[Hashable, Any]]]):
            default settings for a chrisjen project's idea. Defaults to the
            values in the dataclass field.
        parsers (ClassVar[dict[str, tuple[str]]]): keys are the names of
            special categories of settings and values are tuples of suffixes or
            whole words that are associated with those special categories in
            user settings. Defaults to the dict in the dataclass field.
        default_manager (ClassVar[str]): key name of the default manager.
            Defaults to 'publisher'.
        default_librarian (ClassVar[str]): key name of the default librarian.
            Defaults to 'as_needed'.
        default_worker (ClassVar[str]): key name of the default worker design.
            Defaults to 'waterfall'.
        default_task (ClassVar[str]): key name of the default task design.
            Defaults to 'technique'
        null_names (ClassVar[list[Any]]): lists of key names that indicate a
            null node should be used. Defaults to ['none', 'None', None].
        keystones (ClassVar[amos.Catalog[str, ProjectKeystone]]): catalog of 
            ProjectKeystone instances. Defaults to an empty Catalog.        
        
    """
    parsers: ClassVar[dict[str, tuple[str]]] = {
        'criteria': ('criteria',),
        'design': ('design', 'structure'),
        'manager': ('manager', 'project'),
        'files': ('filer', 'files', 'clerk'),
        'general': ('general',),
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
    default_worker: ClassVar[str] = 'waterfall'
    null_names: ClassVar[list[Any]] = ['none', 'None', None]
    keystones: ClassVar[amos.Catalog] = amos.Catalog()


@dataclasses.dataclass
class ProjectKeystones(abc.ABC):
    """Stores ProjectKeystone subclasses.
    
    For each ProjectKeystone, a class attribute is added with the snakecase
    name of that ProjectKeystone. In that class attribute, an amos.Dictionary
    is the value and it stores all ProjectKeystone subclasses of that type
    (again using snakecase names as keys).
    
    Attributes:
        bases (ClassVar[amos.Dictionary]): dictionary of all direct 
            ProjectKeystone subclasses. Keys are snakecase names of the
            ProjectKeystone subclass.
        All direct ProjectKeystone subclasses will have an attribute name added
        dynamically.
        
    """
    bases: ClassVar[amos.Dictionary] = amos.Dictionary()
        
    """ Public Methods """
    
    @classmethod
    def add(cls, item: Type[ProjectKeystone]) -> None:
        """Adds a new keystone attribute with an empty dictionary.

        Args:
            item (Type[ProjectKeystone]): direct ProjectKeystone subclass from
                which the name of a new attribute should be derived.
            
        """
        name = cls._get_name(item = item)
        cls.bases[name] = item
        setattr(cls, name, amos.Dictionary())
        return
    
    @classmethod
    def classify(cls, item: str | Type[ProjectKeystone]) ->str:
        """Returns the str name of the ProjectKeystone of which 'item' is.

        Args:
            item (str | Type[ProjectKeystone]): ProjectKeystone subclass or its
                str name to return the str name of its base type.

        Raises:
            ValueError: if 'item' does not match a subclass of any 
                ProjectKeystone type.
            
        Returns:
            str: snakecase str name of the ProjectKeystone base type of which 
                'item' is a subclass.
                
        """
        if isinstance(item, str):
            for key in cls.bases.keys():
                subtype_dict = getattr(cls, key)
                for name in subtype_dict.keys():
                    if item == name:
                        return key
        else:
            for key, value in cls.bases.items():
                if issubclass(item, value):
                    return key
        raise ValueError(f'{item} is not a subclass of any ProjectKeystone')
              
    @classmethod
    def register(
        cls, 
        item: Type[ProjectKeystone] | ProjectKeystone,
        name: Optional[str] = None) -> None:
        """Registers 'item' in the appropriate class attribute registry.
        
        Args:
            item (Type[ProjectKeystone] | ProjectKeystone): ProjectKeystone 
                subclass or subclass instance to store.
            name (Optional[str], optional): key name to use in storing 'item'. 
                Defaults to None.
            
        """
        name = cls._get_name(item = item, name = name)
        keystone = cls.classify(item = item)
        getattr(cls, keystone)[name] = item
        return

    @classmethod
    def validate(cls, item: object, attribute: str) -> object:
        """Creates or validates 'attribute' in 'item'.

        Args:
            item (object): object (often a Project or Manager instance) of which
                a ProjectKeystone in 'attribute' needs to be validated or 
                created. If 'item' is not a Project instance, it must have a
                'project' attribute containing a Project instance.
            attribute (str): name of the attribute' in item containing a value
                to be validated or which provides information to create an
                appropriate instance.

        Raises:
            ValueError: if the value of 'attribute' in 'item' does match any
                known subclass or subclass instance of that ProjectKeystone
                subtype.

        Returns:
            object: completed, linked instance.
            
        """       
        # Finds Project instance to pass or add to instance.
        if isinstance(item, Project):
            project = item
        else:
            project = getattr(item, 'project')
        # Get current value of the relevant attribute and corresponding base 
        # class.
        value = getattr(item, attribute)
        base = cls.bases[attribute]
        # Adds link to 'project' if 'value' is already an instance of the 
        # appropriate base type.
        if isinstance(value, base):
            setattr(value, 'project', project)
        else:
            # Gets the relevant registry for 'attribute'.
            registry = getattr(cls, attribute)
            # Selects default name of class if none exists.
            if getattr(item, attribute) is None:
                name = getattr(ProjectRules, f'default_{attribute}')
                setattr(item, attribute, registry[name])
            # Uses str value to select appropriate subclass.
            elif isinstance(getattr(item, attribute), str):
                name = getattr(item, attribute)
                setattr(item, attribute, registry[name])
            # Gets name of class if it is already an appropriate subclass.
            elif inspect.issubclass(value, base):
                name = amos.namify(item = getattr(item, attribute))
            else:
                raise ValueError(f'{value} is not an appropriate keystone')
            # Creates a subclass instance.
            instance = getattr(item, attribute).create(
                name = name, 
                project = project)
            setattr(item, attribute, instance)
        return            

    """ Private Methods """
    
    @classmethod
    def _get_name(
        cls, 
        item: Type[ProjectKeystone],
        name: Optional[str] = None) -> None:
        """Returns 'name' or str name of item.
        
        By default, the method uses amos.namify to create a snakecase name. If
        the resultant name begins with 'project_', that substring is removed. 

        If you want to use another naming convention, just subclass and override
        this method. All other methods will call this method for naming.
        
        Args:
            item (Type[ProjectKeystone]): item to name.
            name (Optional[str], optional): optional name to use. A 'project_'
                prefix will be removed, if it exists. Defaults to None.

        Returns:
            str: name of 'item' or 'name' (with the 'project' prefix removed).
            
        """
        name = name or amos.namify(item = item)
        if name.startswith('project_'):
            name = name[8:]
        return name        
            
         
@dataclasses.dataclass
class ProjectKeystone(abc.ABC):
    """Mixin for core project base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in ProjectKeystones."""
        # Because ProjectKeystone will be used as a mixin, it is important to 
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if ProjectKeystone in cls.__bases__:
            ProjectKeystones.add(item = cls)
        else:
            ProjectKeystones.register(item = cls)
            
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(
        cls, 
        project: Project,
        name: Optional[str] = None,
        **kwargs: Any) -> ProjectKeystone:
        """Returns a subclass instance based on passed arguments.

        The reason for requiring a 'create' classmethod is that it allows for
        classes to gather information from 'project' needed for the instance,
        but not to necessarily maintain a permanent link to a Project instance.
        This facilitates loose coupling and easier serialization of project
        workflows without complex interdependence.
        
        Args:
            project (Project): related Project instance.
            name (Optional[str]): name or key to lookup a subclass.

        Returns:
            ProjectKeystone: subclass instance based on passed arguments.
            
        """
        pass 

         
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        idea (Optional[ProjectKeystone]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[ProjectKeystone]): a filing clerk for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        manager (Optional[ProjectKeystone]): constructor for a chrisjen 
            project. Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None. 
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
        rules (Optional[Type[ProjectRules]]): a class storing the default
            project options. Defaults to ProjectRules.
        library (ClassVar[ProjectKeystones]): library of nodes for executing a
            chrisjen project. Defaults to an instance of ProjectLibrary.
 
    """
    name: Optional[str] = None
    idea: Optional[bobbie.Settings] = None 
    manager: Optional[ProjectKeystone] = None
    identification: Optional[str] = None
    automatic: Optional[bool] = True
    rules: Optional[Type[ProjectRules]] = ProjectRules
    library: ClassVar[ProjectKeystones] = ProjectKeystones
        
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self = ProjectKeystones.validate(item = self, attribute = 'manager')
       
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
