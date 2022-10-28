"""
validators: validating functions
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

    
"""
from __future__ import annotations
import abc
from collections.abc import (
    Callable, Hashable, Mapping, MutableMapping, MutableSequence, Sequence)
import inspect
from typing import Any, ClassVar, Optional, Type, TYPE_CHECKING, Union

import amos
import miller

from . import workshop

if TYPE_CHECKING:
    from ..core import framework
    from ..core import keystones

    
def validate_workers(project: framework.Project) -> framework.Project:
    """Creates or validates 'project.manager.contents'.
    
    Args:
        project (framework.Project): project to examine and validate.
        
    Returns:
        framework.Project: validated framework.Project instance.
        
    """
    if not project.outline.workers:
        workers = [project.registry.keystones['worker']]
    else:
        names = project.outline.workers
        workers = []
        for name in names:
            workers.append(project.registry.workers[name])
    project.manager.contents = workers
    return project        
  
def validate_outline(project: framework.Project) -> framework.Project:
    """Creates or validates 'project.outline'.
    
    Args:
        project (framework.Project): project to examine and validate.
        
    Returns:
        framework.Project: validated framework.Project instance.
        
    """
    if not project.outline.workers:
        workers = [project.registry.keystones['worker']]
    else:
        names = project.outline.workers
        workers = []
        for name in names:
            workers.append(project.registry.workers[name])
    project.manager.contents = workers
    return project

       
    # def _validate_keystones(self) -> None:
    #     """Creates or validates 'keystones'."""
    #     if inspect.isclass(self.keystones):
    #         self.keystones = self.keystones()
    #     if (not isinstance(self.keystones, framework.ProjectKeystones)
    #         or not amos.has_attributes(
    #             item = self,
    #             attributes = [
    #                 'clerk', 'component', 'manager', 'settings', 'stage', 
    #                 'workflow'])):
    #         self.keystones = framework.ProjectKeystones()
    #     return self

    
    # def _validate_workflow(self) -> None:
    #     """Creates or validates 'workflow'."""
    #     if self.workflow is None:
    #         self.workflow = self.workflow
    #     return self

    # def _validate_results(self) -> None:
    #     """Creates or validates 'results'."""
    #     if not hasattr(self, 'results'):
    #         self.results = self.results
    #     return self
    
    # def _validate_data(self) -> None:
    #     """Creates or validates 'data'.
        
    #     The default method performs no validation but is included as a hook for
    #     subclasses to override if validation of the 'data' attribute is 
    #     required.
        
    #     """
    #     return self

    