"""Repository: classes to library project assets

Contents:


To Do:


"""
from __future__ import annotations



# @dataclasses.dataclass  # type: ignore
# class ProjectLibrary(camina.Library):
#     """Stores classes instances and classes in a chained mapping.

#     When searching for matches, instances are prioritized over classes.

#     Args:
#         classes (camina.Catalog): a catalog of stored classes. Defaults to any
#             empty Catalog.
#         instances (camina.Catalog): a catalog of stored class instances. Defaults
#             to an empty Catalog.

#     """
#     classes: camina.Catalog[str, Type[ashford.Keystone]] = dataclasses.field(
#         default_factory = camina.Catalog)
#     instances: camina.Catalog[str, ashford.Keystone] = dataclasses.field(
#         default_factory = camina.Catalog)

#     """ Properties """

#     @property
#     def plurals(self) -> tuple[str]:
#         """Returns all stored subclass names as naive plurals of those names.

#         Returns:
#             tuple[str]: all names with an 's' added in order to create simple
#                 plurals combined with the stored keys.

#         """
#         suffixes = []
#         for catalog in ['classes', 'instances']:
#             plurals = [k + 's' for k in getattr(self, catalog).keys()]
#             suffixes.extend(plurals)
#         return tuple(suffixes)


# @dataclasses.dataclass  # type: ignore
# class ProjectRegistry(object):
#     """Stores classes and instances for a chrisjen project.

#     The registry facilitates flexibility and extensibility of the basic
#     defaults used in chrisjen. Users can design different project structures
#     while still taking advantage of chrisjen's accessibility and base classes.

#     Args:
#         keystones
#         managers
#         managers
#         nodes
#         subtypes
#         categories

#     """
#     keystones: ClassVar[camina.Catalog] = camina.Catalog()
#     managers: ClassVar[camina.Catalog] = camina.Catalog()
#     managers: ClassVar[camina.Catalog] = camina.Catalog()
#     nodes: ClassVar[ProjectLibrary] = ProjectLibrary()
#     subtypes: ClassVar[camina.Catalog] = camina.Catalog()
#     categories: ClassVar[MutableMapping[str, str]] = dataclasses.field(
#         default_factory = dict)

#     """ Public Methods """

#     @classmethod
#     def classify(
#         cls,
#         item: Union[ashford.Keystone, Type[ashford.Keystone]]) -> str:
#         """Returns name of kind that 'item' is an instance or subclass of.

#         Args:
#             item (Union[object, Type[Any]]): item to test for matching kind.

#         Raises:
#             TypeError: if no matching base kind is found.

#         Returns:
#             str: name of matching base kind.

#         """
#         if not inspect.isclass(item):
#             item = item.__class__
#         for name, subtype in cls.subtypes.items():
#             if issubclass(item, subtype):
#                 return name
#         raise TypeError(f'{item} does not match a known generic type')

#     @classmethod
#     def register(
#         cls,
#         item: Union[ashford.Keystone, Type[ashford.Keystone]]) -> None:
#         """Registers 'item' in the appropriate class attributes.

#         Args:
#             item (Union[ashford.Keystone, Type[ashford.Keystone]]): item to
#                 test and register.

#         """
#         key = camina.namify(item = item)
#         # Removes 'project_' prefix if it exists.
#         if key.startswith('project_'):
#             key = key[8:]
#         if issubclass(item, Node):
#             cls.nodes.deposit(item = item, name = key)
#         if Node in item.__bases__:
#             cls.subtypes[key] = item
#         if ashford.Keystone in item.__bases__:
#             cls.keystones[key] = item
#         if issubclass(item, Manager):
#             cls.managers[key] = item
#         if issubclass(item, Manager):
#             cls.managers[key] = item
#         kind = cls.classify(item = item)
#         cls.categories[key] = kind
#         return
