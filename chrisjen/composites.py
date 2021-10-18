"""
composites: base lightweight composite data structures
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

Classes:
    
          
To Do:
    Add an Edge class and seamless support for it in Graph to allow for weights,
        direction, and other edge attributes.
    
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Mapping, MutableMapping, MutableSequence, Sequence,
    Set)
import dataclasses
import itertools
import inspect
from typing import Any, Callable, ClassVar, Optional, Type, TypeVar, Union

import more_itertools

from . import containers
from . import utilities
   

""" Type Aliases """

# Simpler alias for generic callable.
Operation = Callable[..., Any]
# Shorter alias for things that can be wrapped.
Wrappable = Union[Type[Any], Operation]
# Abbreviated alias for a dict of inspect.Signature types.
Signatures = MutableMapping[str, inspect.Signature]
# Alias for dict of Type[Any] types.
Types = MutableMapping[str, Type[Any]]

Changer: Type[Any] = Callable[[Hashable], None]
Finder: Type[Any] = Callable[[Hashable], Optional[Hashable]]

Adjacency: Type[Any] = MutableMapping[Hashable, Set[Hashable]]
Edge: Type[Any] = tuple[Hashable, Hashable]
Edges: Type[Any] = MutableSequence[Edge]
Connections: Type[Any] = Set[Hashable]
RawMatrix: Type[Any] = 
Matrix: Type[Any] = tuple[
    MutableSequence[MutableSequence[int]], 
    MutableSequence[Hashable]]
Nodes: Type[Any] = Union[Hashable, Pipeline]
Composite: Type[Any] = Union[Adjacency, Edges, Matrix, Nodes]

def is_adjacency_list(item: Any) -> bool:
    """Returns whether 'item' is an adjacency list."""
    if isinstance(item, MutableMapping):
        edges = list(item.values())
        nodes = list(itertools.chain(item.values()))
        return (all(isinstance(e, (Set)) for e in edges)
                and all(isinstance(n, Hashable) for n in nodes))
    else:
        return False

def is_adjacency_matrix(item: Any) -> bool:
    """Returns whether 'item' is an adjacency matrix."""
    if isinstance(item, tuple) and len(item) == 2:
        matrix = item[0]
        names = item[1]
        edges = list(more_itertools.collapse(matrix))
        return (isinstance(matrix, MutableSequence)
                and isinstance(names, MutableSequence) 
                and all(isinstance(i, MutableSequence) for i in matrix)
                and all(isinstance(n, Hashable) for n in names)
                and all(isinstance(e, int) for e in edges))
    else:
        return False

def is_edge_list(item: Any) -> bool:
    """Returns whether 'item' is an edge list."""
    if (isinstance(item, MutableSequence) 
            and all(len(i) == 2 for i in item)
            and all(isinstance(i, tuple) for i in item)): 
        nodes = list(more_itertools.collapse(item))
        return all(isinstance(n, Hashable) for n in nodes)
    else:
        return False
    
def is_pipeline(item: Any) -> bool:
    """Returns whether 'item' is a pipeline."""
    return (isinstance(item, MutableSequence)
            and all(isinstance(i, Hashable) for i in item))
    
""" Composite-Related Kinds """

@dataclasses.dataclass
class Node(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        methods (ClassVar[Union[list[str], MutableMapping[str, 
            inspect.Signature]]]): a list of str names of methods or a dict of 
            str names of methods with values that are inspect.Signature type for 
            the named methods. 
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
            
    """
    methods: ClassVar[Union[list[str], utilities.Signatures]] = [
        '__hash__', '__eq__', '__ne__']
    generic: ClassVar[Optional[Type[Any]]] = Hashable


@dataclasses.dataclass
class Composite(utilities.Kind):
    """ Type for composite objects.
    
    Args:
        methods (ClassVar[Union[list[str], MutableMapping[str, 
            inspect.Signature]]]): a list of str names of methods or a dict of 
            str names of methods with values that are inspect.Signature type for 
            the named methods. 
        properties (ClassVar[list[str]]): a list of str names of properties. 
            
    """   
    methods: ClassVar[Union[list[str], utilities.Signatures]] = [
        'add', 'delete', 'merge', 'subset', 'walk', '__add__',  '__getitem__', 
        '__iadd__', '__iter__', '__len__', '__str__']
    properties: ClassVar[list[str]] = ['nodes']


