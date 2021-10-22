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

Contents:
    
          
To Do:
    Add a full Edge class with seamless support for it in Graph to allow for 
        weights, direction, and other edge attributes.
    Integrate ashford Kinds system when it is finished.
    Add in 'beautify' str representations from amos once those are finished.
    Add in 'dispatcher' decorators to the converter functions.
    
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
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

""" Type-Checking Functions """
    
def is_adjacency(item: object) -> bool:
    """Returns whether 'item' is an adjacency list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency list.
        
    """
    if isinstance(item, MutableMapping):
        connections = list(item.values())
        nodes = list(itertools.chain(item.values()))
        return (
            all(isinstance(e, (Set)) for e in connections)
            and all(isinstance(n, (Set, Hashable)) for n in nodes))
    else:
        return False
    
def is_composite(item: object) -> bool:
    """Returns whether 'item' is a collection of node connections.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a collection of node connections.
        
    """
    return (
        is_adjacency(item = item)
        or is_edges(item = item)
        or is_graph(item = item)
        or is_matrix(item = item)
        or is_tree(item = item))

def is_connections(item: object) -> bool:
    """Returns whether 'item' is a collection of node connections.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a collection of node connections.
        
    """
    return isinstance(item, Collection) and all(is_node(item = i) for i in item)
    
def is_matrix(item: object) -> bool:
    """Returns whether 'item' is an adjacency matrix.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency matrix.
        
    """
    if isinstance(item, tuple) and len(item) == 2:
        matrix = item[0]
        labels = item[1]
        connections = list(itertools.chain(matrix))
        return (
            isinstance(matrix, MutableSequence)
            and isinstance(labels, Sequence) 
            and not isinstance(labels, str)
            and all(isinstance(i, MutableSequence) for i in matrix)
            and all(isinstance(n, Hashable) for n in labels)
            and all(isinstance(e, int) for e in connections))
    else:
        return False

def is_edge(item: object) -> bool:
    """Returns whether 'item' is an edge.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge.
        
    """
    return (
        isinstance(item, tuple) 
        and len(item) == 2
        and is_node(item = item[0])
        and is_node(item = item[1]))

def is_edges(item: object) -> bool:
    """Returns whether 'item' is an edge list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge list.
    
    """
        
    return (
        isinstance(item, Sequence) 
        and not isinstance(item, str)
        and all(is_edge(item = i) for i in item))

def is_graph(item: object) -> bool:
    """Returns whether 'item' is a graph.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a graph.
    
    """
        
    return is_adjacency(item = item) or is_matrix(item = item)
    
def is_node(item: object) -> bool:
    """Returns whether 'item' is a node.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a node.
    
    """
    return isinstance(item, Hashable)

def is_nodes(item: object) -> bool:
    """Returns whether 'item' is a collection of nodes.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a collection of nodes.
    
    """
    return isinstance(item, Collection) and all(is_node(item = i) for i in item)

def is_pipeline(item: object) -> bool:
    """Returns whether 'item' is a pipeline.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a pipeline.
    
    """
    return (
        isinstance(item, Sequence)
        and not isinstance(item, str)
        and all(is_node(item = i) for i in item))

def is_pipelines(item: object) -> bool:
    """Returns whether 'item' is a dict of pipelines.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a dict of pipelines.
    
    """
    return (
        isinstance(item, MutableMapping)
        and all(isinstance(i, Hashable) for i in item.keys())
        and all(is_pipeline(item = i) for i in item.values())) 
    
def is_tree(item: object) -> bool:
    """Returns whether 'item' is a tree.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a tree.
    
    """
    return (
        isinstance(item, MutableMapping)
        and all(
            isinstance(i, (MutableMapping, Hashable)) for i in item.values())) 
  
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
    if not isinstance(item, (Collection)) or isinstance(item, str):
        item = [item]
    adjacency = collections.defaultdict(set)
    if len(item) == 1:
        adjacency.update({item: set()})
    else:
        edges = more_itertools.windowed(item, 2)
        for edge_pair in edges:
            adjacency[edge_pair[0]] = {edge_pair[1]}
    return adjacency

