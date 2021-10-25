"""
arrays: lightweight linear composite data structures
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

    
"""
from __future__ import annotations
import abc
from collections.abc import (
    Collection, Hashable, Mapping, MutableMapping, MutableSequence, Sequence)
import dataclasses
from typing import Any, Callable, ClassVar, Optional, Type, TypeVar, Union

from . import base
from . import check
from . import bunch
 
@dataclasses.dataclass # type: ignore
class Pipeline(bunch.Hybrid, base.Composite, abc.ABC):
    """Base class for pipeline data structures.
    
    Args:
        contents (MutableSequence[Node]): list of stored Node instances. 
            Defaults to an empty list.
          
    """
    contents: MutableSequence[base.Node] = dataclasses.field(
        default_factory = list)
    
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return check.is_pipeline(item = instance)
     
 
@dataclasses.dataclass # type: ignore
class Pipelines(bunch.Lexicon, base.Composite, abc.ABC):
    """Base class a collection of Pipeline instances.
        
    Args:
        contents (MutableMapping[Hashable, Pipeline]): keys are the name or 
            other identifier for the stored Pipeline instances and values are 
            Pipeline instances. Defaults to an empty dict.

    """
    contents: MutableMapping[Hashable, Pipeline] = dataclasses.field(
        default_factory = dict)
    
    """ Dunder Methods """
        
    @classmethod
    def __instancecheck__(cls, instance: object) -> bool:
        return check.is_pipelines(item = instance)
         