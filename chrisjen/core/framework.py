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
from collections.abc import Hashable, MutableMapping
import contextlib
import dataclasses
import inspect
import pathlib
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING
import warnings

import camina
import bobbie
import holden
import miller


@dataclasses.dataclass
class Rules(abc.ABC):
    """Default values and classes for a chrisjen project.
    
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
        null_names (ClassVar[list[Any]]): lists of key names that indicate a
            null node should be used. Defaults to ['none', 'None', None].   
        
    """
    parsers: ClassVar[dict[str, tuple[str]]] = {
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
    null_names: ClassVar[list[Any]] = ['none', 'None', None]


@dataclasses.dataclass
class Keystones(abc.ABC):
    """Stores Keystone subclasses.
    
    For each Keystone, a class attribute is added with the snakecase
    name of that Keystone. In that class attribute, an camina.Dictionary
    is the value and it stores all Keystone subclasses of that type
    (again using snakecase names as keys).
    
    Attributes:
        bases (ClassVar[camina.Dictionary]): dictionary of all direct 
            Keystone subclasses. Keys are snakecase names of the
            Keystone subclass.
        All direct Keystone subclasses will have an attribute name added
        dynamically.
        
    """
    bases: ClassVar[camina.Dictionary] = camina.Dictionary()
        
    """ Public Methods """
    
    @classmethod
    def add(cls, item: Type[Keystone]) -> None:
        """Adds a new keystone attribute with an empty dictionary.

        Args:
            item (Type[Keystone]): direct Keystone subclass from which the name 
                of a new attribute should be derived.
            
        """
        name = cls._get_name(item = item)
        cls.bases[name] = item
        setattr(cls, name, camina.Dictionary())
        return
    
    @classmethod
    def classify(cls, item: str | Type[Keystone] | Keystone) ->str:
        """Returns the str name of the Keystone of which 'item' is.

        Args:
            item (str | Type[Keystone] | Keystone): Keystone subclass, subclass
                instance, or its str name.

        Raises:
            ValueError: if 'item' does not match a subclass of any Keystone 
                type.
            
        Returns:
            str: snakecase str name of the Keystone base type of which 'item' is 
                a subclass or subclass instance.
                
        """
        if isinstance(item, str):
            for key in cls.bases.keys():
                subtype_dict = getattr(cls, key)
                for name in subtype_dict.keys():
                    if item == name:
                        return key
        else:
            if not inspect.isclass(item):
                item = item.__class__
            for key, value in cls.bases.items():
                if issubclass(item, value):
                    return key
        raise ValueError(f'{item} is not a subclass of any Keystone')
              
    @classmethod
    def register(
        cls, 
        item: Type[Keystone] | Keystone,
        name: Optional[str] = None) -> None:
        """Registers 'item' in the appropriate class attribute registry.
        
        Args:
            item (Type[Keystone] | Keystone): Keystone 
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
                a Keystone in 'attribute' needs to be validated or 
                created. If 'item' is not a Project instance, it must have a
                'project' attribute containing a Project instance.
            attribute (str): name of the attribute' in item containing a value
                to be validated or which provides information to create an
                appropriate instance.

        Raises:
            ValueError: if the value of 'attribute' in 'item' does match any
                known subclass or subclass instance of that Keystone
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
        if (isinstance(value, base) 
            and miller.has_attributes(item = base, attributes = ['project'])):
            setattr(value, 'project', project)
        else:
            # Gets the relevant registry for 'attribute'.
            registry = getattr(cls, attribute)
            # Selects default name of class if none exists.
            if getattr(item, attribute) is None:
                name = getattr(Rules, f'default_{attribute}')
                setattr(item, attribute, registry[name])
            # Uses str value to select appropriate subclass.
            elif isinstance(getattr(item, attribute), str):
                name = getattr(item, attribute)
                setattr(item, attribute, registry[name])
            # Gets name of class if it is already an appropriate subclass.
            elif inspect.issubclass(value, base):
                name = camina.namify(item = getattr(item, attribute))
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
        item: Type[Keystone],
        name: Optional[str] = None) -> None:
        """Returns 'name' or str name of item.
        
        By default, the method uses camina.namify to create a snakecase name. If
        the resultant name begins with 'project_', that substring is removed. 

        If you want to use another naming convention, just subclass and override
        this method. All other methods will call this method for naming.
        
        Args:
            item (Type[Keystone]): item to name.
            name (Optional[str], optional): optional name to use. A 'project_'
                prefix will be removed, if it exists. Defaults to None.

        Returns:
            str: name of 'item' or 'name' (with the 'project' prefix removed).
            
        """
        name = name or camina.namify(item = item)
        if name.startswith('project_'):
            name = name[8:]
        return name        
            
         
@dataclasses.dataclass
class Keystone(abc.ABC):
    """Mixin for core project base classes."""

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in Keystones."""
        # Because Keystone will be used as a mixin, it is important to 
        # call other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if Keystone in cls.__bases__:
            Keystones.add(item = cls)
        else:
            Keystones.register(item = cls)
            
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def create(
        cls, 
        project: Project,
        name: Optional[str] = None,
        **kwargs: Any) -> Keystone:
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
            Keystone: subclass instance based on passed arguments.
            
        """
        pass 

         
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        idea (Optional[Keystone]): configuration settings for the 
            project. Defaults to None.
        clerk (Optional[Keystone]): a filing clerk for loading and saving 
            files throughout a chrisjen project. Defaults to None.
        manager (Optional[Keystone]): constructor for a chrisjen 
            project. Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None. 
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
        rules (Optional[Type[Rules]]): a class storing the default
            project options. Defaults to Rules.
        library (ClassVar[Keystones]): library of nodes for executing a
            chrisjen project. Defaults to an instance of ProjectLibrary.
 
    """
    name: Optional[str] = None
    idea: Optional[bobbie.Settings] = None 
    manager: Optional[Keystone] = None
    identification: Optional[str] = None
    automatic: Optional[bool] = True
    rules: Optional[Type[Rules]] = Rules
    library: ClassVar[Keystones] = Keystones
        
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
