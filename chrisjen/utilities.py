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

  
""" Converters """

# @amos.dynamic.dispatcher 
def to_adjacency(item: Any) -> Adjacency:
    """Converts 'item' to an Adjacency.
    
    Args:
        item (Any): item to convert to an Adjacency.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        Adjacency: derived from 'item'.

    """
    if isinstance(item, Adjacency):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_adjacency.register # type: ignore
def edges_to_adjacency(item: Edges) -> Adjacency:
    """Converts and edge list to an adjacency list.

    Args:
        item (Edges): [description]

    Returns:
        Adjacency: [description]
        
    """    
    print('test edges', item)
    adjacency = collections.defaultdict(set)
    for edge_pair in item:
        if edge_pair[0] not in adjacency:
            adjacency[edge_pair[0]] = {edge_pair[1]}
        else:
            adjacency[edge_pair[0]].add(edge_pair[1])
        if edge_pair[1] not in adjacency:
            adjacency[edge_pair[1]] = set()
    return adjacency

# @to_adjacency.register # type: ignore 
def matrix_to_adjacency(item: Matrix) -> Adjacency:
    """Converts a Matrix to an Adjacency.

    Args:
        item (Matrix): [description]

    Returns:
        Adjacency: [description]
    """    
    matrix = item[0]
    names = item[1]
    name_mapping = dict(zip(range(len(matrix)), names))
    raw_adjacency = {
        i: [j for j, adjacent in enumerate(row) if adjacent] 
        for i, row in enumerate(matrix)}
    adjacency = collections.defaultdict(set)
    for key, value in raw_adjacency.items():
        new_key = name_mapping[key]
        new_values = set()
        for edge in value:
            new_values.add(name_mapping[edge])
        adjacency[new_key] = new_values
    return adjacency

# @to_adjacency.register # type: ignore 
def pipeline_to_adjacency(item: Pipeline) -> Adjacency:
    """Converts a Pipeline to an Adjacency.

    Args:
        item (Pipeline): [description]

    Returns:
        Adjacency: [description]
    """    
    adjacency = collections.defaultdict(set)
    edges = more_itertools.windowed(item, 2)
    for edge_pair in edges:
        adjacency[edge_pair[0]] = {edge_pair[1]}
    return adjacency

# @amos.dynamic.dispatcher   
def to_edges(item: Any) -> Edges:
    """Converts 'item' to an Edges.
    
    Args:
        item (Any): item to convert to an Edges.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        Edges: derived from 'item'.

    """
    if isinstance(item, Edges):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')
    
# @to_edges.register # type: ignore
def adjacency_to_edges(item: Adjacency) -> Edges:
    """[summary]

    Args:
        item (Adjacency): [description]

    Returns:
        Edges: [description]
        
    """    
    """Converts an Adjacency to an Edges."""
    edges = []
    for node, connections in item.items():
        for connection in connections:
            edges.append(tuple(node, connection))
    return edges

# @amos.dynamic.dispatcher   
def to_matrix(item: Any) -> Matrix:
    """Converts 'item' to a Edges.
    
    Args:
        item (Any): item to convert to a Matrix.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        Matrix: derived from 'item'.

    """
    if isinstance(item, Matrix):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_matrix.register # type: ignore 
def adjacency_to_matrix(item: Adjacency) -> Matrix:
    """[summary]

    Args:
        item (Adjacency): [description]

    Returns:
        Matrix: [description]
    """    
    """Converts an Adjacency to a Matrix."""
    names = list(item.keys())
    matrix = []
    for i in range(len(item)): 
        matrix.append([0] * len(item))
        for j in item[i]:
            matrix[i][j] = 1
    return tuple(matrix, names)    

# @to_tree.register # type: ignore 
def matrix_to_tree(item: Matrix) -> Tree:
    """[summary]

    Args:
        item (Matrix): [description]

    Returns:
        Tree: [description]
        
    """
    tree = {}
    for node in item:
        children = item[:]
        children.remove(node)
        tree[node] = matrix_to_tree(children)
    return tree

""" Factories """

@dataclasses.dataclass
class BaseFactory(abc.ABC):
    """Base class for instance factory mixins.

    Namespaces: create   
    
    """
    
    """ Required Subclass Methods """

    @abc.abstractclassmethod
    def create(cls, item: Any, *args: Any, **kwargs: Any) -> BaseFactory:
        """Implements technique for creating a (sub)class instance.

        Args:
            item (Any): argument indicating creation method to use.

        Returns:
            BaseFactory: instance of a SourcesFactory.
            
        """
        pass

          
