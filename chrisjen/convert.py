"""
composites: base classes and functions for lightweight composite data structures
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
    Complete functions that are presently not implemented.
    Add in 'dispatcher' decorators to the converter functions.
    
"""
from __future__ import annotations
import abc
import collections
from collections.abc import (
    Collection, Hashable, MutableMapping, MutableSequence, Sequence, Set)
import dataclasses
from typing import (
    Any, Callable, ClassVar, Optional, Type, TYPE_CHECKING, TypeVar, Union)

import more_itertools

from . import check
   
if TYPE_CHECKING:
    from . import graph
    from . import manifest
    from . import proxy
    from . import tree
    
""" Converters """

# @amos.dispatcher 
def to_adjacency(item: Any) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.
    
    Args:
        item (Any): item to convert to an graph.Adjacency.

    Raises:
        TypeError: if 'item' is a type that is not registered with the 
        dispatcher.

    Returns:
        graph.Adjacency: derived from 'item'.

    """
    if check.is_adjacency(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_adjacency.register # type: ignore
def edges_to_adjacency(item: graph.Edges) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.

    Args:
        item (graph.Edges): item to convert to an graph.Adjacency.

    Returns:
        graph.Adjacency: derived from 'item'.

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
def matrix_to_adjacency(item: graph.Matrix) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.

    Args:
        item (graph.Matrix): item to convert to an graph.Adjacency.

    Returns:
        graph.Adjacency: derived from 'item'.

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
def pipeline_to_adjacency(item: manifest.Pipeline) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.

    Args:
        item (manifest.Pipeline): item to convert to an graph.Adjacency.

    Returns:
        graph.Adjacency: derived from 'item'.

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
def pipelines_to_adjacency(item: manifest.Pipelines) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.

    Args:
        item (manifest.Pipelines): item to convert to an graph.Adjacency.

    Returns:
        graph.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    for _, pipeline in item.items():
        adjacency.update(pipeline_to_adjacency(item = pipeline))
    return adjacency

# @to_adjacency.register # type: ignore 
def tree_to_adjacency(item: tree.Tree) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.

    Args:
        item (tree.Tree): item to convert to an graph.Adjacency.

    Returns:
        graph.Adjacency: derived from 'item'.

    """
    raise NotImplementedError
             
# @to_adjacency.register # type: ignore 
def nodes_to_adjacency(item: proxy.Nodes) -> graph.Adjacency:
    """Converts 'item' to an graph.Adjacency.

    Args:
        item (proxy.Nodes): item to convert to an graph.Adjacency.

    Returns:
        graph.Adjacency: derived from 'item'.

    """
    adjacency = collections.defaultdict(set)
    return adjacency.update((k, set()) for k in item)

# @amos.dispatcher   
def to_edges(item: Any) -> graph.Edges:
    """Converts 'item' to an graph.Edges.
    
    Args:
        item (Any): item to convert to an graph.Edges.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        graph.Edges: derived from 'item'.

    """
    if check.is_edges(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')
    
# @to_edges.register # type: ignore
def adjacency_to_edges(item: graph.Adjacency) -> graph.Edges:
    """Converts 'item' to an graph.Edges.
    
    Args:
        item (graph.Adjacency): item to convert to an graph.Edges.

    Returns:
        graph.Edges: derived from 'item'.

    """ 
    edges = []
    for node, connections in item.items():
        for connection in connections:
            edges.append(tuple(node, connection))
    return tuple(edges)

# @amos.dispatcher   
def to_matrix(item: Any) -> graph.Matrix:
    """Converts 'item' to a graph.Matrix.
    
    Args:
        item (Any): item to convert to a graph.Matrix.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        graph.Matrix: derived from 'item'.

    """
    if check.is_matrix(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_matrix.register # type: ignore 
def adjacency_to_matrix(item: graph.Adjacency) -> graph.Matrix:
    """Converts 'item' to a graph.Matrix.
    
    Args:
        item (graph.Adjacency): item to convert to a graph.Matrix.

    Returns:
        graph.Matrix: derived from 'item'.

    """ 
    names = list(item.keys())
    matrix = []
    for i in range(len(item)): 
        matrix.append([0] * len(item))
        for j in item[i]:
            matrix[i][j] = 1
    return tuple(matrix, names)    

# @amos.dispatcher   
def to_tree(item: Any) -> tree.Tree:
    """Converts 'item' to a tree.Tree.
    
    Args:
        item (Any): item to convert to a tree.Tree.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        tree.Tree: derived from 'item'.

    """
    if check.is_tree(item = item):
        return item
    else:
        raise TypeError(
            f'item cannot be converted because it is an unsupported type: '
            f'{type(item).__name__}')

# @to_tree.register # type: ignore 
def matrix_to_tree(item: graph.Matrix) -> tree.Tree:
    """Converts 'item' to a tree.Tree.
    
    Args:
        item (graph.Matrixy): item to convert to a tree.Tree.

    Raises:
        TypeError: if 'item' is a type that is not registered.

    Returns:
        tree.Tree: derived from 'item'.

    """
    tree = {}
    for node in item:
        children = item[:]
        children.remove(node)
        tree[node] = matrix_to_tree(children)
    return tree

 