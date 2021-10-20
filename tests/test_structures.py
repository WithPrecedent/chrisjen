"""
test_structures: unit tests for chrisjen structures
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
import dataclasses
import inspect 
import sys
import types

import chrisjen

sys.setrecursionlimit = 5000

@dataclasses.dataclass
class Something(chrisjen.Node):
    
    pass


@dataclasses.dataclass
class AnotherThing(chrisjen.Node):
    
    pass


@dataclasses.dataclass
class EvenAnother(chrisjen.Node):
    
    pass


def test_graph() -> None:
    edges = tuple([('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')])
    dag = chrisjen.System.from_edges(item = edges)
    dag.add(node = 'cat')
    dag.add(node = 'dog', ancestors = 'e', descendants = ['cat'])
    adjacency = {
        'tree': {'house', 'yard'},
        'house': set(),
        'yard': set()}
    another_dag = chrisjen.System.from_adjacency(item = adjacency)
    dag.append(item = another_dag)
    print('test print dag', dag)
    return

def test_pipeline() -> None:
    return

def test_tree() -> None:
    
    return


if __name__ == '__main__':
    test_graph()
    test_pipeline()
    test_tree()
    