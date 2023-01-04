"""
base: essential classes for a chrisjen project
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
    Defaults
    Idea
    Resources
    Resource
    Project

To Do:

            
"""
from __future__ import annotations
import abc
from collections.abc import Hashable, Mapping, MutableMapping
import contextlib
import dataclasses
import pathlib
from typing import Any, ClassVar, Optional, Type
import warnings

import ashford
import bobbie
import camina
import holden

   
@dataclasses.dataclass
class Defaults(abc.ABC):
    """Default values and defaults for building a chrisjen project.
    
    Every attribute in Defaults should be a class attribute so that it is 
    accessible without instancing it (which it cannot be).

    Args:
        settings (ClassVar[dict[Hashable, dict[Hashable, Any]]]): default 
            settings for a chrisjen project's idea. 
        manager (ClassVar[str]): key name of the default manager. Defaults to 
            'publisher'.
        librarian (ClassVar[str]): key name of the default librarian. Defaults 
            to 'as_needed'.
        task (ClassVar[str]): key name of the default task design. Defaults to 
            'technique'.
        workflow (ClassVar[str]): key name of the default worker design. 
            Defaults to 'waterfall'.
        null_nodes (ClassVar[list[Any]]): lists of key names that indicate a 
            null node should be used. Defaults to ['none', 'None', None].   
        
    """
    settings: ClassVar[dict[Hashable, dict[Hashable, Any]]] = {
        'general': {
            'verbose': False,
            'parallelize': False,
            'efficiency': 'up_front'},
        'files': {
            'file_encoding': 'windows-1252',
            'threads': -1}}
    manager: ClassVar[str] = 'publisher'
    librarian: ClassVar[str] = 'up_front'
    superviser: ClassVar[str] = 'copier'
    task: ClassVar[str] = 'technique'
    workflow: ClassVar[str] = 'waterfall'
    null_nodes: ClassVar[list[Any]] = ['none', 'None', None]
 

@dataclasses.dataclass
class Idea(bobbie.Settings): 
    """Loads and stores configuration settings.

    To create an Idea instance, a user can pass as the 'contents' parameter a:
        1) pathlib file path of a compatible file type;
        2) string containing a a file path to a compatible file type;
                                or,
        3) 2-level nested dict.
To tip things off, let's look back at the first Fantasy Draft from October
    If 'contents' is imported from a file, Idea creates a dict and can convert 
    the dict values to appropriate datatypes. Currently, supported file types 
    are: ini, json, toml, yaml, and python. If you want to use toml, yaml, 
    or json, the identically named packages must be available in your python
    environment.

    If 'infer_types' is set to True (the default option), str dict values are 
    automatically converted to appropriate datatypes (str, list, float, bool, 
    and int are currently supported). Type conversion is automatically disabled
    if the source file is a python module (assuming the user has properly set
    the types of the stored python dict).

    Because Idea uses ConfigParser for .ini files, by default it stores 
    a 2-level dict. The desire for accessibility and simplicity dictated this 
    limitation. A greater number of levels can be achieved by having separate
    sections with names corresponding to the strings in the values of items in 
    other sections. 

    Args:
        contents (MutableMapping[Hashable, Any]): a dict for storing 
            configuration options. Defaults to en empty dict.
        default_factory (Optional[Any]): default value to return when the 'get' 
            method is used. Defaults to an empty camina.Dictionary.
        defaults (Optional[Mapping[str, Mapping[str]]]): any default options 
            that should be used when a user does not provide the corresponding 
            options in their configuration settings. Defaults to an empty dict.
        infer_types (Optional[bool]): whether values in 'contents' are converted 
            to other datatypes (True) or left alone (False). If 'contents' was 
            imported from an .ini file, all values will be strings. Defaults to 
            True.
        parsers (Optional[MutableMapping[Hashable, extensions.Parser]]): keys 
            are str names of Parser instances and the values are Parser 
            instances. The keys will be used as attribute names when the 'parse'
            method is automatically called if 'parsers' is not None. Defaults to 
            None.

    """
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    default_factory: Optional[Any] = camina.Dictionary
    defaults: Optional[Mapping[Hashable, Any]] = dataclasses.field(
        default_factory = dict)
    infer_types: Optional[bool] = True
    parsers: Optional[bobbie.Parsers] = None


@dataclasses.dataclass
class Resources(ashford.Keystones, abc.ABC):
    """Stores Resource subclasses.
    
    For each Resource, a class attribute is added with the snakecase name of 
    that Resource. In that class attribute, a dict-like object (determined by
    'default_factory') is the value and it stores all Resource subclasses of 
    that type (again using snakecase names as keys).
    
    Attributes:
        bases (ClassVar[camina.Dictionary]): dictionary of all direct Resource 
            subclasses. Keys are snakecase names of the Resource subclass and
            values are the base Resource subclasses.
        defaults (ClassVar[camina.Dictionary]): dictionary of the default class
            for each of the Resource subclasses. Keys are snakecase names of the
            base type and values are Resource subclasses.
        default_factory (ClassVar[Type[MutableMapping]]): dict-like class used
            to store Resource subclasses. Defaults to camina.Dictionary.
        All direct Resource subclasses will have an attribute name added
        dynamically.
        
    """
    bases: ClassVar[camina.Dictionary] = camina.Dictionary()
    defaults: ClassVar[camina.Dictionary] = camina.Dictionary()
    default_factory: ClassVar[Type[MutableMapping]] = camina.Dictionary
   
         
