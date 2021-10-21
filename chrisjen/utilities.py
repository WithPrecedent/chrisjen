"""
utilities: shared helper functions
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2021, Corey Rayburn Yung
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
    adjacency_to_edges (Callable): converts adjacency list to edge list.
    adjacency_to_matrix (Callable): converts adjacency list to adjacency matrix.
    edges_to_adjacency (Callable): converts edge list to an adjacency list.
    matrix_to_adjacency (Callable): converts adjacency matrix to an adjacency 
        list.
    pipeline_to_adjacency (Callable): converts pipeline to an adjacency list.
        
"""
from __future__ import annotations
import abc
import ast
import collections
from collections.abc import (
    Container, Hashable, Iterable, Mapping, MutableSequence, Sequence, Set,
    Iterable, MutableMapping)
import dataclasses
import functools
import importlib
import inspect
import pathlib
import re
import types
from typing import Any, Callable, ClassVar, Optional, Type, Union

import more_itertools

# Simpler alias for generic callable.
Operation = Callable[..., Any]
# Shorter alias for things that can be wrapped.
Wrappable = Union[Type[Any], Operation]
# Abbreviated alias for a dict of inspect.Signature types.
Signatures = MutableMapping[str, inspect.Signature]
# Alias for dict of Type[Any] types.
Types = MutableMapping[str, Type[Any]]

def drop_dunders(item: list[Any]) -> list[Any]:
    """Drops items in 'item' with names beginning with an underscore.

    Args:
        item (list[Any]): attributes, methods, and properties of a class.

    Returns:
        list[Any]: attributes, methods, and properties that do not start with an
            underscore.
        
    """
    if len(item) > 0 and hasattr(item[0], '__name__'):
        return [
            i for i in item 
            if not i.__name__.startswith('__') 
            and not i.__name__.endswith('__')]
    else:
        return [
            i for i in item if not i.startswith('__') and not i.endswith('__')]
    
def drop_privates(item: list[Any]) -> list[Any]:
    """Drops items in 'item' with names beginning with an underscore.

    Args:
        item (list[Any]): attributes, methods, and properties of a class.

    Returns:
        list[Any]: attributes, methods, and properties that do not start with an
            underscore.
        
    """
    if len(item) > 0 and hasattr(item[0], '__name__'):
        return [i for i in item if not i.__name__.startswith('_')]
    else:
        return [i for i in item if not i.startswith('_')]

def from_file_path(
    path: Union[pathlib.Path, str], 
    name: Optional[str] = None) -> types.ModuleType:
    """Imports and returns module from file path at 'name'.

    Args:
        path (Union[pathlib.Path, str]): file path of module to load.
        name (Optional[str]): name to store module at in 'sys.modules'. If it
            is None, the stem of 'path' is used. Defaults to None.
    Returns:
        types.ModuleType: imported module.
        
    """
    path = pathlibify(item = path)
    if name is None:
        name = path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None:
        raise ImportError(f'Failed to create spec from {path}')
    else:
        imported = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(imported)
        return imported
                  
def iterify(item: Any) -> Iterable:
    """Returns 'item' as an iterable, but does not iterate str types.
    
    Args:
        item (Any): item to turn into an iterable

    Returns:
        Iterable: of 'item'. A str type will be stored as a single item in an
            Iterable wrapper.
        
    """     
    if item is None:
        return iter(())
    elif isinstance(item, (str, bytes)):
        return iter([item])
    else:
        try:
            return iter(item)
        except TypeError:
            return iter((item,))
        
def pathlibify(item: Union[str, pathlib.Path]) -> pathlib.Path:
    """Converts string 'path' to pathlib.Path object.

    Args:
        item (Union[str, pathlib.Path]): either a string summary of a
            path or a pathlib.Path object.

    Returns:
        pathlib.Path object.

    Raises:
        TypeError if 'path' is neither a str or pathlib.Path type.

    """
    if isinstance(item, str):
        return pathlib.Path(item)
    elif isinstance(item, pathlib.Path):
        return item
    else:
        raise TypeError('item must be str or pathlib.Path type')
    
