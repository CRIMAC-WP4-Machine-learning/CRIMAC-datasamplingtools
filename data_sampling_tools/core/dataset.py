from .cruise import ICruiseList

import datatable as dt
import xarray as xr

from typing import Union
import collections.abc
import abc


class IDataset(collections.abc.Sized, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "table")
            and callable(subclass.table)
            and hasattr(subclass, "cruise_list")
            and callable(subclass.cruise_list)
            or NotImplemented
        )

    @property
    @abc.abstractmethod
    def table(self) -> dt.Frame:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cruise_list(self) -> ICruiseList:
        raise NotImplementedError

    def __getitem__(self, index: int) -> dict[str, xr.Dataset]:
        raise NotImplementedError


__all__ = ["IDataset"]
