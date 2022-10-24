"""
directors: tools for constructing chrisjen project workflows
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
    UpFront (Builder): all nodes are created at the beginning of a project and 
        stored in a repository for when they are needed. This method is the 
        fastest.
    AsNeeded (Builder): nodes are created the first time that they are needed 
        and then stored in a repository of they are needed again. This method 
        balances speed and memory usage.
    OnlyAsNeeded (Builder): nodes are created only when needed and need to be 
        recreated if needed again. This method conserves memory the best.
        
To Do:

            
"""
# from __future__ import annotations
# import abc
# from collections.abc import Hashable, MutableMapping, MutableSequence
# import contextlib
# import dataclasses
# from typing import Any, ClassVar, Optional, Protocol, Type, TYPE_CHECKING, Union

# from ..core import base
# from ..core import foundry

    
# @dataclasses.dataclass
# class ProjectDirector(ProjectKeystone, abc.ABC):
#     """Constructor for chrisjen workflows.
        
#     Args:
#         project (Project): linked Project instance to modify and control.
             
#     """
#     project: Project
    
#     """ Initialization Methods """

#     def __post_init__(self) -> None:
#         """Initializes and validates class instance attributes."""
#         # Calls parent and/or mixin initialization method(s).
#         with contextlib.suppress(AttributeError):
#             super().__post_init__()
#         # Validates core attributes.
#         self.validate()
#         # Sets multiprocessing technique, if necessary.
#         workshop.set_parallelization(project = self.project)
#         # Completes 'project' if 'project.automatic' is True.
#         if self.project.automatic:
#             self.draft()
#             self.publish()
#             self.complete()
                                 
#     """ Required Subclass Methods """

#     @abc.abstractmethod
#     def draft(self, *args: Any, **kwargs: Any) -> None:
#         """Creates views of workflow components."""
#         pass

#     @abc.abstractmethod
#     def publish(self, *args: Any, **kwargs: Any) -> None:
#         """Creates node classes and/or instances."""
#         pass

#     @abc.abstractmethod
#     def complete(self, *args: Any, **kwargs: Any) -> None:
#         """Applies all workflow components to 'project'."""
#         pass

#     """ Public Methods """       
    
#     def validate(self) -> None:
#         """Validates or creates required portions of 'project'."""
#         self.project = validators.validate_settings(project = self.project)
#         self.project = validators.validate_name(project = self.project)
#         self.project = validators.validate_id(project = self.project)
#         self.project = validators.validate_clerk(project = self.project)
#         return
    
     
# @dataclasses.dataclass
# class UpFront(base.ProjectDirector):
#     """Constructor for chrisjen workflows.
        
#     Args:
#         project (base.Project): linked Project instance to modify and control.
             
#     """
#     project: base.Project
                                 
#     """ Public Methods """

#     def draft(self) -> None:
#         """Creates str representations of workflow components."""
#         self.project.outline = foundry.create_outline(project = self.project)
#         self.project.workflow = foundry.create_workflow(project = self.project)
#         return

#     def publish(self) -> None:
#         """Creates all component classes and instances."""
#         self.project.workflow.nodes = foundry.create_nodes(
#             project = self.project)
#         return 

#     def complete(self, *args: Any, **kwargs: Any) -> None:
#         """Applies all workflow components to 'project'."""
#         for worker in self.contents:
#             self.project = worker.complete(self.project, *args, **kwargs)
#         return 

 
# @dataclasses.dataclass
# class AsNeeded(base.ProjectDirector):
#     """Constructor for chrisjen workflows.
        
#     Args:
#         project (base.Project): linked Project instance to modify and control.
             
#     """
#     project: base.Project
                                 
#     """ Public Methods """

#     def draft(self, *args: Any, **kwargs: Any) -> None:
#         """Creates str representations of all workflow components."""
#         self.project = validators.validate_workers(self.project)
#         self.project = validators.validate_outline(self.project)
#         self.project = foundry.create_workers(self.project, *args, **kwargs)
#         return

#     def publish(self, *args: Any, **kwargs: Any) -> None:
#         """Creates all component classes and instances."""
#         for component in self.contents:
#             self.project = foundry.create_component(
#                 component,
#                 self.project, 
#                 *args, 
#                 **kwargs)
#         return 

#     def complete(self, *args: Any, **kwargs: Any) -> None:
#         """Applies all workflow components to 'project'."""
#         for worker in self.contents:
#             self.project = worker.complete(self.project, *args, **kwargs)
#         return 
  
   
# @dataclasses.dataclass
# class OnlyAsNeeded(base.ProjectDirector):
#     """Constructor for chrisjen workflows.
        
#     Args:
#         project (base.Project): linked Project instance to modify and control.
             
#     """
#     project: base.Project
                                 
#     """ Public Methods """

#     def draft(self, *args: Any, **kwargs: Any) -> None:
#         """Creates str representations of all workflow components."""
#         self.project = validators.validate_workers(self.project)
#         self.project = validators.validate_outline(self.project)
#         self.project = foundry.create_workers(self.project, *args, **kwargs)
#         return

#     def publish(self, *args: Any, **kwargs: Any) -> None:
#         """Creates all component classes and instances."""
#         for component in self.contents:
#             self.project = foundry.create_component(
#                 component,
#                 self.project, 
#                 *args, 
#                 **kwargs)
#         return 

#     def complete(self, *args: Any, **kwargs: Any) -> None:
#         """Applies all workflow components to 'project'."""
#         for worker in self.contents:
#             self.project = worker.complete(self.project, *args, **kwargs)
#         return 
    