def snakify(item: str) -> str:
    """Converts a capitalized str to snake case.

    Args:
        item (str): str to convert.

    Returns:
        str: 'item' converted to snake case.

    """
    item = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', item)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', item).lower()    

@functools.singledispatch
def contains(
    item: object,
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether 'item' contains the type(s) in 'contents'.

    Args:
        item (object): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    raise TypeError(f'item {item} is not supported by {__name__}')

@contains.register(Mapping)    
def dict_contains(
    item: Mapping[Hashable, Any], 
    contents: tuple[Union[Type[Any], tuple[Type[Any], ...]],
                    Union[Type[Any], tuple[Type[Any], ...]]]) -> bool:
    """Returns whether dict 'item' contains the type(s) in 'contents'.

    Args:
        item (Mapping[Hashable, Any]): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    return (
        serial_contains(item = item.keys(), contents = contents[0])
        and serial_contains(item = item.values(), contents = contents[1]))

@contains.register(MutableSequence)   
def list_contains(
    item: MutableSequence[Any],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether list 'item' contains the type(s) in 'contents'.

    Args:
        item (MutableSequence[Any]): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    return serial_contains(item = item, contents = contents)

@contains.register(Set)   
def set_contains(
    item: Set[Any],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether list 'item' contains the type(s) in 'contents'.

    Args:
        item (Set[Any]): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    return serial_contains(item = item, contents = contents)

@contains.register(tuple)   
def tuple_contains(
    item: tuple[Any, ...],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether tuple 'item' contains the type(s) in 'contents'.

    Args:
        item (tuple[Any, ...]): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    if isinstance(contents, tuple) and len(item) == len(contents):
        technique = parallel_contains
    else:
        technique = serial_contains
    return technique(item = item, contents = contents)

@contains.register(Sequence)   
def parallel_contains(
    item: Sequence[Any],
    contents: tuple[Type[Any], ...]) -> bool:
    """Returns whether parallel 'item' contains the type(s) in 'contents'.

    Args:
        item (Sequence[Any]): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    return all(isinstance(item[i], contents[i]) for i in enumerate(item))

@contains.register(Container)       
def serial_contains(
    item: Container[Any],
    contents: Union[Type[Any], tuple[Type[Any], ...]]) -> bool:
    """Returns whether serial 'item' contains the type(s) in 'contents'.

    Args:
        item (Collection[Any]): item to examine.
        contents (Union[Type[Any], tuple[Type[Any], ...]]): types to check for
            in 'item' contents.

    Returns:
        bool: whether 'item' holds the types in 'contents'.
        
    """
    return all(isinstance(i, contents) for i in item)
         
def get_annotations(
    item: object, 
    include_private: bool = False) -> dict[str, Type[Any]]:
    """Returns dict of attributes of 'item' with type annotations.
    
    Args:
        item (object): instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        dict[str, Any]: dict of attributes in 'item' (keys are attribute names 
            and values are type annotations) that are type annotated.
            
    """
    annotations = item.__annotations__
    if include_private:
        return annotations
    else:
        return {k: v for k, v in annotations.items() if not k.startswith('_')}

def get_attributes(
    item: object, 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> dict[str, Any]:
    """Returns dict of attributes of 'item'.
    
    Args:
        item (Any): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
                        
    Returns:
        dict[str, Any]: dict of attributes in 'item' (keys are attribute names 
            and values are attribute values).
            
    """
    exclude = exclude or []
    attributes = name_attributes(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    values = [getattr(item, m) for m in attributes]
    return dict(zip(attributes, values))

def get_methods(
    item: Union[object, Type[Any]], 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> dict[str, types.MethodType]:
    """Returns dict of methods of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
               
    Returns:
        dict[str, types.MethodType]: dict of methods in 'item' (keys are method 
            names and values are methods).
        
    """ 
    exclude = exclude or []
    methods = name_methods(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    return [getattr(item, m) for m in methods]

def get_name(item: Any, default: Optional[str] = None) -> Optional[str]:
    """Returns str name representation of 'item'.
    
    Args:
        item (Any): item to determine a str name.
        default(Optional[str]): default name to return if other methods at name
            creation fail.

    Returns:
        str: a name representation of 'item.'
        
    """        
    if isinstance(item, str):
        return item
    else:
        if hasattr(item, 'name') and isinstance(item.name, str):
            return item.name
        else:
            try:
                return snakify(item.__name__) # type: ignore
            except AttributeError:
                if item.__class__.__name__ is not None:
                    return snakify( # type: ignore
                        item.__class__.__name__) 
                else:
                    return default

def get_properties(
    item: object, 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> dict[str, Any]:
    """Returns properties of 'item'.

    Args:
        item (object): instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
               
    Returns:
        dict[str, Any]: dict of properties in 'item' (keys are property names 
            and values are property values).
        
    """ 
    exclude = exclude or []   
    properties = name_properties(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    values = [getattr(item, p) for p in properties]
    return dict(zip(properties, values))

def get_signatures(
    item: Union[object, Type[Any]], 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> dict[str, inspect.Signature]:
    """Returns dict of method signatures of 'item'.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
               
    Returns:
        dict[str, inspect.Signature]: dict of method signatures in 'item' (keys 
            are method names and values are method signatures).
                   
    """ 
    exclude = exclude or []
    methods = name_methods(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    signatures = [inspect.signature(getattr(item, m)) for m in methods]
    return dict(zip(methods, signatures))

def get_variables(
    item: object, 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> dict[str, Any]:
    """Returns dict of attributes of 'item' that are not methods or properties.
    
    Args:
        item (object): instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
         exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
                                      
    Returns:
        dict[str, Any]: dict of attributes in 'item' (keys are attribute names 
            and values are attribute values) that are not methods or properties.
            
    """
    exclude = exclude or []
    attributes = name_attributes(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    methods = name_methods(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    properties = name_properties(
        item = item, 
        include_private = include_private,
        exclude = exclude)
    variables = [
        a for a in attributes if a not in methods and a not in properties]
    values = [getattr(item, m) for m in variables]
    return dict(zip(variables, values))

def has_attributes(
    item: Union[object, Type[Any]], 
    attributes: MutableSequence[str]) -> bool:
    """Returns whether 'attributes' exist in 'item'.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        attributes (MutableSequence[str]): names of attributes to check to see
            if they exist in 'item'.
            
    Returns:
        bool: whether all 'attributes' exist in 'items'.
    
    """
    return all(hasattr(item, a) for a in attributes)

def has_methods(
    item: Union[object, Type[Any]], 
    methods: Union[str, MutableSequence[str]]) -> bool:
    """Returns whether 'item' has 'methods' which are methods.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        methods (Union[str, MutableSequence[str]]): name(s) of methods to check 
            to see if they exist in 'item' and are types.MethodType.
            
    Returns:
        bool: whether all 'methods' exist in 'items' and are types.MethodType.
        
    """
    methods = list(iterify(methods))
    return all(is_method(item = item, attribute = m) for m in methods)

def has_properties(
    item: Union[object, Type[Any]], 
    properties: Union[str, MutableSequence[str]]) -> bool:
    """Returns whether 'item' has 'properties' which are properties.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        properties (MutableSequence[str]): names of properties to check to see 
            if they exist in 'item' and are property type.
            
    Returns:
        bool: whether all 'properties' exist in 'items'.
        
    """
    properties = list(iterify(properties))
    return all(is_property(item = item, attribute = p) for p in properties)

def has_signatures(
    item: Union[object, Type[Any]], 
    signatures: Mapping[str, inspect.Signature]) -> bool:
    """Returns whether 'item' has 'signatures' of its methods.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        signatures (Mapping[str, inspect.Signature]): keys are the names of 
            methods and values are the corresponding method signatures.
            
    Returns:
        bool: whether all 'signatures' exist in 'items'.
        
    """
    item_signatures = get_signatures(item = item, include_private = True)
    pass_test = True
    for name, parameters in signatures.items():
        if (name not in item_signatures or item_signatures[name] != parameters):
            pass_test = False
    return pass_test
    
def has_traits(
    item: Union[object, Type[Any]],
    attributes: Optional[MutableSequence[str]] = None,
    methods: Optional[MutableSequence[str]] = None,
    properties: Optional[MutableSequence[str]] = None,
    signatures: Optional[Mapping[str, inspect.Signature]] = None) -> bool:
    """Returns if 'item' has 'attributes', 'methods' and 'properties'.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        attributes (MutableSequence[str]): names of attributes to check to see
            if they exist in 'item'.
        methods (MutableSequence[str]): name(s) of methods to check to see if 
            they exist in 'item' and are types.MethodType.          
        properties (MutableSequence[str]): names of properties to check to see 
            if they exist in 'item' and are property type.
        signatures (Mapping[str, inspect.Signature]): keys are the names of 
            methods and values are the corresponding method signatures.
                          
    Returns:
        bool: whether all passed arguments exist in 'items'.    
    
    """
    if not inspect.isclass(item):
        item = item.__class__ 
    attributes = attributes or []
    methods = methods or []
    properties = properties or []
    signatures = signatures or {}
    return (
        has_attributes(item = item, attributes = attributes)
        and has_methods(item = item, methods = methods)
        and has_properties(item = item, properties = properties)
        and has_signatures(item = item, signatures = signatures))
    
@functools.singledispatch
def has_types(item: object) -> Optional[Union[
    tuple[Type[Any], ...], 
    tuple[tuple[Type[Any], ...], tuple[Type[Any], ...]]]]:
    """Returns types contained in 'item'.

    Args:
        item (object): item to examine.
    
    Returns:
        Optional[Union[tuple[Type[Any], ...], tuple[tuple[Type[Any], ...], 
            tuple[Type[Any], ...]]]]:: returns the types of things contained 
            in 'item'. Returns None if 'item' is not a container.
        
    """
    raise TypeError(f'item {item} is not supported by {__name__}')

@has_types.register(Mapping)  
def has_types_dict(
    item: Mapping[Hashable, Any]) -> Optional[
        tuple[tuple[Type[Any], ...], tuple[Type[Any], ...]]]:
    """Returns types contained in 'item'.

    Args:
        item (object): item to examine.
    
    Returns:
        Optional[tuple[Type[Any], ...]]: returns the types of things contained 
            in 'item'. Returns None if 'item' is not a container.
        
    """
    if isinstance(item, Mapping):
        key_types = has_types_sequence(item = item.keys())
        value_types = has_types_sequence(item = item.values())
        return tuple([key_types, value_types])
    else:
        return None

@has_types.register(MutableSequence)  
def has_types_list(item: list[Any]) -> Optional[tuple[Type[Any], ...]]:
    """Returns types contained in 'item'.

    Args:
        item (list[Any]): item to examine.
    
    Returns:
        Optional[tuple[Type[Any], ...]]: returns the types of things contained 
            in 'item'. Returns None if 'item' is not a container.
        
    """
    if isinstance(item, list):
        key_types = has_types_sequence(item = item.keys())
        value_types = has_types_sequence(item = item.values())
        return tuple([key_types, value_types])
    else:
        return None

@has_types.register(Sequence)    
def has_types_sequence(item: Sequence[Any]) -> Optional[tuple[Type[Any], ...]]:
    """Returns types contained in 'item'.

    Args:
        item (Sequence[Any]): item to examine.
    
    Returns:
        Optional[tuple[Type[Any], ...]]: returns the types of things contained 
            in 'item'. Returns None if 'item' is not a container.
        
    """
    if isinstance(item, Sequence):
        all_types = []
        for thing in item:
            kind = type(thing)
            if not kind in all_types:
                all_types.append(kind)
        return tuple(all_types)
    else:
        return None
 
def is_class_attribute(item: Union[object, Type[Any]], attribute: str) -> bool:
    """Returns if 'attribute' is a class attribute of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    return (
        hasattr(item, attribute)
        and not is_method(item = item, attribute = attribute)
        and not is_property(item = item, attribute = attribute))
    
def is_container(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is a container and not a str.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        
    Returns:
        bool: if 'item' is a container but not a str.
        
    """  
    if not inspect.isclass(item):
        item = item.__class__ 
    return issubclass(item, Container) and not issubclass(item, str)

def is_function(item: Union[object, Type[Any]], attribute: Any) -> bool:
    """Returns if 'attribute' is a function of 'item'."""
    if isinstance(attribute, str):
        try:
            attribute = getattr(item, attribute)
        except AttributeError:
            return False
    return isinstance(attribute, types.FunctionType)
   
def is_iterable(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is iterable and is NOT a str type.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        
    Returns:
        bool: if 'item' is iterable but not a str.
        
    """ 
    if not inspect.isclass(item):
        item = item.__class__ 
    return issubclass(item, Iterable) and not issubclass(item, str)
        
def is_method(item: Union[object, Type[Any]], attribute: Any) -> bool:
    """Returns if 'attribute' is a method of 'item'."""
    if isinstance(attribute, str):
        if (
            not hasattr(item, attribute) 
            or isinstance(getattr(item, attribute), property)):
            return False
    return (
        isinstance(item, (object, Type))
        and isinstance(attribute, types.FunctionType))

def is_nested(item: Mapping[Any, Any]) -> bool:
    """Returns if 'item' is nested at least one-level.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        
    Returns:
        bool: if 'item' is a nested mapping.
        
    """ 
    return (
        isinstance(item, Mapping) 
        and any(isinstance(v, Mapping) for v in item.values()))
 
def is_property(item: Union[object, Type[Any]], attribute: Any) -> bool:
    """Returns if 'attribute' is a property of 'item'."""
    if not inspect.isclass(item):
        item = item.__class__
    if isinstance(attribute, str):
        try:
            attribute = getattr(item, attribute)
        except AttributeError:
            return False
    return isinstance(attribute, property)

def is_sequence(item: Union[object, Type[Any]]) -> bool:
    """Returns if 'item' is a sequence and is NOT a str type.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        
    Returns:
        bool: if 'item' is a sequence but not a str.
        
    """ 
    if not inspect.isclass(item):
        item = item.__class__ 
    return issubclass(item, Sequence) and not issubclass(item, str) 

def is_variable(item: Union[object, Type[Any]], attribute: str) -> bool:
    """Returns if 'attribute' is a simple data attribute of 'item'.

    Args:
        item (Union[object, Type[Any]]): [description]
        attribute (str): [description]

    Returns:
        bool: [description]
        
    """
    return (
        hasattr(item, attribute)
        and not is_function(item = item, attribute = attribute)
        and not is_property(item = item, attribute = attribute))

def name_attributes(
    item: Union[object, Type[Any]], 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> list[str]:
    """Returns attribute names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
                                       
    Returns:
        list[str]: names of attributes in 'item'.
            
    """
    exclude = exclude or []
    names = [n for n in dir(item) if n not in exclude]
    if not include_private:
        names = drop_privates(item = names)
    return names

def name_methods(
    item: Union[object, Type[Any]], 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> list[str]:
    """Returns method names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
                                       
    Returns:
        list[str]: names of methods in 'item'.
            
    """
    exclude = exclude or []
    names = [n for n in dir(item) if n not in exclude]
    methods = [
        a for a in names
        # if isinstance(getattr(item, a), types.FunctionType)]
        if is_method(item = item, attribute = a)]
    if not include_private:
        methods = drop_privates(item = methods)
    return methods

def name_parameters(item: Type[Any]) -> list[str]:
    """Returns list of parameters based on annotations of 'item'.

    Args:
        item (Type[Any]): class to get parameters to.

    Returns:
        list[str]: names of parameters in 'item'.
        
    """          
    return list(item.__annotations__.keys())

def name_properties(
    item: Union[object, Type[Any]], 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> list[str]:
    """Returns method names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
                                       
    Returns:
        list[str]: names of properties in 'item'.
            
    """
    exclude = exclude or []
    if not inspect.isclass(item):
        item = item.__class__
    names = [n for n in dir(item) if n not in exclude]
    properties = [
        a for a in names
        if is_property(item = item, attribute = a)]
    if not include_private:
        properties = drop_privates(item = properties)
    return properties

def name_variables(
    item: Union[object, Type[Any]], 
    include_private: bool = False,
    exclude: Optional[Container[str]] = None) -> list[str]:
    """Returns variable names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
        exclude (Optional[Container[str]]): names of attributes to exclude.
            Defaults to None.
                                       
    Returns:
        list[str]: names of attributes in 'item' that are neither methods nor
            properties.
            
    """
    exclude = exclude or []
    names = [n for n in dir(item) if n not in exclude]
    names = [a for a in names if is_variable(item = item, attribute = a)]
    if not include_private:
        names = drop_privates(item = names)
    return names

def drop_prefix_from_str(item: str, prefix: str, divider: str = '') -> str:
    """Drops 'prefix' from 'item' with 'divider' in between.
    
    Args:
        item (str): item to be modified.
        prefix (str): prefix to be added to 'item'.
        divider (str): str to add between 'item' and 'prefix'. Defaults to '',
            which means no divider will be added.
 
    Returns:
        str: modified str.

    """
    prefix = ''.join([prefix, divider])
    if item.startswith(prefix):
        return item[len(prefix):]
    else:
        return item
 

@dataclasses.dataclass
class Registrar(object):
    
    registry: ClassVar[MutableMapping[str, Type[Any]]] = {}
    
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
        cls.register(item = cls)

    """ Public Methods """
    
    @classmethod
    def register(cls, item: Type[Any], name: Optional[str] = None) -> None:
        """Adds 'item' to 'registry'.
        
        A separate 'register' method is included so that virtual subclasses can
        also be registered.
        
        Args:
            item (Type[Any]): a class to add to the registry.
            name (Optional[str]): name to use as the key when 'item' is stored
                in 'registry'. Defaults to None. If not passed, the 'get_name'
                method will be used to 
        
        """
        if abc.ABC not in cls.__bases__:
            # The default key for storing cls relies on the 'get_name' method, 
            # which usually will use the snakecase name of 'item'.
            key = name or get_name(item = cls)
            cls.registry[key] = item
        return   


@dataclasses.dataclass
class RegistrarFactory(Registrar, abc.ABC):
    """
    
    """
    registry: ClassVar[MutableMapping[str, Type[Any]]] = {}
    
    """ Public Methods """

    @classmethod
    def create(cls, item: Any, *args: Any, **kwargs: Any) -> RegistrarFactory:
        """Creates an instance of a RegistrarFactory subclass from 'item'.
        
        Args:
            item (Any): any supported data structure which acts as a source for
                creating a RegistrarFactory or a str which matches a key in 
                'registry'.
                                
        Returns:
            RegistrarFactory: a RegistrarFactory subclass instance created based 
                on 'item' and any passed arguments.
                
        """
        if isinstance(item, str):
            try:
                return cls.registry[item](*args, **kwargs)
            except KeyError:
                pass
        try:
            name = get_name(item = item)
            return cls.registry[name](item, *args, **kwargs)
        except KeyError:
            for name, kind in cls.registry.items():
                if kind.__instancecheck__(instance = item):
                    method = getattr(cls, f'from_{name}')
                    return method(item, *args, **kwargs)       
            raise ValueError(
                f'Could not create {cls.__name__} from item because it '
                f'is not one of these supported types: '
                f'{str(list(cls.registry.keys()))}')