@dataclasses.dataclass
class Resource(ashford.Keystone, abc.ABC):    
    """Mixin for core package base classes.
    
    Attributes:
        library (ClassVar[Type[Team]]: library where Resource subclasses are 
            stored.
            
    """

    """ Initialization Methods """
    
    @classmethod
    def __init_subclass__(cls, *args: Any, **kwargs: Any):
        """Automatically registers subclass in Keystones."""
        # Because Keystone will be used as a mixin, it is important to call 
        # other base class '__init_subclass__' methods, if they exist.
        with contextlib.suppress(AttributeError):
            super().__init_subclass__(*args, **kwargs) # type: ignore
        if Resource in cls.__bases__:
            Resources.add(item = cls)
        else:
            Resources.register(item = cls)
            
    # """ Dunder Methods """
    
    # def __get__(self, obj: object, objtype: Type[Any] = None) -> Any:
    #     """Getter for use as a descriptor.

    #     Args:
    #         obj (object): the object which has a Parser instance as a 
    #             descriptor.

    #     Returns:
    #         Any: stored value(s).
            
    #     """
    #     try:
    #         settings = obj.settings
    #     except AttributeError:
    #         settings = obj
    #     return parsers.parse(settings = settings, parser = self)

    # def __set__(self, obj: object, value: Any) -> None:
    #     """Setter for use as a descriptor.

    #     Args:
    #         obj (object): the object which has a Parser instance as a 
    #             descriptor.
    #         value (Any): the value to assign when accessed.
            
    #     """
    #     try:
    #         settings = obj.settings
    #     except AttributeError:
    #         settings = obj
    #     keys = parsers.get_keys(
    #         settings = settings,
    #         terms = self.terms,
    #         scope = 'all',
    #         excise = False)
    #     try:
    #         key = keys[0]
    #     except IndexError:
    #         key = self.terms[0]
    #     settings[key] = value
    #     return

    # def __set_name__(self, owner: Type[Any], name: str) -> None:
    #     """Stores the attribute name in 'owner' of the Parser descriptor.

    #     Args:
    #         owner (Type[Any]): the class which has a Parser instance as a 
    #             descriptor.
    #         name (str): the str name of the descriptor.
            
    #     """
    #     self.name = name
    #     return

            
@dataclasses.dataclass
class Project(object):
    """User interface for a chrisjen project.
    
    Args:
        name (Optional[str]): designates the name of a class instance that is 
            used for internal referencing throughout chrisjen. Defaults to None. 
        idea (Optional[Resource]): configuration settings for the project. 
            Defaults to None.
        manager (Optional[Resource]): constructor for a chrisjen project. 
            Defaults to None.
        identification (Optional[str]): a unique identification name for a 
            chrisjen project. The name is primarily used for creating file 
            folders related to the project. If it is None, a str will be created 
            from 'name' and the date and time. This prevents files from one 
            project from overwriting another. Defaults to None. 
        automatic (bool): whether to automatically iterate through the project
            stages (True) or whether it must be iterating manually (False). 
            Defaults to True.
            
    Attributes:
        defaults (ClassVar[Defaults]): a class storing the default project 
            options. Defaults to Defaults.
        library (ClassVar[Team]): library of nodes for executing a
            chrisjen project. Defaults to an instance of ProjectLibrary.
 
    """
    name: Optional[str] = None
    idea: Optional[Idea] = dataclasses.field(
        default = None, repr = False)
    workflow: Optional[holden.Composite] = dataclasses.field(
        default = None)
    resources: Optional[Type[Resources]] = dataclasses.field(
        default = Resources, repr = False)
    identification: Optional[str] = dataclasses.field(
        default = None, compare = False)
    automatic: Optional[bool] = dataclasses.field(
        default = True, compare = False)
    manager: Optional[Type[Resource] | Resource] = None
    defaults: ClassVar[Type[Defaults]] = Defaults
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes and validates an instance."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Calls parent and/or mixin initialization method(s).
        with contextlib.suppress(AttributeError):
            super().__post_init__()
        self = Resources.validate(
            item = self, 
            attribute = 'manager',
            parameters = {'project': self})
       
    """ Public Class Methods """

    @classmethod
    def create(
        cls, 
        idea: pathlib.Path | str | Idea,
        **kwargs) -> Project:
        """Returns a Project instance based on 'idea' and kwargs.

        Args:
            idea (pathlib.Path | str | Idea): a path to a file 
                containing configuration settings, a python dict, or an Idea 
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

