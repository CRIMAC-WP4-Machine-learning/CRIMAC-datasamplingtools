from echo_dataset import eds

from typing import Iterable, Union
import collections
import abc


# _NotImplementedType = type(NotImplemented)
#
#
# class ITestClass(collections.abc.Iterator, metaclass=abc.ABCMeta):
#     @classmethod
#     def __subclasshook__(cls, subclass) -> Union[bool, _NotImplementedType]:
#         return (
#             hasattr(subclass, "__len__")
#             and callable(subclass.__len__)
#             and hasattr(subclass, "__iter__")
#             and callable(subclass.__iter__)
#             or NotImplemented
#         )
#
#     @abc.abstractmethod
#     def __len__(self) -> int:
#         raise NotImplementedError
#
#     @abc.abstractmethod
#     def __iter__(self) -> Iterable[int]:
#         raise NotImplementedError
#
#
# class INewTestClass(ITestClass):
#     _new_property: bool
#
#     @classmethod
#     def __subclasshook__(cls, subclass) -> Union[bool, _NotImplementedType]:
#         return (
#             hasattr(subclass, "new_method")
#             and callable(subclass.new_method)
#             or NotImplemented
#         )
#
#     @abc.abstractmethod
#     def new_method(self, x: int) -> None:
#         raise NotImplementedError
#
#     @property
#     def new_property(self) -> bool:
#         return self._new_property
#
#
# class TestClass(INewTestClass):
#     def __init__(self) -> None:
#         self._new_property = False
#         self.a = [*range(10)]
#
#     def __iter__(self) -> Iterable[int]:
#         self._n = 0
#         return self
#
#     def __len__(self) -> int:
#         return len(self.a)
#
#     def __next__(self) -> int:
#         if self._n < len(self):
#             self._n += 1
#             return self.a[self._n - 1]
#         else:
#             raise StopIteration
#
#     def new_method(self, x: int) -> None:
#         print(x)
#
#
# a = TestClass()
# a.new_property
# print(issubclass(type(a), ITestClass))
# a.new_method(9999)
# for val in a:
#     print(val)
#
# b = eds.ICompoundSamplerComponent()

from echo_dataset import eds


print(issubclass(eds.ICompoundSamplerComponent, eds.IStatelessSampler))

val = eds.RandomSchoolSampler((200, 200))