@dataclasses.dataclass
class Connections(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = Collection
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = Node


@dataclasses.dataclass
class Network(Composite):
    """ Type for nodes in composite objects.
    
    Args:
        methods (ClassVar[Union[list[str], MutableMapping[str, 
            inspect.Signature]]]): a list of str names of methods or a dict of 
            str names of methods with values that are inspect.Signature type for 
            the named methods. 
        properties (ClassVar[list[str]]): a list of str names of properties. 
            
    """    
    methods: ClassVar[Union[list[str], utilities.Signatures]] = [
        'connect', 'disconnect']
    properties: ClassVar[list[str]] = ['edges']


@dataclasses.dataclass
class Directed(Network):
    """ Type for nodes in composite objects.
    
    Args:
        methods (ClassVar[Union[list[str], MutableMapping[str, 
            inspect.Signature]]]): a list of str names of methods or a dict of 
            str names of methods with values that are inspect.Signature type for 
            the named methods. 
        properties (ClassVar[list[str]]): a list of str names of properties. 
            
    """    
    methods: ClassVar[Union[list[str], utilities.Signatures]] = [
        'prepend', 'append']
    properties: ClassVar[list[str]] = ['endpoints', 'paths', 'roots']


@dataclasses.dataclass
class Adjacency(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = MutableMapping
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        str, Connections)


@dataclasses.dataclass
class Edge(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (Node, Node)


@dataclasses.dataclass
class Edges(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (Edge)
    

@dataclasses.dataclass
class Labels(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """   
    generic: ClassVar[Optional[Type[Any]]] = Sequence
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = str


@dataclasses.dataclass
class RowColumn(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = Sequence
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = int
    
    
@dataclasses.dataclass
class RawMatrix(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        RowColumn, RowColumn)
    
    
@dataclasses.dataclass
class Matrix(utilities.Kind):
    """ Type for nodes in composite objects.
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = tuple
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (
        RawMatrix, Labels)
    

@dataclasses.dataclass
class RawTree(utilities.Kind):
    """ Type for tree data structure
    
    Args:
        generic (ClassVar[Optional[Type[Any]]]): any generic type (e.g. the
            base classes in collections.abc) that the Kind must be a subclass
            of.
        contains (ClassVar[Optional[Union[Any, tuple[Any, ...]]]]): if 'generic'
            is a containers, 'contains' may refer to the allowed types in that
            container.
            
    """    
    generic: ClassVar[Optional[Type[Any]]] = MutableMapping
    contains: ClassVar[Optional[Union[Any, tuple[Any, ...]]]] = (str, Composite)
    
    
""" Composite Data Structure Base Classes """

@dataclasses.dataclass # type: ignore
class Graph(containers.Bunch):
    """Base class for an graph data 
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
        sources (ClassVar[Mapping[Type[Any], str]]): keys are the types of the
            data sources for object creation. For the appropriate creation
            classmethod to be called, the types need to match the type of the
            first argument passed.
                                      
    """  
    # contents: Collection[Any]
    # sources: ClassVar[Mapping[Type[Any], str]] = {
    #     Adjacency: 'adjacency',
    #     Matrix: 'matrix',
    #     Edges: 'edges',
    #     'Pipeline': 'pipeline',
    #     'Pipelines': 'pipelines',
    #     'Tree': 'tree'}
    
    """ Required Subclass Properties """

    @abc.abstractproperty
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an adjacency list."""
        pass

    @abc.abstractproperty
    def edges(self) -> Adjacency:
        """Returns the stored graph as an edge list."""
        pass

    @abc.abstractproperty
    def matrix(self) -> Matrix:
        """Returns the stored graph as an adjacency matrix."""
        pass

    @abc.abstractproperty
    def nodes(self) -> list[Node]:
        """Returns all stored nodes in a list."""
        pass
    
    @abc.abstractproperty
    def pipeline(self) -> Pipeline:
        """Returns stored graph as a Pipeline."""
        pass
       
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_adjacency(cls, item: Adjacency) -> Graph:
        """Creates a Graph instance from an Adjacency instance."""
        pass
    
    @abc.abstractclassmethod
    def from_edges(cls, item: Edges) -> Graph:
        """Creates a Graph instance from an Edges instance."""
        pass
    
    @abc.abstractclassmethod
    def from_matrix(cls, item: Matrix) -> Graph:
        """Creates a Graph instance from a Matrix instance."""
        pass
    
    @abc.abstractclassmethod
    def from_pipeline(cls, item: Pipeline) -> Graph:
        """Creates a Graph instance from a Pipeline instance."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Tree) -> Graph:
        """Creates a Graph instance from a Tree instance."""
        pass
       
    @abc.abstractmethod
    def add(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def delete(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def merge(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def subset(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def walk(item: Any, *args, **kwargs) -> None:
        pass

    """ Public Methods """
    
    @classmethod
    def create(cls, item: Composite) -> Graph:
        """Creates an instance of a Graph from 'item'.
        
        Args:
            item (Composite): an adjacency list, adjacency matrix, 
                edge list, or pipeline which can used to create the stored 
                graph.
                
        Returns:
            Graph: a Graph instance created based on 'item'.
                
        """
        if isinstance(item, Adjacency):
            return cls.from_adjacency(item = item) # type: ignore
        elif isinstance(item, Matrix):
            return cls.from_matrix(item = item) # type: ignore
        elif isinstance(item, tuple):
            return cls.from_edges(item = item) # type: ignore
        elif isinstance(item, Pipeline): 
            return cls.from_pipeline(item = item) # type: ignore
        else:
            raise TypeError(
                f'create requires item to be an adjacency list, adjacency '
                f'matrix, edge list, or pipeline')      
    
    # """ Dunder Methods """
    
    # @classmethod
    # def __subclasshook__(cls, subclass: Type[Any]) -> bool:
    #     """Tests whether 'subclass' has the relevant characteristics."""
    #     return (
    #         utilities.has_traits(
    #             item = subclass,
    #             methods = [
    #                 'add', 'create', 'delete', 'from_adjacency', 'from_edges', 
    #                 'from_matrix', 'from_pipeline', 'subset', '__add__', 
    #                 '__getitem__', '__iadd__', '__iter__', '__len__', 
    #                 '__str__'],
    #             properties = ['adjacency', 'matrix']))
            
    # def __str__(self) -> str:
    #     """Returns prettier str representation of the stored graph.

    #     Returns:
    #         str: a formatted str of class information and the contained graph.
            
    #     """
    #     return amos.beautify(item = self, package = 'chrisjen')
   
   
@dataclasses.dataclass # type: ignore
class Pipeline(utilities.SourcesFactory, containers.Hybrid):
    """Base class for pipeline data structures.
    
    Args:
        contents (MutableSequence[Node]): list of stored Node instances. 
            Defaults to an empty list.
          
    """
    contents: MutableSequence[Node] = dataclasses.field(
        default_factory = list)
    sources: ClassVar[Mapping[Type[Any], str]] = {
        Graph: 'graph',
        Edges: 'edges',
        MutableSequence: 'list',
        'Pipelines': 'pipelines',
        'Tree': 'tree'}
     
    """ Required Properties """

    @abc.abstractproperty
    def edges(self) -> Adjacency:
        """Returns the stored graph as an edge list."""
        pass

    @abc.abstractproperty
    def graph(self) -> Graph:
        """Returns the stored pipeline as a Graph."""
        pass

    @abc.abstractproperty
    def nodes(self) -> list[Node]:
        """Returns all stored nodes in a list."""
        pass
    
    @abc.abstractproperty
    def tree(self) -> Tree:
        """Returns the stored pipeline as a Tree."""
        pass
    
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_graph(cls, item: Graph) -> Pipeline:
        """Creates a Pipeline instance from a Graph instance."""
        pass
    
    @abc.abstractclassmethod
    def from_list(cls, item: list[Node]) -> Pipeline:
        """Creates a Pipeline instance from a list of nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_pipelines(cls, item: Pipelines) -> Pipeline:
        """Creates a Pipeline instance from a Pipelines instance."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Tree) -> Pipeline:
        """Creates a Pipeline instance from a Tree instance."""
        pass   
    
    @abc.abstractmethod
    def add(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def delete(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def merge(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def subset(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def walk(item: Any, *args, **kwargs) -> None:
        pass
    
    # """ Dunder Methods """
    
    # @classmethod
    # def __subclasshook__(cls, subclass: Type[Any]) -> bool:
    #     """Tests whether 'subclass' has the relevant characteristics."""
    #     return (
    #         utilities.has_traits(
    #             item = subclass,
    #             methods = [
    #                 'add', 'create', 'delete', 'from_adjacency', 'from_edges', 
    #                 'from_matrix', 'from_pipeline', 'subset', '__add__', 
    #                 '__getitem__', '__iadd__', '__iter__', '__len__', 
    #                 '__str__'],
    #             properties = ['adjacency', 'matrix']))
            
    # def __str__(self) -> str:
    #     """Returns prettier str representation of the stored graph.

    #     Returns:
    #         str: a formatted str of class information and the contained graph.
            
    #     """
    #     return amos.recap.beautify(item = self, package = 'chrisjen')


@dataclasses.dataclass # type: ignore
class Pipelines(utilities.SourcesFactory, containers.Lexicon):
    """Base class a collection of Pipeline instances.
        
    Args:
        contents (MutableMapping[Hashable, Pipeline]): keys are the name or 
            other identifier for the stored Pipeline instances and values are 
            Pipeline instances. Defaults to an empty dict.

    """
    contents: MutableMapping[Hashable, Pipeline] = dataclasses.field(
        default_factory = dict)
    sources: ClassVar[Mapping[Type[Any], str]] = {
        Graph: 'graph',
        'Tree': 'tree'}
     
    """ Required Properties """

    @abc.abstractproperty
    def edges(self) -> Adjacency:
        """Returns the stored graph as an edge list."""
        pass

    @abc.abstractproperty
    def graph(self) -> Graph:
        """Returns the stored pipeline as a Graph."""
        pass

    @abc.abstractproperty
    def nodes(self) -> list[Node]:
        """Returns all stored nodes in a list."""
        pass
    
    @abc.abstractproperty
    def tree(self) -> Tree:
        """Returns the stored pipeline as a Tree."""
        pass
    
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_graph(cls, item: Graph) -> Pipelines:
        """Creates a Pipelines instance from a Graph instance."""
        pass
    
    @abc.abstractclassmethod
    def from_list(cls, item: list[list[Node]]) -> Pipelines:
        """Creates a Pipelines instance from a list of lists of nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_pipeline(cls, item: Pipeline) -> Pipelines:
        """Creates a Pipelines instance from a Pipelines instance."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Matrix) -> Pipelines:
        """Creates a Pipelines instance from a Tree instance."""
        pass   
    
    @abc.abstractmethod
    def add(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def delete(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def merge(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def subset(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def walk(item: Any, *args, **kwargs) -> None:
        pass
        
    
@dataclasses.dataclass # type: ignore
class Tree(utilities.SourcesFactory, containers.Hybrid):
    """Base class for an tree data structures.
    
    The Tree class uses a Hybrid instead of a linked list for storing children
    nodes to allow easier access of nodes further away from the root. For
    example, a user might use 'a_tree["big_branch"]["small_branch"]["a_leaf"]' 
    to access a desired node instead of 'a_tree[2][0][3]' (although the latter
    access technique is also supported).
    
    There are several differences between a Tree and a Graph in chrisjen:
        1) Graphs are more flexible. Trees must have 1 root, are directed, and
            each node can have only 1 parent node.
        2) Edges are only implicit in a Tree whereas they are explicit in a 
            Graph. This allows for certain methods and functions surrounding
            iteration and traversal to be faster.
        3) As the size of the data structure increases, a Tree should use less
            memory because the data about relationships between nodes is not
            centrally maintained (as with an adjacency matrix). This decreases
            access time to non-consecutive nodes, but is more efficient for 
            larger data structures.
        
    Args:
        contents (MutableSequence[Node]): list of stored Tree or other 
            Node instances. Defaults to an empty list.
        name (Optional[str]): name of Tree node which should match a parent 
            tree's key name corresponding to this Tree node. All nodes in a Tree
            must have unique names. The name is used to make all Tree nodes 
            hashable and capable of quick comparison. Defaults to None, but it
            should not be left as None when added to a Tree.
        parent (Optional[Tree]): parent Tree, if any. Defaults to None.

                  
    """
    contents: MutableSequence[Node] = dataclasses.field(
        default_factory = list)
    name: Optional[str] = None
    parent: Optional[Tree] = None 
    sources: ClassVar[Mapping[Type[Any], str]] = {
        Edges: 'edges',
        Graph: 'graph',
        Pipeline: 'pipeline',
        Pipelines: 'pipelines'}
    
    """ Required Properties """

    @abc.abstractproperty
    def edges(self) -> Adjacency:
        """Returns the stored graph as an edge list."""
        pass

    @abc.abstractproperty
    def graph(self) -> Graph:
        """Returns the stored pipeline as a Graph."""
        pass

    @abc.abstractproperty
    def nodes(self) -> list[Node]:
        """Returns all stored nodes in a list."""
        pass
    
    @abc.abstractproperty
    def tree(self) -> Tree:
        """Returns the stored pipeline as a Tree."""
        pass
    
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_graph(cls, item: Graph) -> Pipeline:
        """Creates a Pipeline instance from a Graph instance."""
        pass
    
    @abc.abstractclassmethod
    def from_list(cls, item: Edges) -> Pipeline:
        """Creates a Pipeline instance from a list of nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_pipelines(cls, item: Pipeline) -> Pipeline:
        """Creates a Pipeline instance from a Pipelines instance."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Matrix) -> Pipeline:
        """Creates a Pipeline instance from a Tree instance."""
        pass   
    
    @abc.abstractmethod
    def add(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def delete(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def merge(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def subset(item: Any, *args, **kwargs) -> None:
        pass
    
    @abc.abstractmethod
    def walk(item: Any, *args, **kwargs) -> None:
        pass

    """ Dunder Methods """

    def __add__(self, other: Union[Composite]) -> None:
        """Adds 'other' to the stored tree using the 'append' method.

        Args:
            other (Union[Composite]): another Tree, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        """
        self.append(item = other)     
        return 

    def __radd__(self, other: Union[Composite]) -> None:
        """Adds 'other' to the stored tree using the 'prepend' method.

        Args:
            other (Union[Composite]): another Tree, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        """
        self.prepend(item = other)     
        return 

    def __missing__(self) -> dict[str, Tree]:
        """[summary]

        Returns:
            dict[str, Tree]: [description]
            
        """
        return {}
    
    def __hash__(self) -> int:
        """[summary]

        Returns:
            int: [description]
            
        """
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        """[summary]

        Args:
            other (Any): [description]

        Returns:
            bool: [description]
            
        """
        if hasattr(other, 'name'):
            return other.name == self.name
        else:
            return False
        
    def __ne__(self, other: Any) -> bool:
        """[summary]

        Args:
            other (Any): [description]

        Returns:
            bool: [description]
            
        """
        return not self.__eq__(other = other)
          
    # def __str__(self) -> str:
    #     """Returns prettier str representation of the stored tree.

    #     Returns:
    #         str: a formatted str of class information and the contained tree.
            
    #     """
    #     return amos.recap.beautify(item = self, package = 'chrisjen')