# @to_adjacency.register # type: ignore 
def nodes_to_adjacency(item: Nodes) -> Adjacency:
    """Converts a Nodes to an Adjacency.

    Args:
        item (Nodes): [description]

    Returns:
        Adjacency: [description]
        
    """ 
    return pipeline_to_adjacency(item = item)

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


@dataclasses.dataclass
class Connections(object):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_connections(item = instance)


@dataclasses.dataclass
class Edge(object):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_edge(item = instance)


@dataclasses.dataclass
class Node(object):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_node(item = instance)

    
""" Composite Data Structure Base Classes """
           
@dataclasses.dataclass # type: ignore
class Composite(utilities.RegistrarFactory, containers.Bunch, abc.ABC):
    """Base class for an graph data 
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                      
    """  
    contents: Collection[Any]
    registry: ClassVar[MutableMapping[str, Type[Any]]] = {}
    
    """ Required Subclass Properties """

    @abc.abstractproperty
    def nodes(self) -> Nodes:
        """Returns all stored nodes."""
        pass
    
    """ Required Subclass Methods """
    
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
    
    # """ Properties """

    # @classmethod
    # @property
    # def creators(cls) -> dict[str, types.MethodType]:
    #     """[summary]

    #     Returns:
    #         dict[str, types.MethodType]: [description]
            
    #     """
    #     all_methods = utilities.get_methods(item = cls, exclude = ['creators'])
    #     print('test all methods', all_methods)
    #     creators = [m for m in all_methods if m.__name__.startswith('from_')]
    #     print('test creators in property', creators)
    #     sources = [
    #         utilities.drop_prefix_from_str(item = c.__name__, prefix = 'from_') 
    #         for c in creators]
    #     return dict(zip(sources, creators))

    # """ Dunder Methods """
    
    # def __str__(self) -> str:
    #     """Returns prettier str representation of the stored graph.

    #     Returns:
    #         str: a formatted str of class information and the contained graph.
            
    #     """
    #     return amos.recap.beautify(item = self, package = 'chrisjen')  
         

@dataclasses.dataclass
class Adjacency(Composite, abc.ABC):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_adjacency(item = instance)


