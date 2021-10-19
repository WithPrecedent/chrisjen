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
RawMatrix: Type[Any] = MutableSequence[MutableSequence[int]]
Labels: Type[Any] = MutableSequence[Hashable]
Matrix: Type[Any] = tuple[RawMatrix, Labels]
Nodes: Type[Any] = Union[Hashable, Collection[Hashable]]
Composite: Type[Any] = Union[Adjacency, Edges, Matrix, Nodes]


def is_adjacency_list(item: object) -> bool:
    """Returns whether 'item' is an adjacency list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an adjacency list.
        
    """
    if isinstance(item, MutableMapping):
        connections = list(item.values())
        nodes = list(itertools.chain(item.values()))
        return (all(isinstance(e, (Set)) for e in connections)
                and all(isinstance(n, Hashable) for n in nodes))
    else:
        return False

def is_adjacency_matrix(item: object) -> bool:
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

def is_edge_list(item: object) -> bool:
    """Returns whether 'item' is an edge list.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is an edge list.
    
    """
        
    return (
        isinstance(item, MutableSequence) 
        and all(is_edge(item = i) for i in item))

def is_node(item: object) -> bool:
    """Returns whether 'item' is a node.

    Args:
        item (object): instance to test.

    Returns:
        bool: whether 'item' is a node.
    
    """
    return isinstance(item, Hashable)

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
    contents: Collection[Any]
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
        if is_adjacency_list(item = item):
            return cls.from_adjacency(item = item) # type: ignore
        elif is_adjacency_matrix(item = item):
            return cls.from_matrix(item = item) # type: ignore
        elif is_edge_list(item = item):
            return cls.from_edges(item = item) # type: ignore
        elif is_pipeline(item = item): 
            return cls.from_pipeline(item = item) # type: ignore
        elif is_tree(item = item):
            return cls.from_tree(item = item)
        else:
            raise TypeError(
                f'create requires item to be an adjacency list, adjacency '
                f'matrix, edge list, pipeline, or tree')      
    
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