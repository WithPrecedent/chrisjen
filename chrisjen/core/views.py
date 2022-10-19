"""
views: classes and functions related to stages of a chrisjen project
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2022, Corey Rayburn Yung
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
    Workflow
    Results
    create_workflow
    create_results

To Do:

        
"""
from __future__ import annotations
import collections
from collections.abc import (
    Hashable, Mapping, MutableMapping, MutableSequence, Set)
import dataclasses
import itertools
import pathlib
from typing import Any, ClassVar, Optional, Type, Union

import amos
import bobbie
import holden

from .core import base
from .core import parsers


# @dataclasses.dataclass
# class Summary(amos.Dictionary):
#     """Reports from completion of a chrisjen project.
    
#     Args:
#         contents (MutableMapping[Hashable, Any]): stored dictionary. Defaults 
#             to an empty dict.
#         default_factory (Optional[Any]): default value to return or default 
                          
#     """
#     contents: MutableMapping[Hashable, Any] = dataclasses.field(
#         default_factory = dict)
#     default_factory: Optional[Any] = None
    
#     """ Public Methods """

#     @classmethod
#     def create(cls, project: base.Project) -> Summary:
#         """[summary]

#         Args:
#             project (base.Project): [description]

#         Returns:
#             Results: [description]
            
#         """        
#         return workshop.create_results(project = project, base = cls)

#     # def complete(
#     #     self, 
#     #     project: base.Project, 
#     #     **kwargs) -> base.Project:
#     #     """Calls the 'implement' method the number of times in 'iterations'.

#     #     Args:
#     #         project (base.Project): instance from which data needed for 
#     #             implementation should be derived and all results be added.

#     #     Returns:
#     #         base.Project: with possible changes made.
            
#     #     """
#     #     if self.contents not in [None, 'None', 'none']:
#     #         for node in self:
#     #             project = node.complete(project = project, **kwargs)
#     #     return project
    
      
# """ Public Functions """
