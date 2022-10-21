"""
filing: base file management classes and functions for chrisjen projects
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
    FileFormat (object): contains data needed for a Filer-compatible file 
        format.
    formats (dict): a dictionary of the out-of-the-box supported file formats.
    default_parameters (dict): a dictionary with default shared parameters for
        various disk-related tasks.
    Filer (object): interface for chrisjen file management classes and methods.
     
"""
from __future__ import annotations
from collections.abc import Hashable, Mapping, MutableMapping
import copy
import dataclasses
import inspect
import pathlib
import types
from typing import Any, Optional, Type, TYPE_CHECKING, Union

import amos
import nagata

from . import base
      
      
@dataclasses.dataclass
class FileFormat(object):
    """File format information.

    Args:
        name (Optional[str]): the format name which should match the key when a 
            FileFormat instance is stored.
        module (Optional[str]): name of module where object to incorporate is, 
            which can either be a chrisjen or non-chrisjen module. Defaults to 
            None.
        extension (Optional[str]): str file extension to use. Defaults to None.
        load_method (Optional[Union[str, types.FunctionType]]): if a str, it is
            the name of import method in 'module' to use. Otherwise, it should
            be a function for loading. Defaults to None.
        save_method (Optional[Union[str, types.FunctionType]]): if a str, it is
            the name of import method in 'module' to use. Otherwise, it should
            be a function for saved. Defaults to None.
        parameters (Mapping[str, str]]): shared parameters to use from 
            configuration settings where the key is the parameter name that the 
            load or save method should use and the value is the key for the 
            argument in the shared parameters. Defaults to an empty dict. 

    """
    name: Optional[str] = None
    module: Optional[str] = None
    extension: Optional[str] = None
    load_method: Optional[Union[str, types.FunctionType]] = None
    save_method: Optional[Union[str, types.FunctionType]] = None
    parameters: Mapping[str, str] = dataclasses.field(default_factory = dict)
    
    """ Dunder Methods """
    
    @classmethod
    def __subclasshook__(cls, subclass: Type[Any]) -> bool:
        """Returns whether 'subclass' is a virtual or real subclass.

        Args:
            subclass (Type[Any]): item to test as a subclass.

        Returns:
            bool: whether 'subclass' is a real or virtual subclass.
            
        """
        return (subclass in cls.__subclasses__() 
                or amos.has_attributes(
                    item = subclass,
                    methods = [
                        'name', 'module', 'extension', 'load_method',
                        'save_method', 'parameters']))


""" Included File Formats """

file_formats: MutableMapping[str, FileFormat] = {
    'csv': FileFormat(
        name = 'csv',
        module =  'pandas',
        extension = '.csv',
        load_method = 'read_csv',
        save_method = 'to_csv',
        parameters = {
            'encoding': 'file_encoding',
            'index_col': 'index_column',
            'header': 'include_header',
            'low_memory': 'conserve_memory',
            'nrows': 'test_size'}),
    'excel': FileFormat(
        name = 'excel',
        module =  'pandas',
        extension = '.xlsx',
        load_method = 'read_excel',
        save_method = 'to_excel',
        parameters = {
            'index_col': 'index_column',
            'header': 'include_header',
            'nrows': 'test_size'}),
    'feather': FileFormat(
        name = 'feather',
        module =  'pandas',
        extension = '.feather',
        load_method = 'read_feather',
        save_method = 'to_feather',
        parameters = {'nthreads': 'threads'}),
    'hdf': FileFormat(
        name = 'hdf',
        module =  'pandas',
        extension = '.hdf',
        load_method = 'read_hdf',
        save_method = 'to_hdf',
        parameters = {
            'columns': 'included_columns',
            'chunksize': 'test_size'}),
    'json': FileFormat(
        name = 'json',
        module =  'pandas',
        extension = '.json',
        load_method = 'read_json',
        save_method = 'to_json',
        parameters = {
            'encoding': 'file_encoding',
            'columns': 'included_columns',
            'chunksize': 'test_size'}),
    'stata': FileFormat(
        name = 'stata',
        module =  'pandas',
        extension = '.dta',
        load_method = 'read_stata',
        save_method = 'to_stata',
        parameters = {'chunksize': 'test_size'}),
    'text': FileFormat(
        name = 'text',
        module =  None,
        extension = '.txt',
        load_method = '_import_text',
        save_method = '_export_text'),
    'png': FileFormat(
        name = 'png',
        module =  'seaborn',
        extension = '.png',
        save_method = 'save_fig',
        parameters = {
            'bbox_inches': 'visual_tightness', 
            'format': 'visual_format'}),
    'pickle': FileFormat(
        name = 'pickle',
        module =  None,
        extension = '.pickle',
        load_method = '_pickle_object',
        save_method = '_unpickle_object')}   
    
default_parameters: MutableMapping[str, Any] = {
    'file_encoding': 'windows-1252',
    'index_column': True,
    'include_header': True,
    'conserve_memory': False,
    'test_size': 1000,
    'threads': -1,
    'visual_tightness': 'tight', 
    'visual_format': 'png'}

   
