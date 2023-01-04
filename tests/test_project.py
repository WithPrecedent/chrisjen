"""
test_project: tests Project class and created composite objects
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


To Do:

            
"""
from __future__ import annotations
import dataclasses
import pathlib

import chrisjen
import holden


@dataclasses.dataclass
class Parser(chrisjen.Compete):

    pass


@dataclasses.dataclass
class Search(chrisjen.Step):

    pass   


@dataclasses.dataclass
class Divide(chrisjen.Step):

    pass   
    
    
@dataclasses.dataclass
class Destroy(chrisjen.Step):

    pass   
    

@dataclasses.dataclass
class Slice(chrisjen.Technique):

    pass  


@dataclasses.dataclass
class Dice(chrisjen.Technique):

    pass 
    
    
@dataclasses.dataclass
class Find(chrisjen.Technique):

    pass 

    
@dataclasses.dataclass
class Locate(chrisjen.Technique):

    pass 

    
@dataclasses.dataclass
class Explode(chrisjen.Technique):

    pass 

    
@dataclasses.dataclass
class Dynamite(chrisjen.Technique):
    
    name: str = 'annihilate'


def test_project():
    settings = pathlib.Path('tests') / 'cancer_settings.ini'
    project = chrisjen.Project(
        idea = settings,
        automatic = False)
    project.manager.draft()
    assert project.outline.connections['wrangler'] == ['none']
    assert project.outline.connections['scale'] == [
        'minmax', 
        'robust', 
        'normalize']
    assert project.outline.designs == {
        'wisconsin_cancer': 'waterfall',
        'analyst': 'compete', 
        'critic': 'waterfall'}
    assert project.outline.implementation['cleaver'] == {'include_all': True}
    assert project.outline.initialization['analyst'] == {
        'model_type': 'classify', 
        'label': 'target', 
        'default_package': 'sklearn', 
        'search_method': 'random'}
    assert project.outline.kinds['scale'] == 'step'
    assert project.outline.kinds['logit'] == 'technique'
    assert 'train_test' in project.outline.labels
    assert 'random_forest' in project.outline.labels
    assert 'critic' in project.outline.labels
    assert project.outline.manager['wisconsin_cancer_workers'] == [
        'wrangler',
        'analyst', 
        'critic']
    project.manager.publish()
    export = pathlib.Path('tests').joinpath('dag.dot')
    chrisjen.to_dot(project = project, path = export, name = 'dag')
    # print('test workers', project.outline.workers.keys())
    # print('test workflow', project.workflow.graph)
    # print('test paths', [(e[0].name, e[1].name) for e in project.workflow.edges])
    # Tests base libraries.
    # Tests workflow construction.
    # print('test project workflow', project.workflow)
    # print('test workflow endpoints', str(project.workflow.endpoint))
    # print('test workflow roots', str(project.workflow.root))
    return


if __name__ == '__main__':
    test_project()
    