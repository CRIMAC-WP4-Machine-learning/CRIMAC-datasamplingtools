# from echo_dataset import eds

from typing import Iterable, Union
import collections.abc
import abc


class ITestClass(collections.abc.Iterator, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "__len__")
            and callable(subclass.__len__)
            # and hasattr(subclass, "__iter__")
            # and callable(subclass.__iter__)
            or NotImplemented
        )

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> Iterable[int]:
        raise NotImplementedError


class NewTestClass(ITestClass):
    def __len__(self) -> int:
        pass

    def __next__(self):
        pass

    def __init__(self):
        self.x = [1, 2, 3]

class INewTestClass(ITestClass):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "new_method")
            and callable(subclass.new_method)
            or NotImplemented
        )

    @abc.abstractmethod
    def new_method(self, x: int) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def new_property(self) -> bool:
        raise NotImplementedError


class TestClass(INewTestClass):
    def __init__(self) -> None:
        self._new_property = False
        self.a = [*range(10)]

    def __iter__(self) -> Iterable[int]:
        self._n = 0
        return self

    def __len__(self) -> int:
        return len(self.a)

    def __next__(self) -> int:
        if self._n < len(self):
            self._n += 1
            return self.a[self._n - 1]
        else:
            raise StopIteration

    def new_method(self, x: int) -> None:
        print(x)

    @property
    def new_property(self) -> bool:
        return True


class SimpleClass:
    def __init__(self):
        self.x = 1000

    @property
    def y(self) -> int:
        return self.x


# a = TestClass()
# print(a.new_property)
# print(issubclass(type(a), ITestClass))
# a.new_method(9999)
# for val in a:
#     print(val)
#
# b = SimpleClass()
# print(b.y)

a = NewTestClass()
print(a)

# b = eds.ICompoundSamplerComponent()

# from echo_dataset import eds
#
#
# print(issubclass(eds.ICompoundSamplerComponent, eds.IStatelessSampler))
#
# val = eds.RandomSchoolSampler((200, 200))
