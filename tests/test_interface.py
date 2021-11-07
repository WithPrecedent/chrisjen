"""
test_project: tests Project class and created composite objects
Corey Rayburn Yung <coreyrayburnyung@gmail.com>
Copyright 2020-2021, Corey Rayburn Yung
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)
"""
from __future__ import annotations
import dataclasses
import pathlib

import chrisjen


@dataclasses.dataclass
class Parser(chrisjen.Contest):

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
    project = chrisjen.Project(
        name = 'cool_project',
        settings = pathlib.Path('tests') / 'project_settings.py',
        automatic = True)
    # Tests base libraries.
    assert 'parser' in chrisjen.Component.library.subclasses
    dynamite = Dynamite()
    assert 'annihilate' in chrisjen.Component.library.instances
    # Tests workflow construction.
    print('test project workflow', project.workflow)
    print('test workflow endpoints', str(project.workflow.endpoints))
    print('test workflow roots', str(project.workflow.roots))
    return


if __name__ == '__main__':
    test_project()
    