from .cruise import ICruiseList

from typing import Iterable, Union
from dataclasses import dataclass
import collections.abc
import abc


@dataclass
class SamplerItem:
    """
    :param x: x coordinate of the upper left corner of the sampled window.
    :param y: y coordinate of the upper left corner of the sampled window.
    :param w: sampled window width; adds to x coordinate.
    :param h: sampled window height; adds to y coordinate.
    :param cruise_idx: cruise index according to the caller's enumeration.
    :param cruise_info: information summary about the selected cruise.
    """

    x: int
    y: int
    w: int
    h: int
    x_padding: int
    y_padding: int
    cruise_idx: int
    cruise_info: dict[str, any]


class ISampler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "full_init")
            and callable(subclass.full_init)
            or NotImplemented
        )

    @abc.abstractmethod
    def full_init(self, *, cruise_list: ICruiseList) -> None:
        """Finish instantiation after __init__."""
        raise NotImplementedError


class IStatelessSampler(ISampler):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "__call__")
            and callable(subclass.__call__)
            or NotImplemented
        )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> SamplerItem:
        raise NotImplementedError


class IStatefulSampler(ISampler, collections.abc.Sized):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "__iter__")
            and callable(subclass.__iter__)
            and hasattr(subclass, "__next__")
            and callable(subclass.__next__)
            and hasattr(subclass, "__getitem__")
            and callable(subclass.__getitem__)
            or NotImplemented
        )

    @abc.abstractmethod
    def __iter__(self) -> Iterable[SamplerItem]:
        """
        Instantiates iterator state. Called before the first iteration.
        Please, follow the return type annotation in the __next__ method
        implementation (__next__ must be implemented; see
        collections.abc.Iterator). For example, if __iter__ returns
        Iterable[int], that means the __next__ method is supposed to return and
        *int* value when called.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __next__(self) -> SamplerItem:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, index: int) -> SamplerItem:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> SamplerItem:
        raise NotImplementedError


__all__ = ["SamplerItem", "ISampler", "IStatefulSampler", "IStatelessSampler"]
