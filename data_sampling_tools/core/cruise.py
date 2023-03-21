from pydantic import BaseModel
import polars as pl
import xarray as xr

from typing import Union, Sequence, Optional, TypeVar
from pathlib import Path
from enum import Enum
import collections.abc
import abc


Self = TypeVar("Self", bound="ICruise")


class SchoolBoxesOrigin(Enum):
    NOT_AVAILABLE = 1
    CSV = 2
    CONTOUR_SEARCH = 3


# TODO: encode logic coupled with each field
class FilterConfig(BaseModel):
    frequencies: list[int, ...]
    categories: list[int, ...]
    with_annotations_only: bool
    with_bottom_only: bool
    names: Optional[list[str, ...]] = None
    years: Optional[list[int, ...]] = None


class ICruise(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "info")
            and callable(subclass.info)
            and hasattr(subclass, "path")
            and callable(subclass.path)
            and hasattr(subclass, "echogram")
            and callable(subclass.echogram)
            and hasattr(subclass, "frequencies")
            and callable(subclass.frequencies)
            and hasattr(subclass, "num_pings")
            and callable(subclass.num_pings)
            and hasattr(subclass, "num_ranges")
            and callable(subclass.num_ranges)
            and hasattr(subclass, "annotations_available")
            and callable(subclass.annotations_available)
            and hasattr(subclass, "annotations")
            and callable(subclass.annotations)
            and hasattr(subclass, "categories")
            and callable(subclass.categories)
            and hasattr(subclass, "school_boxes")
            and callable(subclass.school_boxes)
            and hasattr(subclass, "school_boxes_origin")
            and callable(subclass.school_boxes_origin)
            and hasattr(subclass, "bottom_available")
            and callable(subclass.bottom_available)
            and hasattr(subclass, "bottom")
            and callable(subclass.bottom)
            and hasattr(subclass, "from_box")
            and callable(subclass.from_box)
            and hasattr(subclass, "crop")
            and callable(subclass.crop)
            or NotImplemented
        )

    @property
    @abc.abstractmethod
    def path(self) -> Path:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def info(self) -> dict[str, any]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def echogram(self) -> xr.Dataset:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def frequencies(self) -> tuple[int, ...]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def num_pings(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def num_ranges(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def annotations_available(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def annotations(self) -> xr.Dataset:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def categories(self) -> tuple[int, ...]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def school_boxes(
        self,
    ) -> dict[int, list[tuple[int, int, int, int], ...]]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def school_boxes_origin(self) -> SchoolBoxesOrigin:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def bottom_available(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def bottom(self) -> xr.Dataset:
        raise NotImplementedError

    @abc.abstractmethod
    def from_box(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        /,
        *,
        category: int,
        force_find_school_boxes: bool,
    ) -> Self:
        raise NotImplementedError

    @abc.abstractmethod
    def crop(self, x1: int, y1: int, x2: int, y2: int) -> dict[str, xr.Dataset]:
        """
                    Ping time
        (x1, y1)    ---->
                ┌──────────────┐
        Range │ │              │
              ▼ │              │
                └──────────────┘
                                (x2, y2)

        :param x1: upper left row index.
        :param y1: upper left column index.
        :param x2: lower right row index.
        :param y2: lower right column index.
        :return: xarray.Dataset containing the slice.

        **Note**: x2 and y2 are excluded
        """
        raise NotImplementedError


class ICruiseList(
    collections.abc.Iterable, collections.abc.Sized, metaclass=abc.ABCMeta
):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, type(NotImplemented)]:
        return (
            hasattr(subclass, "table")
            and callable(subclass.table)
            and hasattr(subclass, "cruises")
            and callable(subclass.cruises)
            and hasattr(subclass, "cruise_ping_fractions")
            and callable(subclass.cruise_ping_fractions)
            and hasattr(subclass, "total_num_pings")
            and callable(subclass.total_num_pings)
            and hasattr(subclass, "min_range_len")
            and callable(subclass.min_range_len)
            and hasattr(subclass, "max_range_len")
            and callable(subclass.max_range_len)
            and hasattr(subclass, "is_ping_uniform")
            and callable(subclass.is_ping_uniform)
            and hasattr(subclass, "categories")
            and callable(subclass.categories)
            and hasattr(subclass, "frequencies")
            and callable(subclass.frequencies)
            and hasattr(subclass, "school_boxes")
            and callable(subclass.school_boxes)
            and hasattr(subclass, "crop")
            and callable(subclass.crop)
            or NotImplemented
        )

    @property
    @abc.abstractmethod
    def table(self) -> pl.DataFrame:
        """Table with the summary over the cruises."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cruises(self) -> tuple[ICruise, ...]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cruise_ping_fractions(self) -> tuple[float, ...]:
        """Returns fractions proportional to number of pings per cruise."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def total_num_pings(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def min_range_len(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def max_range_len(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_ping_uniform(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def categories(self) -> tuple[int, ...]:
        """Returns unique categories across all cruises."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def frequencies(self) -> tuple[int, ...]:
        """Returns unique frequencies across all cruises."""
        raise NotImplementedError

    @abc.abstractmethod
    def school_boxes(
        self, cruise_idx: int, fish_category: Optional[int] = None
    ) -> dict[int, list[tuple[int, int, int, int], ...]]:
        raise NotImplementedError

    @abc.abstractmethod
    def crop(self, cruise_idx: int, box: Sequence[int]) -> dict[str, xr.Dataset]:
        raise NotImplementedError


__all__ = ["ICruise", "ICruiseList", "SchoolBoxesOrigin"]
