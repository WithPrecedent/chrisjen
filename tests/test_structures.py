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
    # print('test dir', dir(chrisjen.System))
    # item = chrisjen.System
    # directory = dir(item)
    # attribute = directory[-1]
    # if isinstance(attribute, str):
    #     try:
    #         attribute = getattr(item, attribute)
    #     except AttributeError:
    #         pass
    # print('test attribute type', attribute, type(attribute))
    # print('test is method', isinstance(attribute, types.FunctionType))
    # methods = [
    #     a for a in dir(chrisjen.System)
    #     if chrisjen.is_method(item = chrisjen.System, attribute = a)]
    # print('test methods', methods)
    edges = tuple([('a', 'b'), ('c', 'd'), ('a', 'd'), ('d', 'e')])
    dag = chrisjen.System.create(item = edges)
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
    