@dataclasses.dataclass
class SourcesFactory(BaseFactory, abc.ABC):
    """Supports subclass creation using 'sources' class attribute.

    Args:
        sources (str, str]]): keys are str names of the types of the data 
            sources for object creation. For the appropriate creation 
            classmethod to be called, the types need to match the type of the
            first argument passed.
    
    Namespaces: create, sources, _get_create_method_name       
    
    """
    sources: ClassVar[Mapping[str, str]] = {}
    
    """ Public Methods """

    @classmethod
    def create(cls, item: Any, *args: Any, **kwargs: Any) -> SourcesFactory:
        """Calls corresponding creation class method to instance a class.
        
        For create to work properly, there should be a corresponding classmethod
        named f'from_{value in sources}'. If you would prefer a different naming
        format, you can subclass SourcesFactory and override the 
        '_get_create_method_name' classmethod.

        Raises:
            AttributeError: If an appropriate method does not exist for the
                data type of 'item.'

        Returns:
            TypeFactory: instance of a SourcesFactory.
            
        """
        for kind, suffix in cls.sources.items():
            if isinstance(kind, str):
                tester = ast.literal_eval(kind)
            else:
                tester = kind
            if isinstance(item, tester):
                method_name = cls._get_create_method_name(item = suffix)
                try:
                    method = getattr(cls, method_name)
                except AttributeError:
                    raise AttributeError(f'{method_name} does not exist')
                return method(item, *args, **kwargs)
        return cls(*args, **kwargs)


    """ Private Methods """
    
    @classmethod
    def _get_create_method_name(cls, item: str) -> str:
        """Returns classmethod name for creating an instance.
        
        Args:
            item (str): name corresponding to part of the str of the method
                name used for instancing.
                
        """
        return f'from_{item}'

          
@dataclasses.dataclass
class TypeFactory(BaseFactory, abc.ABC):
    """Supports subclass creation using str name of item type passed.

    Namespaces: create, _get_create_method_name       
    
    """
    
    """ Public Methods """

    @classmethod
    def create(cls, item: Any, *args: Any, **kwargs: Any) -> TypeFactory:
        """Calls construction method based on type of 'item'.
        
        For create to work properly, there should be a corresponding classmethod
        named f'from_{snake-case str name of type}'. If you would prefer a 
        different naming format, you can subclass TypeFactory and override the 
        '_get_create_method_name' classmethod.

        Raises:
            AttributeError: If an appropriate method does not exist for the
                data type of 'item.'

        Returns:
            TypeFactory: instance of a TypeFactory.
            
        """
        suffix = modify.snakify(item = str(type(item)))
        method_name = cls._get_create_method_name(item = suffix)
        try:
            method = getattr(cls, method_name)
        except AttributeError:
            raise AttributeError(f'{method_name} does not exist')
        return method(item, *args, **kwargs)

    """ Private Methods """
    
    @classmethod
    def _get_create_method_name(cls, item: str) -> str:
        """Returns classmethod name for creating an instance.
        
        Args:
            item (str): name corresponding to part of the str of the method
                name used for instancing.
                
        """
        return f'from_{item}'
      

@dataclasses.dataclass
class SubclassFactory(BaseFactory, abc.ABC):
    """Returns a subclass based on arguments passed to the 'create' method."""
        
    """ Public Methods """

    @classmethod
    def create(cls, item: str, *args: Any, **kwargs: Any) -> SubclassFactory:
        """Returns subclass based on 'item'
        
        A subclass in the '__subclasses__' attribute is selected based on the
        snake-case name of the subclass.
        
        Raises:
            KeyError: If a corresponding subclass does not exist for 'item.'

        Returns:
            SubclassFactory: instance of a SubclassFactory subclass.
            
        """
        options = {snakify(item = s.__name__): s for s in cls.__subclasses__}
        try:
            return options[item](*args, **kwargs)
        except KeyError:
            raise KeyError(f'No subclass {item} was found')


""" Simplified Protocol System """

def is_generic(
    item: Union[Type[Any], object], 
    generic: Optional[Type[Any]],
    contains: Optional[Union[Any, tuple[Any, ...]]] = None) -> bool:
    """Tests whether 'item' is a subclass or instance of 'generic'.
    
    Returns True if 'item' is a subclass/instance of 'generic' or 'generic' is 
    None.
    
    Args:
        item (Union[Type[Any], object]): [description]
        generic (Optional[Type[Any]]): [description]
        contains (Optional[Union[Any, tuple[Any, ...]]]): Defaults to None.

    Returns:
        bool: [description]
        
    """
    if not inspect.isclass(item):
        item = item.__class__
    return generic is None or issubclass(item, generic) # type: ignore
  
def is_kind(item: Union[Type[Any], object], kind: Kind) -> bool:
    """Returns whether 'item' is an instance or subclass of 'kind'.

    Args:
        item (Union[Type[Any], object]): [description]
        kind (Kind): [description]

    Returns:
        bool: [description]
        
    """  
    if not inspect.isclass(item):
        item = item.__class__   
    return (
        has_traits(
            item = item,
            attributes = kind.attributes,
            methods = kind.methods, 
            properties = kind.properties)
        and is_generic(
             item = item, 
             generic = kind.generic,
             contains = kind.contains))


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
    include_private: bool = False) -> dict[str, Any]:
    """Returns dict of attributes of 'item'.
    
    Args:
        item (Any): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        dict[str, Any]: dict of attributes in 'item' (keys are attribute names 
            and values are attribute values).
            
    """
    attributes = name_attributes(item = item, include_private = include_private)
    values = [getattr(item, m) for m in attributes]
    return dict(zip(attributes, values))

