"""
graphs: lightweight graph data structures
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
    System (Graph): a lightweight directed acyclic graph (DAG). Internally, the 
        graph is stored as an adjacency list. As a result, it should primarily 
        be used for workflows or other uses that do require large graphs.
        
To Do:
    Complete Network which will use an adjacency matrix for internal storage.
    
"""
from __future__ import annotations
from collections.abc import (
    Hashable, MutableMapping, MutableSequence, Sequence, Set)
import collections.abc
import copy
import dataclasses
import itertools
from typing import Any, Callable, ClassVar, Optional, Type, TypeVar, Union

import more_itertools

from . import containers
from . import composites
from . import utilities
import chrisjen

    
@dataclasses.dataclass
class System(containers.Lexicon, composites.Graph):
    """Directed graph with unweighted edges.
    
    Args:
        contents (Collection[Any]): stored collection of nodes and/or edges.
                            
    """  
    contents: MutableMapping[Hashable, Any] = dataclasses.field(
        default_factory = dict)
    
    """ Properties """

    @property
    def adjacency(self) -> composites.Adjacency:
        """Returns the stored graph as an adjacency list."""
        return self.contents

    @property
    def edges(self) -> composites.Edges:
        """Returns the stored graph as an edge list."""
        return utilities.adjacency_to_edges(item = self.contents)

    @property
    def endpoints(self) -> set[composites.Node]:
        """Returns endpoint nodes in the stored graph in a list."""
        return {k for k in self.contents.keys() if not self.contents[k]}

    @property
    def matrix(self) -> composites.Matrix:
        """Returns the stored graph as an adjacency matrix."""
        return utilities.adjacency_to_matrix(item = self.contents)
                      
    @property
    def nodes(self) -> set[composites.Node]:
        """Returns all stored nodes in a list."""
        return set(self.contents.keys())

    @property
    def paths(self) -> composites.Nodes:
        """Returns all paths through the stored as a list of Nodes."""
        return self._find_all_paths(starts = self.roots, stops = self.endpoints)
    
    @property
    def pipeline(self) -> composites.Pipeline:
        """Returns stored graph as a Pipeline."""
        raise NotImplementedError
    
    @property
    def pipelines(self) -> composites.Pipelines:
        """Returns stored graph as a Pipelines."""
        all_paths = self.paths
        instances = [chrisjen.Process(contents = p) for p in all_paths]
        return chrisjen.Processes(contents = instances)
    
    @property
    def roots(self) -> set[composites.Node]:
        """Returns root nodes in the stored graph in a list."""
        stops = list(itertools.chain.from_iterable(self.contents.values()))
        return {k for k in self.contents.keys() if k not in stops}
    
    """ Class Methods """
 
    @classmethod
    def from_adjacency(cls, item: composites.Adjacency) -> System:
        """Creates a System instance from an adjacency list."""
        return cls(contents = item)
    
    @classmethod
    def from_edges(cls, item: composites.Edges) -> System:
        """Creates a System instance from an edge list."""
        return cls(contents = composites.edges_to_adjacency(item = item))
    
    @classmethod
    def from_matrix(cls, item: composites.Matrix) -> System:
        """Creates a System instance from an adjacency matrix."""
        return cls(contents = composites.matrix_to_adjacency(item = item))
    
    @classmethod
    def from_pipeline(cls, item: composites.Pipeline) -> System:
        """Creates a System instance from a Pipeline."""
        new_contents = composites.pipeline_to_adjacency(item = item)
        return cls(contents = new_contents)

    @classmethod
    def from_pipelines(cls, item: composites.Pipelines) -> System:
        """Creates a System instance from a Pipeline."""
        new_contents = composites.pipelines_to_adjacency(item = item)
        return cls(contents = new_contents)

    @classmethod
    def from_tree(cls, item: composites.Tree) -> System:
        """Creates a System instance from a Tree."""
        raise NotImplementedError
             
    """ Public Methods """

    def add(
        self, 
        node: composites.Node,
        ancestors: composites.Nodes = None,
        descendants: composites.Nodes = None) -> None:
        """Adds 'node' to the stored graph.
        
        Args:
            node (composites.Node): a node to add to the stored graph.
            ancestors (composites.Nodes): node(s) from which 'node' should be 
                connected.
            descendants (composites.Nodes): node(s) to which 'node' should be 
                connected.

        Raises:
            KeyError: if some nodes in 'descendants' or 'ancestors' are not in 
                the stored graph.
                
        """
        if descendants is None:
            self.contents[node] = set()
        # elif utilities.is_property(item = descendants, instance = self):
        #     self.contents = set(getattr(self, descendants))
        else:
            descendants = list(utilities.iterify(item = descendants))
            descendants = [utilities.get_name(item = n) for n in descendants]
            missing = [n for n in descendants if n not in self.contents]
            if missing:
                raise KeyError(
                    f'descendants {str(missing)} are not in '
                    f'{self.__class__.__name__}')
            else:
                self.contents[node] = set(descendants)
        if ancestors is not None:  
            # if utilities.is_property(item = ancestors, instance = self):
            #     start = list(getattr(self, ancestors))
            # else:
            ancestors = list(utilities.iterify(item = ancestors))
            missing = [n for n in ancestors if n not in self.contents]
            if missing:
                raise KeyError(
                    f'ancestors {str(missing)} are not in '
                    f'{self.__class__.__name__}')
            for start in ancestors:
                if node not in self[start]:
                    self.connect(start = start, stop = node)                 
        return 

    def append(self, item: Union[composites.Composite]) -> None:
        """Appends 'item' to the endpoints of the stored graph.

        Appending creates an edge between every endpoint of this instance's
        stored graph and the every root of 'item'.

        Args:
            item (Union[composites.Composite]): another Graph, 
                an adjacency list, an edge list, an adjacency matrix, or one or
                more nodes.
            
        Raises:
            TypeError: if 'item' is neither a Graph, composites.Adjacency, composites.Edges, composites.Matrix,
                or composites.Nodes type.
                
        """
        if isinstance(item, composites.Composite):
            current_endpoints = list(self.endpoints)
            new_graph = self.create(item = item)
            self.merge(item = new_graph)
            for endpoint in current_endpoints:
                for root in new_graph.roots:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError(
                'item must be a System, Adjacency, Edges, Matrix, Pipeline, '
                'Pipelines, or Node type')
        return
  
    def connect(self, start: composites.Node, stop: composites.Node) -> None:
        """Adds an edge from 'start' to 'stop'.

        Args:
            start (composites.Node): name of node for edge to start.
            stop (composites.Node): name of node for edge to stop.
            
        Raises:
            ValueError: if 'start' is the same as 'stop'.
            
        """
        if start == stop:
            raise ValueError(
                'The start of an edge cannot be the same as the '
                'stop in a System because it is acyclic')
        elif start not in self:
            self.add(node = start)
        elif stop not in self:
            self.add(node = stop)
        if stop not in self.contents[start]:
            self.contents[start].add(utilities.get_name(item = stop))
        return

    def delete(self, node: composites.Node) -> None:
        """Deletes node from graph.
        
        Args:
            node (composites.Node): node to delete from 'contents'.
        
        Raises:
            KeyError: if 'node' is not in 'contents'.
            
        """
        try:
            del self.contents[node]
        except KeyError:
            raise KeyError(f'{node} does not exist in the graph')
        self.contents = {k: v.discard(node) for k, v in self.contents.items()}
        return

    def disconnect(self, start: composites.Node, stop: composites.Node) -> None:
        """Deletes edge from graph.

        Args:
            start (composites.Node): starting node for the edge to delete.
            stop (composites.Node): ending node for the edge to delete.
        
        Raises:
            KeyError: if 'start' is not a node in the stored graph..

        """
        try:
            self.contents[start].discard(stop)
        except KeyError:
            raise KeyError(f'{start} does not exist in the graph')
        return

    def merge(self, item: Union[composites.Composite]) -> None:
        """Adds 'item' to this Graph.

        This method is roughly equivalent to a dict.update, just adding the
        new keys and values to the existing graph. It converts 'item' to an 
        adjacency list that is then added to the existing 'contents'.
        
        Args:
            item (Union[composites.Composite]): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, composites.Adjacency, composites.Edges, composites.Matrix, 
                or composites.Nodes type.
            
        """
        if isinstance(item, System):
            adjacency = item.adjacency
        elif isinstance(item, composites.Adjacency):
            adjacency = item
        elif isinstance(item, composites.Edges):
            adjacency = composites.edges_to_adjacency(item = item)
        elif isinstance(item, composites.Matrix):
            adjacency = composites.matrix_to_adjacency(item = item)
        elif isinstance(item, (list, tuple, set)):
            adjacency = composites.pipeline_to_adjacency(item = item)
        elif isinstance(item, composites.Node):
            adjacency = {item: set()}
        else:
            raise TypeError(
                'item must be a System, Adjacency, Edges, Matrix, Pipeline, '
                'Pipelines, or Node type')
        self.contents.update(adjacency)
        return

    def prepend(self, item: Union[composites.Composite]) -> None:
        """Prepends 'item' to the roots of the stored graph.

        Prepending creates an edge between every endpoint of 'item' and every
        root of this instance;s stored graph.

        Args:
            item (Union[composites.Composite]): another Graph, an adjacency list, an 
                edge list, an adjacency matrix, or one or more nodes.
            
        Raises:
            TypeError: if 'item' is neither a System, composites.Adjacency, composites.Edges, composites.Matrix, 
                or composites.Nodes type.
                
        """
        if isinstance(item, composites.Composite):
            current_roots = list(self.roots)
            new_graph = self.create(item = item)
            self.merge(item = new_graph)
            for root in current_roots:
                for endpoint in new_graph.endpoints:
                    self.connect(start = endpoint, stop = root)
        else:
            raise TypeError(
                'item must be a System, Adjacency, Edges, Matrix, Pipeline, '
                'Pipelines, or Node type')
        return
      
    def subset(
        self, 
        include: Union[Any, Sequence[Any]] = None,
        exclude: Union[Any, Sequence[Any]] = None) -> System:
        """Returns a new System without a subset of 'contents'.
        
        All edges will be removed that include any nodes that are not part of
        the new subgraph.
        
        Any extra attributes that are part of a System (or a subclass) will be
        maintained in the returned subgraph.

        Args:
            include (Union[Any, Sequence[Any]]): nodes which should be included
                with any applicable edges in the new subgraph.
            exclude (Union[Any, Sequence[Any]]): nodes which should not be 
                included with any applicable edges in the new subgraph.

        Returns:
           System: with only key/value pairs with keys not in 'subset'.

        """
        if include is None and exclude is None:
            raise ValueError('Either include or exclude must not be None')
        else:
            if include:
                excludables = [k for k in self.contents if k not in include]
            else:
                excludables = []
            excludables.extend([i for i in self.contents if i in exclude])
            new_graph = copy.deepcopy(self)
            for node in utilities.iterify(item = excludables):
                new_graph.delete(node = node)
        return new_graph
    
    def walk(
        self, 
        start: composites.Node,
        stop: composites.Node, 
        path: Optional[composites.Pipeline] = None) -> composites.Pipeline:
        """Returns all paths in graph from 'start' to 'stop'.

        The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
        Args:
            start (composites.Node): node to start paths from.
            stop (composites.Node): node to stop paths.
            path (composites.Pipeline): a path from 'start' to 'stop'. Defaults 
                to an empty list. 

        Returns:
            composites.Pipeline: a list of possible paths (each path is a list 
                nodes) from 'start' to 'stop'.
            
        """
        if path is None:
            path = []
        path = path + [start]
        if start == stop:
            return [path]
        if start not in self.contents:
            return []
        paths = []
        for node in self.contents[start]:
            if node not in path:
                new_paths = self.walk(
                    start = node, 
                    stop = stop, 
                    path = path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    """ Private Methods """

    def _find_all_paths(
        self, 
        starts: composites.Nodes, 
        stops: composites.Nodes) -> composites.Pipeline:
        """Returns all paths between 'starts' and 'stops'.

        Args:
            start (composites.Nodes): starting point(s) for paths through the 
                System.
            ends (composites.Nodes): ending point(s) for paths through the 
                System.

        Returns:
            composites.Pipeline: list of all paths through the System from all 
                'starts' to all 'ends'.
            
        """
        all_paths = []
        for start in utilities.iterify(item = starts):
            for end in utilities.iterify(item = stops):
                paths = self.walk(start = start, stop = end)
                if paths:
                    if all(isinstance(path, composites.Node) for path in paths):
                        all_paths.append(paths)
                    else:
                        all_paths.extend(paths)
        return all_paths
    
    """ Dunder Methods """

    def __add__(self, other: Union[composites.Composite]) -> None:
        """Adds 'other' to the stored graph using the 'append' method.

        Args:
            other (Union[composites.Composite]): another Graph, adjacency list, 
                an edge list, an adjacency matrix, or one or more nodes.
            
        """
        self.append(item = other)     
        return 

    def __radd__(self, other: Union[composites.Composite]) -> None:
        """Adds 'other' to the stored graph using the 'prepend' method.

        Args:
            other (Union[composites.Composite]): another Graph, adjacency list, 
                an edge list, an adjacency matrix, or one or more nodes.
            
        """
        self.prepend(item = other)     
        return 


# @dataclasses.dataclass
# class Network(composites.Graph):
#     """Base class for undirected graphs with unweighted edges.
    
#     Graph stores a directed acyclic graph (DAG) as an adjacency list. Despite 
#     being called an adjacency "list," the typical and most efficient way to 
#     store one is using a python dict. a chrisjen Graph inherits from a Lexicon 
#     in order to allow use of its extra functionality over a plain dict.
    
#     Graph supports '+' and '+=' to be used to join two chrisjen Graph instances. A
#     properly formatted adjacency list could also be the added object.
    
#     Graph internally supports autovivification where a list is created as a 
#     value for a missing key. This means that a Graph need not inherit from 
#     defaultdict.
    
#     Args:
#         contents (composites.Adjacency): an adjacency list where the keys are nodes and the 
#             values are nodes which the key is connected to. Defaults to an empty 
#             dict.
                  
#     """  
#     contents: composites.Matrix = dataclasses.field(default_factory = dict)
    
#     """ Properties """

#     @property
#     def adjacency(self) -> composites.Adjacency:
#         """Returns the stored graph as an adjacency list."""
#         return composites.matrix_to_adjacency(item = self.contents)

#     @property
#     def breadths(self) -> composites.Pipeline:
#         """Returns all paths through the Graph using breadth-first search.
        
#         Returns:
#             composites.Pipeline: returns all paths from 'roots' to 'endpoints' in a list 
#                 of lists of nodes.
                
#         """
#         return self._find_all_paths(
#             starts = self.roots, 
#             ends = self.endpoints,
#             depth_first = False)

#     @property
#     def depths(self) -> composites.Pipeline:
#         """Returns all paths through the Graph using depth-first search.
        
#         Returns:
#             composites.Pipeline: returns all paths from 'roots' to 'endpoints' in a list 
#                 of lists of nodes.
                
#         """
#         return self._find_all_paths(starts = self.roots, 
#                                     ends = self.endpoints,
#                                     depth_first = True)
     
#     @property
#     def edges(self) -> composites.Edges:
#         """Returns the stored graph as an edge list."""
#         return adjacency_to_edges(item = self.contents)

#     @property
#     def endpoints(self) -> list[composites.Node]:
#         """Returns a list of endpoint nodes in the stored graph.."""
#         return [k for k in self.contents.keys() if not self.contents[k]]

#     @property
#     def matrix(self) -> composites.Matrix:
#         """Returns the stored graph as an adjacency matrix."""
#         return adjacency_to_matrix(item = self.contents)
                      
#     @property
#     def nodes(self) -> dict[str, composites.Node]:
#         """Returns a dict of node names as keys and nodes as values.
        
#         Because Graph allows various composites.Node objects to be used as keys,
#         including the composites.Nodes class, there isn't an obvious way to access already
#         stored nodes. This property creates a new dict with str keys derived
#         from the nodes (looking first for a 'name' attribute) so that a user
#         can access a node. 
        
#         This property is not needed if the stored nodes are all strings.
        
#         Returns:
#             Dict[str, composites.Node]: keys are the name or has of nodes and the 
#                 values are the nodes themselves.
            
#         """
#         return {self.utilities.get_name(item = n): n for n in self.contents.keys()}
  
#     @property
#     def roots(self) -> list[composites.Node]:
#         """Returns root nodes in the stored graph..

#         Returns:
#             list[composites.Node]: root nodes.
            
#         """
#         stops = list(itertools.chain.from_iterable(self.contents.values()))
#         return [k for k in self.contents.keys() if k not in stops]
    
#     """ Class Methods """
    
#     @classmethod
#     def create(cls, item: Union[composites.Adjacency, composites.Edges, composites.Matrix]) -> Graph:
#         """Creates an instance of a Graph from 'item'.
        
#         Args:
#             item (Union[composites.Adjacency, composites.Edges, composites.Matrix]): an adjacency list, 
#                 adjacency matrix, or edge list which can used to create the
#                 stored graph.
                
#         Returns:
#             Graph: a Graph instance created based on 'item'.
                
#         """
#         if is_adjacency_list(item = item):
#             return cls.from_adjacency(adjacency = item)
#         elif is_adjacency_matrix(item = item):
#             return cls.from_matrix(matrix = item)
#         elif is_edge_list(item = item):
#             return cls.from_adjacency(edges = item)
#         else:
#             raise TypeError(
#                 f'create requires item to be an adjacency list, adjacency '
#                 f'matrix, or edge list')
           
#     @classmethod
#     def from_adjacency(cls, adjacency: composites.Adjacency) -> Graph:
#         """Creates a Graph instance from an adjacency list.
        
#         'adjacency' should be formatted with nodes as keys and values as lists
#         of names of nodes to which the node in the key is connected.

#         Args:
#             adjacency (composites.Adjacency): adjacency list used to 
#                 create a Graph instance.

#         Returns:
#             Graph: a Graph instance created based on 'adjacent'.
              
#         """
#         return cls(contents = adjacency)
    
#     @classmethod
#     def from_edges(cls, edges: composites.Edges) -> Graph:
#         """Creates a Graph instance from an edge list.

#         'edges' should be a list of tuples, where the first item in the tuple
#         is the node and the second item is the node (or name of node) to which
#         the first item is connected.
        
#         Args:
#             edges (composites.Edges): Edge list used to create a Graph 
#                 instance.
                
#         Returns:
#             Graph: a Graph instance created based on 'edges'.

#         """
#         return cls(contents = edges_to_adjacency(item = edges))
    
#     @classmethod
#     def from_matrix(cls, matrix: composites.Matrix) -> Graph:
#         """Creates a Graph instance from an adjacency matrix.

#         Args:
#             matrix (composites.Matrix): adjacency matrix used to create a Graph instance. 
#                 The values in the matrix should be 1 (indicating an edge) and 0 
#                 (indicating no edge).
 
#         Returns:
#             Graph: a Graph instance created based on 'matrix'.
                        
#         """
#         return cls(contents = matrix_to_adjacency(item = matrix))
    
#     @classmethod
#     def from_pipeline(cls, pipeline: composites.Pipeline) -> Graph:
#         """Creates a Graph instance from a composites.Pipeline.

#         Args:
#             pipeline (composites.Pipeline): serial pipeline used to create a Graph
#                 instance.
 
#         Returns:
#             Graph: a Graph instance created based on 'pipeline'.
                        
#         """
#         return cls(contents = pipeline_to_adjacency(item = pipeline))
       
#     """ Public Methods """
    
#     def add(self, 
#             node: composites.Node,
#             ancestors: composites.Nodes = None,
#             descendants: composites.Nodes = None) -> None:
#         """Adds 'node' to 'contents' with no corresponding edges.
        
#         Args:
#             node (composites.Node): a node to add to the stored graph.
#             ancestors (composites.Nodes): node(s) from which node should be connected.
#             descendants (composites.Nodes): node(s) to which node should be connected.

#         """
#         if descendants is None:
#             self.contents[node] = []
#         elif descendants in self:
#             self.contents[node] = utilities.iterify(item = descendants)
#         else:
#             missing = [n for n in descendants if n not in self.contents]
#             raise KeyError(f'descendants {missing} are not in the stored graph.')
#         if ancestors is not None:  
#             if (isinstance(ancestors, composites.Node) and ancestors in self
#                     or (isinstance(ancestors, (list, tuple, set)) 
#                         and all(isinstance(n, composites.Node) for n in ancestors)
#                         and all(n in self.contents for n in ancestors))):
#                 start = ancestors
#             elif (hasattr(self.__class__, ancestors) 
#                     and isinstance(getattr(type(self), ancestors), property)):
#                 start = getattr(self, ancestors)
#             else:
#                 missing = [n for n in ancestors if n not in self.contents]
#                 raise KeyError(f'ancestors {missing} are not in the stored graph.')
#             for starting in utilities.iterify(item = start):
#                 if node not in [starting]:
#                     self.connect(start = starting, stop = node)                 
#         return 

#     def append(self, 
#                item: Union[Graph, composites.Adjacency, composites.Edges, composites.Matrix, composites.Nodes]) -> None:
#         """Adds 'item' to this Graph.

#         Combining creates an edge between every endpoint of this instance's
#         Graph and the every root of 'item'.

#         Args:
#             item (Union[Graph, composites.Adjacency, composites.Edges, composites.Matrix, composites.Nodes]): another 
#                 Graph to join with this one, an adjacency list, an edge list, an
#                 adjacency matrix, or composites.Nodes.
            
#         Raises:
#             TypeError: if 'item' is neither a Graph, composites.Adjacency, composites.Edges, composites.Matrix,
#                 or composites.Nodes type.
            
#         """
#         if isinstance(item, Graph):
#             if self.contents:
#                 current_endpoints = self.endpoints
#                 self.contents.update(item.contents)
#                 for endpoint in current_endpoints:
#                     for root in item.roots:
#                         self.connect(start = endpoint, stop = root)
#             else:
#                 self.contents = item.contents
#         elif isinstance(item, composites.Adjacency):
#             self.append(item = self.from_adjacency(adjacecny = item))
#         elif isinstance(item, composites.Edges):
#             self.append(item = self.from_edges(edges = item))
#         elif isinstance(item, composites.Matrix):
#             self.append(item = self.from_matrix(matrix = item))
#         elif isinstance(item, composites.Nodes):
#             if isinstance(item, (list, tuple, set)):
#                 new_graph = Graph()
#                 edges = more_itertools.windowed(item, 2)
#                 for edge_pair in edges:
#                     new_graph.add(node = edge_pair[0], descendants = edge_pair[1])
#                 self.append(item = new_graph)
#             else:
#                 self.add(node = item)
#         else:
#             raise TypeError(
#                 'item must be a Graph, composites.Adjacency, composites.Edges, composites.Matrix, or composites.Nodes '
#                 'type')
#         return
  
#     def connect(self, start: composites.Node, stop: composites.Node) -> None:
#         """Adds an edge from 'start' to 'stop'.

#         Args:
#             start (composites.Node): name of node for edge to start.
#             stop (composites.Node): name of node for edge to stop.
            
#         Raises:
#             ValueError: if 'start' is the same as 'stop'.
            
#         """
#         if start == stop:
#             raise ValueError(
#                 'The start of an edge cannot be the same as the stop')
#         else:
#             if stop not in self.contents:
#                 self.add(node = stop)
#             if start not in self.contents:
#                 self.add(node = start)
#             if stop not in self.contents[start]:
#                 self.contents[start].append(self.utilities.get_name(item = stop))
#         return

#     def delete(self, node: composites.Node) -> None:
#         """Deletes node from graph.
        
#         Args:
#             node (composites.Node): node to delete from 'contents'.
        
#         Raises:
#             KeyError: if 'node' is not in 'contents'.
            
#         """
#         try:
#             del self.contents[node]
#         except KeyError:
#             raise KeyError(f'{node} does not exist in the graph')
#         self.contents = {
#             k: v.remove(node) for k, v in self.contents.items() if node in v}
#         return

#     def disconnect(self, start: composites.Node, stop: composites.Node) -> None:
#         """Deletes edge from graph.

#         Args:
#             start (composites.Node): starting node for the edge to delete.
#             stop (composites.Node): ending node for the edge to delete.
        
#         Raises:
#             KeyError: if 'start' is not a node in the stored graph..
#             ValueError: if 'stop' does not have an edge with 'start'.

#         """
#         try:
#             self.contents[start].remove(stop)
#         except KeyError:
#             raise KeyError(f'{start} does not exist in the graph')
#         except ValueError:
#             raise ValueError(f'{stop} is not connected to {start}')
#         return

#     def merge(self, item: Union[Graph, composites.Adjacency, composites.Edges, composites.Matrix]) -> None:
#         """Adds 'item' to this Graph.

#         This method is roughly equivalent to a dict.update, just adding the
#         new keys and values to the existing graph. It converts the supported
#         formats to an adjacency list that is then added to the existing 
#         'contents'.
        
#         Args:
#             item (Union[Graph, composites.Adjacency, composites.Edges, composites.Matrix]): another Graph to 
#                 add to this one, an adjacency list, an edge list, or an
#                 adjacency matrix.
            
#         Raises:
#             TypeError: if 'item' is neither a Graph, composites.Adjacency, composites.Edges, or 
#                 composites.Matrix type.
            
#         """
#         if isinstance(item, Graph):
#             item = item.contents
#         elif isinstance(item, composites.Adjacency):
#             pass
#         elif isinstance(item, composites.Edges):
#             item = self.from_edges(edges = item).contents
#         elif isinstance(item, composites.Matrix):
#             item = self.from_matrix(matrix = item).contents
#         else:
#             raise TypeError(
#                 'item must be a Graph, composites.Adjacency, composites.Edges, or composites.Matrix type to '
#                 'update')
#         self.contents.update(item)
#         return
  
#     def subgraph(self, 
#                  include: Union[Any, Sequence[Any]] = None,
#                  exclude: Union[Any, Sequence[Any]] = None) -> Graph:
#         """Returns a new Graph without a subset of 'contents'.
        
#         All edges will be removed that include any nodes that are not part of
#         the new subgraph.
        
#         Any extra attributes that are part of a Graph (or a subclass) will be
#         maintained in the returned subgraph.

#         Args:
#             include (Union[Any, Sequence[Any]]): nodes which should be included
#                 with any applicable edges in the new subgraph.
#             exclude (Union[Any, Sequence[Any]]): nodes which should not be 
#                 included with any applicable edges in the new subgraph.

#         Returns:
#             Graph: with only key/value pairs with keys not in 'subset'.

#         """
#         if include is None and exclude is None:
#             raise ValueError('Either include or exclude must not be None')
#         else:
#             if include:
#                 excludables = [k for k in self.contents if k not in include]
#             else:
#                 excludables = []
#             excludables.extend([i for i in self.contents if i not in exclude])
#             new_graph = copy.deepcopy(self)
#             for node in utilities.iterify(item = excludables):
#                 new_graph.delete(node = node)
#         return new_graph

#     def walk(self, 
#              start: composites.Node, 
#              stop: composites.Node, 
#              path: composites.Pipeline = None,
#              depth_first: bool = True) -> composites.Pipeline:
#         """Returns all paths in graph from 'start' to 'stop'.

#         The code here is adapted from: https://www.python.org/doc/essays/graphs/
        
#         Args:
#             start (composites.Node): node to start paths from.
#             stop (composites.Node): node to stop paths.
#             path (composites.Pipeline): a path from 'start' to 'stop'. Defaults to an 
#                 empty list. 

#         Returns:
#             composites.Pipeline: a list of possible paths (each path is a list 
#                 nodes) from 'start' to 'stop'.
            
#         """
#         if path is None:
#             path = []
#         path = path + [start]
#         if start == stop:
#             return [path]
#         if start not in self.contents:
#             return []
#         if depth_first:
#             method = self._depth_first_search
#         else:
#             method = self._breadth_first_search
#         paths = []
#         for node in self.contents[start]:
#             if node not in path:
#                 new_paths = self.walk(
#                     start = node, 
#                     stop = stop, 
#                     path = path,
#                     depth_first = depth_first)
#                 for new_path in new_paths:
#                     paths.append(new_path)
#         return paths

#     def _all_paths_bfs(self, start, stop):
#         """

#         """
#         if start == stop:
#             return [start]
#         visited = {start}
#         queue = collections.deque([(start, [])])
#         while queue:
#             current, path = queue.popleft()
#             visited.add(current)
#             for connected in self[current]:
#                 if connected == stop:
#                     return path + [current, connected]
#                 if connected in visited:
#                     continue
#                 queue.append((connected, path + [current]))
#                 visited.add(connected)   
#         return []

#     def _breadth_first_search(self, node: composites.Node) -> composites.Pipeline:
#         """Returns a breadth first search path through the Graph.

#         Args:
#             node (composites.Node): node to start the search from.

#         Returns:
#             composites.Pipeline: nodes in a path through the Graph.
            
#         """        
#         visited = set()
#         queue = [node]
#         while queue:
#             vertex = queue.pop(0)
#             if vertex not in visited:
#                 visited.add(vertex)
#                 queue.extend(set(self[vertex]) - visited)
#         return list(visited)
       
#     def _depth_first_search(self, 
#         node: composites.Node, 
#         visited: list[composites.Node]) -> composites.Pipeline:
#         """Returns a depth first search path through the Graph.

#         Args:
#             node (composites.Node): node to start the search from.
#             visited (list[composites.Node]): list of visited nodes.

#         Returns:
#             composites.Pipeline: nodes in a path through the Graph.
            
#         """  
#         if node not in visited:
#             visited.append(node)
#             for edge in self[node]:
#                 self._depth_first_search(node = edge, visited = visited)
#         return visited
  
#     def _find_all_paths(self, 
#         starts: Union[composites.Node, Sequence[composites.Node]],
#         stops: Union[composites.Node, Sequence[composites.Node]],
#         depth_first: bool = True) -> composites.Pipeline:
#         """[summary]

#         Args:
#             start (Union[composites.Node, Sequence[composites.Node]]): starting points for 
#                 paths through the Graph.
#             ends (Union[composites.Node, Sequence[composites.Node]]): endpoints for paths 
#                 through the Graph.

#         Returns:
#             composites.Pipeline: list of all paths through the Graph from all
#                 'starts' to all 'ends'.
            
#         """
#         all_paths = []
#         for start in utilities.iterify(item = starts):
#             for end in utilities.iterify(item = stops):
#                 paths = self.walk(
#                     start = start, 
#                     stop = end,
#                     depth_first = depth_first)
#                 if paths:
#                     if all(isinstance(path, composites.Node) for path in paths):
#                         all_paths.append(paths)
#                     else:
#                         all_paths.extend(paths)
#         return all_paths
            
#     """ Dunder Methods """

#     def __add__(self, other: composites.Graph) -> None:
#         """Adds 'other' Graph to this Graph.

#         Adding another graph uses the 'merge' method. Read that method's 
#         docstring for further details about how the graphs are added 
#         together.
        
#         Args:
#             other (Graph): a second Graph to join with this one.
            
#         """
#         self.merge(graph = other)        
#         return

#     def __iadd__(self, other: Graph) -> None:
#         """Adds 'other' Graph to this Graph.

#         Adding another graph uses the 'merge' method. Read that method's 
#         docstring for further details about how the graphs are added 
#         together.
        
#         Args:
#             other (Graph): a second Graph to join with this one.
            
#         """
#         self.merge(graph = other)        
#         return

#     def __contains__(self, nodes: composites.Nodes) -> bool:
#         """[summary]

#         Args:
#             nodes (composites.Nodes): [description]

#         Returns:
#             bool: [description]
            
#         """
#         if isinstance(nodes, (list, tuple, set)):
#             return all(n in self.contents for n in nodes)
#         elif isinstance(nodes, composites.Node):
#             return nodes in self.contents
#         else:
#             return False   
        
#     def __getitem__(self, key: composites.Node) -> Any:
#         """Returns value for 'key' in 'contents'.

#         Args:
#             key (composites.Node): key in 'contents' for which a value is sought.

#         Returns:
#             Any: value stored in 'contents'.

#         """
#         return self.contents[key]

#     def __setitem__(self, key: composites.Node, value: Any) -> None:
#         """sets 'key' in 'contents' to 'value'.

#         Args:
#             key (composites.Node): key to set in 'contents'.
#             value (Any): value to be paired with 'key' in 'contents'.

#         """
#         self.contents[key] = value
#         return

#     def __delitem__(self, key: composites.Node) -> None:
#         """Deletes 'key' in 'contents'.

#         Args:
#             key (composites.Node): key in 'contents' to delete the key/value pair.

#         """
#         del self.contents[key]
#         return

#     def __missing__(self) -> list:
#         """Returns an empty list when a key doesn't exist.

#         Returns:
#             list: an empty list.

#         """
#         return []
    
#     def __str__(self) -> str:
#         """Returns prettier summary of the Graph.

#         Returns:
#             str: a formatted str of class information and the contained 
#                 adjacency list.
            
#         """
#         new_line = '\n'
#         tab = '    '
#         summary = [f'{new_line}chrisjen {self.__class__.__name__}']
#         summary.append('adjacency list:')
#         for node, edges in self.contents.items():
#             summary.append(f'{tab}{node}: {str(edges)}')
#         return new_line.join(summary) 