@dataclasses.dataclass
class Filer(nagata.FileManager):
    """File and folder management for chrisjen.

    Creates and stores dynamic and static file paths, properly formats files
    for import and export, and provides methods for loading and saving
    chrisjen, pandas, and numpy objects.

    Args:
        project (base.Project): a Project instance with a 'settings' 
            attribute that may contain configuration options for Filer.
        root_folder (Union[str, pathlib.Path]): the complete path from which the 
            other paths and folders used by Filer are ordinarily derived 
            (unless you decide to use full paths for all other options). 
            Defaults to None. If not passed, the parent folder of the current 
            working workery is used.
        input_folder (Union[str, pathlib.Path]]): the input_folder subfolder 
            name or a complete path if the 'input_folder' is not off of
            'root_folder'. Defaults to 'input'.
        output_folder (Union[str, pathlib.Path]]): the output_folder subfolder
            name or a complete path if the 'output_folder' is not off of
            'root_folder'. Defaults to 'output'.
        formats (MutableMapping[str, FileFormat]): a dictionary of file_formats
            and keys with the chrisjen str names of those formats. Defaults to the
            global 'formats' variable.
        parameters (MutableMapping[str, str]): keys are the chrisjen names of 
            parameters and values are the values which should be passed to the
            Distributor instances when loading or savings files. Defaults to the
            global 'default_parameters' variable.

    """
    project: Optional[base.Project] = None
    root_folder: Union[str, pathlib.Path] = pathlib.Path('..')
    input_folder: Union[str, pathlib.Path] = 'input'
    output_folder: Union[str, pathlib.Path] = 'output'
    formats: MutableMapping[str, FileFormat] = dataclasses.field(
        default_factory = lambda: file_formats)
    parameters: MutableMapping[str, str] = dataclasses.field(
        default_factory = lambda: default_parameters) 
    
    """ Initialization Methods """

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Validates core folder paths and writes them to disk.
        self.root_folder = self.validate_path(path = self.root_folder)
        self.input_folder = self._validate_io_folder(path = self.input_folder)
        self.output_folder = self._validate_io_folder(path = self.output_folder)
        # Adds and/overrides 'parameters' from 'project.settings'.
        self.project.settings = self.project.settings or {}
        self._add_settings()
        return

    """ Class Methods """
    
    @classmethod
    def validate(cls, project: base.Project) -> base.Project:
        """Creates or validates 'project.filer'.

        Args:
            project (base.Project): an instance with a 'filer' attribute.

        Returns:
            base.Project: an instance with a validated 'filer' attribute.
            
        """  
        if inspect.isclass(project.filer):
            project.filer = project.filer(project = project)
        elif project.filer is None:
            project.filer = cls.create(project = project)
        return project    
       
    """ Public Methods """

    def load(
        self,
        file_path: Union[str, pathlib.Path] = None,
        folder: Union[str, pathlib.Path] = None,
        file_name: Optional[str] = None,
        file_format: Union[str, FileFormat] = None,
        **kwargs: Any) -> Any:
        """Imports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Any: depending upon method used for appropriate file format, a new
                variable of a supported type is returned.

        """
        file_path, file_format = prepare_transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        parameters = self._get_parameters(file_format = file_format, **kwargs)
        if file_format.module:
            tool = file_format.load('import_method')
        else:
            tool = getattr(self, file_format.import_method)
        return tool(file_path, **parameters)

    def save(
        self,
        item: Any,
        file_path: Optional[Union[str, pathlib.Path]] = None,
        folder: Optional[Union[str, pathlib.Path]] = None,
        file_name: Optional[str] = None,
        file_format: Optional[Union[str, FileFormat]] = None,
        **kwargs: Any) -> None:
        """Exports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            item (Any): object to be save to disk.
            file_path (Union[str, Path]]): a complete file path.
                Defaults to None.
            folder (Union[str, Path]]): a complete folder path or the
                name of a folder stored in 'filer'. Defaults to None.
            file_name (str): file name without extension. Defaults to
                None.
            file_format (Union[str, FileFormat]]): object with
                information about how the file should be loaded or the key to
                such an object stored in 'filer'. Defaults to None
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        """
        file_path, file_format = prepare_transfer(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        parameters = self._get_parameters(file_format = file_format, **kwargs)
        if file_format.module:
            getattr(item, file_format.export_method)(item, **parameters)
        else:
            getattr(self, file_format.export_method)(item, **parameters)
        return

    def validate_path(self, path: Union[str, pathlib.Path]) -> pathlib.Path:
        """Turns 'file_path' into a pathlib.Path.

        Args:
            path (Union[str, pathlib.Path]): str or Path to be validated. If
                a str is passed, the method will see if an attribute matching
                'path' exists and if that attribute contains a Path.

        Raises:
            TypeError: if 'path' is neither a str nor Path.
            FileNotFoundError: if the validated path does not exist and 'create'
                is False.

        Returns:
            pathlib.Path: derived from 'path'.

        """
        path = amos.pathlibify(item = path)
        if isinstance(path, str):
            if (hasattr(self, path) 
                    and isinstance(getattr(self, path), pathlib.Path)):
                validated = getattr(self, path)
            else:
                validated = pathlib.Path(path)
        elif isinstance(path, pathlib.Path):
            validated = path
        else:
            raise TypeError(f'path must be a str or Path type')
        # if test and not validated.exists():
        #     if create:
        #         self._write_folder(folder = validated)
        #     else:
        #         raise FileNotFoundError(f'{validated} does not exist')
        return validated
      
    """ Private Methods """

    def _validate_io_folder(
        self, 
        path: Union[str, pathlib.Path]) -> pathlib.Path:
        """Validates an import or export path.

        Args:
            path (Union[str, pathlib.Path]): path to be validated.

        Returns:
            pathlib.Path: validated path.
            
        """
        try:
            return self.validate_path(path = path)
        except FileNotFoundError:
            return self.validate_path(path = self.root_folder / path)

    def _add_settings(self) -> None:
        """Mixes 'project.settings' with default parameters, if needed."""
        # Gets default parameters for file transfers from 'settings'.
        base = copy.deepcopy(default_parameters)
        self.parameters = base
        try:
            self.parameters.update(self.project.settings.filer)
        except KeyError:
            pass
        return

    def _write_folder(self, folder: Union[str, pathlib.Path]) -> None:
        """Writes folder to disk.

        Parent folders are created as needed.

        Args:
            folder (Union[str, Path]): intended folder to write to disk.

        """
        pathlib.Path.mkdir(folder, parents = True, exist_ok = True)
        return


def validate_file_format(file_format: Union[str, FileFormat]) -> FileFormat:
    """Selects 'file_format' or returns FileFormat instance intact.

    Args:
        file_format (Union[str, FileFormat]): name of file format or a
            FileFormat instance.

    Raises:
        TypeError: if 'file_format' is neither a str nor FileFormat type.

    Returns:
        FileFormat: appropriate instance.

    """
    if file_format in file_formats:
        return file_formats[file_format]
    elif isinstance(file_format, FileFormat):
        return file_format
    elif issubclass(file_format, FileFormat):
        return file_format()
    else:
        raise TypeError(f'{file_format} is not a recognized file format')

def combine_path(
    folder: str,
    file_name: Optional[str] = None,
    extension: Optional[str] = None,
    filer: Optional[Filer] = None) -> pathlib.Path:
    """Converts strings to pathlib Path object.

    If 'folder' matches an attribute, the value stored in that attribute
    is substituted for 'folder'.

    If 'name' and 'extension' are passed, a file path is created. Otherwise,
    a folder path is created.

    Args:
        folder (str): folder for file location.
        name (str): the name of the file.
        extension (str): the extension of the file.
        filer (Optional[Filer]): a Filer instance that may have attributes with
            folder paths. Defaults to None.

    Returns:
        Path: formed from string arguments.

    """
    if filer is not None and hasattr(filer, folder):
        folder = getattr(filer, folder)
    if file_name and extension:
        return pathlib.Path(folder).joinpath(f'{file_name}.{extension}')
    else:
        return pathlib.Path(folder)

def get_transfer_parameters(
    file_format: FileFormat, 
    shared: MutableMapping[str, str],
    **kwargs: Any) -> MutableMapping[Hashable, Any]:
    """Creates complete parameters for a file input/output method.

    Args:
        file_format (FileFormat): an instance with information about the
            needed and optional parameters.
        kwargs: additional parameters to pass to an input/output method.

    Returns:
        MutableMapping[Hashable, Any]: parameters to be passed to an 
            input/output method.

    """
    if file_format.parameters:
        for specific, common in file_format.parameters.items():
            if specific not in kwargs:
                kwargs[specific] = shared[common]
    return kwargs # type: ignore

def prepare_transfer( 
    file_path: Union[str, pathlib.Path],
    folder: Union[str, pathlib.Path],
    file_name: str,
    file_format: Union[str, FileFormat]) -> tuple[pathlib.Path, FileFormat]:
    """Prepares file path related arguments for loading or saving a file.

    Args:
        file_path (Union[str, Path]): a complete file path.
        folder (Union[str, Path]): a complete folder path or the name of a
            folder stored in 'filer'.
        file_name (str): file name without extension.
        file_format (Union[str, FileFormat]): object with information about
            how the file should be loaded or the key to such an object
            stored in 'filer'.
        **kwargs: can be passed if additional options are desired specific
            to the pandas or python method used internally.

    Returns:
        tuple: of a completed Path instance and FileFormat instance.

    """
    if file_path:
        file_path = amos.pathlibify(item = file_path)
        if not file_format:
            try:
                file_format = [f for f in file_formats.values()
                               if f.extension == file_path.suffix[1:]][0]
            except IndexError:
                file_format = [f for f in file_formats.values()
                               if f.extension == file_path.suffix][0]           
    file_format = validate_file_format(file_format = file_format)
    extension = file_format.extension
    if not file_path:
        file_path = combine_path(
            folder = folder, 
            file_name = file_name,
            extension = extension)
    return file_path, file_format