def get_methods(
    item: Union[object, Type[Any]], 
    include_private: bool = False) -> dict[str, types.MethodType]:
    """Returns dict of methods of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.

    Returns:
        dict[str, types.MethodType]: dict of methods in 'item' (keys are method 
            names and values are methods).
        
    """ 
    methods = name_methods(item = item, include_private = include_private)
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
    include_private: bool = False) -> dict[str, Any]:
    """Returns properties of 'item'.

    Args:
        item (object): instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.

    Returns:
        dict[str, Any]: dict of properties in 'item' (keys are property names 
            and values are property values).
        
    """    
    properties = name_properties(item = item, include_private = include_private)
    values = [getattr(item, p) for p in properties]
    return dict(zip(properties, values))

def get_signatures(
    item: Union[object, Type[Any]], 
    include_private: bool = False) -> dict[str, inspect.Signature]:
    """Returns dict of method signatures of 'item'.

    Args:
        item (Union[object, Type[Any]]): class or instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.

    Returns:
        dict[str, inspect.Signature]: dict of method signatures in 'item' (keys 
            are method names and values are method signatures).
                   
    """ 
    methods = name_methods(item = item, include_private = include_private)
    signatures = [inspect.signature(getattr(item, m)) for m in methods]
    return dict(zip(methods, signatures))

def get_variables(
    item: object, 
    include_private: bool = False) -> dict[str, Any]:
    """Returns dict of attributes of 'item' that are not methods or properties.
    
    Args:
        item (object): instance to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        dict[str, Any]: dict of attributes in 'item' (keys are attribute names 
            and values are attribute values) that are not methods or properties.
            
    """
    attributes = name_attributes(item = item, include_private = include_private)
    methods = name_methods(item = item, include_private = include_private)
    properties = name_properties(item = item, include_private = include_private)
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
        try:
            attribute = getattr(item, attribute)
        except AttributeError:
            return False
    return inspect.ismethod(attribute)

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
    include_private: bool = False) -> list[str]:
    """Returns attribute names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        list[str]: names of attributes in 'item'.
            
    """
    names = dir(item)
    if not include_private:
        names = drop_privates(item = names)
    return names

def name_methods(
    item: Union[object, Type[Any]], 
    include_private: bool = False) -> list[str]:
    """Returns method names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        list[str]: names of methods in 'item'.
            
    """
    methods = [
        a for a in dir(item)
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
    include_private: bool = False) -> list[str]:
    """Returns method names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        list[str]: names of properties in 'item'.
            
    """
    if not inspect.isclass(item):
        item = item.__class__
    properties = [
        a for a in dir(item)
        if is_property(item = item, attribute = a)]
    if not include_private:
        properties = drop_privates(item = properties)
    return properties

def name_variables(
    item: Union[object, Type[Any]], 
    include_private: bool = False) -> list[str]:
    """Returns variable names of 'item'.
    
    Args:
        item (Union[object, Type[Any]]): item to examine.
        include_private (bool): whether to include items that begin with '_'
            (True) or to exclude them (False). Defauls to False.
                        
    Returns:
        list[str]: names of attributes in 'item' that are neither methods nor
            properties.
            
    """
    names = [a for a in dir(item) if is_variable(item = item, attribute = a)]
    if not include_private:
        names = drop_privates(item = names)
    return names

    
@dataclasses.dataclass
class Kind(abc.ABC):
    """Base class for easy protocol typing.
    
    The Kind system allows structural virtual subclassing based by matching 
    various aspects of a class with those required. 
    
    Kind must be subclassed either directly by using the helper function 
    'kindify'. Kind subclasses can be further subclassed and inherit the aspects
    of the inherited Kind. All of its attributes are stored as class-level 
    variables and subclasses are not designed to be instanced.
    
    Args:
        attributes (ClassVar[Union[list[str], MutableMapping[str, Type[Any]]]]): 
            a list of the str names of attributes that are neither methods nor 
            properties or a dict of str names of attributes that are neither 
            methods nor properties with values that are types of those 
            attributes. Defaults to an empty list.
        methods (ClassVar[Union[list[str], MutableMapping[str, 
            inspect.Signature]]]): a list of str names of methods or a dict of 
            str names of methods with values that are inspect.Signature type for 
            the named methods. Defaults to an empty list.
        properties (ClassVar[list[str]]): a list of str names of properties. 
            Defaults to an empty list.
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of. Defaults to None.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
        registry (ClassVar[MutableMapping[str, Kind]]): dict which stores 
            registered Kind subclasses.
    
    """
    attributes: ClassVar[Union[list[str], Types]] = []
    methods: ClassVar[Union[list[str], Signatures]] = []
    properties: ClassVar[list[str]] = []
    generic: ClassVar[Optional[Type[Any]]] = None
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = None
    registry: ClassVar[MutableMapping[str, Kind]] = {}
            
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Tests whether 'subclass' has the relevant characteristics."""
        if hasattr(super(), '__subclasshook__'):
            return (
                super().__subclasshook__(subclass)
                and is_kind(item = subclass, kind = cls))
        else:
            return is_kind(item = subclass, kind = cls) # type: ignore