@dataclasses.dataclass
class Edges(Composite, abc.ABC):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_edges(item = instance)
    
    
@dataclasses.dataclass
class Matrix(Composite, abc.ABC):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_matrix(item = instance)

        
@dataclasses.dataclass # type: ignore
class Graph(Composite, abc.ABC):
    """Base class for an graph data 
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                                      
    """  
    contents: Collection[Any]

    """ Required Subclass Properties """

    @abc.abstractproperty
    def adjacency(self) -> Adjacency:
        """Returns the stored graph as an adjacency list."""
        pass

    @abc.abstractproperty
    def edges(self) -> Edges:
        """Returns the stored graph as an edge list."""
        pass

    @abc.abstractproperty
    def matrix(self) -> Matrix:
        """Returns the stored graph as an adjacency matrix."""
        pass
    
    @abc.abstractproperty
    def pipeline(self) -> Pipeline:
        """Returns stored graph as a Pipeline."""
        pass
       
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_adjacency(cls, item: Adjacency) -> Graph:
        """Creates a Graph instance from an Adjacency."""
        pass
    
    @abc.abstractclassmethod
    def from_edges(cls, item: Edges) -> Graph:
        """Creates a Graph instance from an Edges."""
        pass
    
    @abc.abstractclassmethod
    def from_matrix(cls, item: Matrix) -> Graph:
        """Creates a Graph instance from a Matrix."""
        pass
    
    @abc.abstractclassmethod
    def from_nodes(cls, item: Nodes) -> Graph:
        """Creates a Graph instance from a Nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Tree) -> Graph:
        """Creates a Graph instance from a Tree."""
        pass

   
@dataclasses.dataclass # type: ignore
class Pipeline(containers.Hybrid, Composite, abc.ABC):
    """Base class for pipeline data structures.
    
    Args:
        contents (MutableSequence[Node]): list of stored Node instances. 
            Defaults to an empty list.
          
    """
    contents: MutableSequence[Node] = dataclasses.field(
        default_factory = list)
     
    """ Required Properties """

    @abc.abstractproperty
    def edges(self) -> Edges:
        """Returns the stored graph as an edge list."""
        pass

    @abc.abstractproperty
    def graph(self) -> Graph:
        """Returns the stored pipeline as a Graph."""
        pass
    
    @abc.abstractproperty
    def tree(self) -> Tree:
        """Returns the stored pipeline as a Tree."""
        pass
    
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_adjacency(cls, item: Adjacency) -> Pipeline:
        """Creates a Pipeline instance from an adjacency list."""
        pass
    
    @abc.abstractclassmethod
    def from_edges(cls, item: Graph) -> Pipeline:
        """Creates a Pipeline instance from an Edges."""
        pass

    @abc.abstractclassmethod
    def from_graph(cls, item: Graph) -> Pipeline:
        """Creates a Pipeline instance from a Graph."""
        pass

    @abc.abstractclassmethod
    def from_matrix(cls, item: Matrix) -> Pipeline:
        """Creates a Pipeline instance from an adjacency matrix."""
        pass
    
    @abc.abstractclassmethod
    def from_nodes(cls, item: Nodes) -> Pipeline:
        """Creates a Pipeline instance from a list of nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_pipelines(cls, item: Pipelines) -> Pipeline:
        """Creates a Pipeline instance from a Pipelines."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Tree) -> Pipeline:
        """Creates a Pipeline instance from a Tree."""
        pass   


@dataclasses.dataclass # type: ignore
class Pipelines(containers.Lexicon, Composite, abc.ABC):
    """Base class a collection of Pipeline instances.
        
    Args:
        contents (MutableMapping[Hashable, Pipeline]): keys are the name or 
            other identifier for the stored Pipeline instances and values are 
            Pipeline instances. Defaults to an empty dict.

    """
    contents: MutableMapping[Hashable, Pipeline] = dataclasses.field(
        default_factory = dict)
     
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
    def tree(self) -> Tree:
        """Returns the stored pipeline as a Tree."""
        pass
    
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_graph(cls, item: Graph) -> Pipelines:
        """Creates a Pipelines instance from a Graph."""
        pass
    
    @abc.abstractclassmethod
    def from_list(cls, item: list[list[Node]]) -> Pipelines:
        """Creates a Pipelines instance from a list of lists of nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_pipeline(cls, item: Pipeline) -> Pipelines:
        """Creates a Pipelines instance from a Pipelines."""
        pass
    
    @abc.abstractclassmethod
    def from_tree(cls, item: Matrix) -> Pipelines:
        """Creates a Pipelines instance from a Tree."""
        pass   


@dataclasses.dataclass # type: ignore
class Tree(containers.Hybrid, Composite, abc.ABC):
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
    def tree(self) -> Tree:
        """Returns the stored pipeline as a Tree."""
        pass
    
    """ Required Subclass Methods """
    
    @abc.abstractclassmethod
    def from_graph(cls, item: Graph) -> Tree:
        """Creates a Tree instance from a Graph."""
        pass
    
    @abc.abstractclassmethod
    def from_list(cls, item: Edges) -> Tree:
        """Creates a Tree instance from a list of nodes."""
        pass
    
    @abc.abstractclassmethod
    def from_pipeline(cls, item: Pipeline) -> Tree:
        """Creates a Tree instance from a Pipeline."""
        pass
   
    @abc.abstractclassmethod
    def from_pipelines(cls, item: Pipelines) -> Tree:
        """Creates a Tree instance from a Pipelines."""
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


@dataclasses.dataclass
class Nodes(Composite, abc.ABC):
    
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return is_nodes(item = instance)

 