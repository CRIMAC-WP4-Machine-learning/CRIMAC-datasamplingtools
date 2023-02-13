from ..utils.samplers import validate_window_size
from ..utils.helpers import box_is_consistent

import datatable as dt
import xarray as xr
import numpy as np

from typing import Sequence, Optional, Iterable, Union
import collections
import random
import abc


__all__ = [
    "ISampler",
    "IStatefulSampler",
    "IStatelessSampler",
    "ICompoundSamplerComponent",
    "RandomSchoolSampler",
    # "RandomSchoolSampler",
    # "RandomBackgroundSampler",
]


_NotImplementedType = type(NotImplemented)


class ISampler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, _NotImplementedType]:
        return (
            hasattr(subclass, "full_init")
            and callable(subclass.full_init)
            or NotImplemented
        )

    @abc.abstractmethod
    def full_init(self, *, ds_summary: dt.Frame, **kwargs: any) -> None:
        """Finish instantiation with ds_summary form the caller."""
        raise NotImplementedError


class IStatefulSampler(ISampler, collections.abc.Iterator):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, _NotImplementedType]:
        return (
            hasattr(subclass, "__len__")
            and callable(subclass.__len__)
            or NotImplemented
        )

    @abc.abstractmethod
    def __len__(self) -> int:
        """Returns the number data points"""
        raise NotImplementedError

    @abc.abstractmethod
    def __iter__(self) -> Iterable[dict[str, xr.Dataset]]:
        """
        Instantiates iterator state. Called before the first iteration.
        Please, follow the return type annotation in the __next__ method
        implementation (__next__ must be implemented; see
        collections.abc.Iterator). For example, if __iter__ returns
        Iterable[int], that means the __next__ method is supposed to return and
        *int* value when called.
        """
        raise NotImplementedError


class IStatelessSampler(ISampler):
    @classmethod
    def __subclasshook__(cls, subclass) -> Union[bool, _NotImplementedType]:
        return (
            hasattr(subclass, "__call__")
            and callable(subclass.__call__)
            or NotImplemented
        )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
        raise NotImplementedError


class ICompoundSamplerComponent(IStatelessSampler):
    _window_size: tuple[int, int]

    @property
    def window_size(self) -> tuple[int, int]:
        return self._window_size


TCompoundSamplerComponentObject = type(ICompoundSamplerComponent)


class RandomSchoolSampler(ICompoundSamplerComponent):
    def __init__(self, window_size: Sequence[int]) -> None:
        validate_window_size(window_size=window_size)
        self._window_size = (
            tuple([window_size, window_size])
            if isinstance(window_size, int)
            else tuple(window_size)
        )

    def full_init(self, *, ds_summary: dt.Frame, **kwargs: any) -> None:

        pass

    def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
        if self._categories is None:
            raise ValueError
        cruise_idx = random.randint(0, ds.num_cruises - 1)
        valid_categories = [
            c for c in ds.cruise(cruise_idx).categories if c in self._categories
        ]
        category_idx = random.randint(0, len(valid_categories) - 1)
        fish_category = valid_categories[category_idx]
        school_boxes = ds.schools(
            cruise_idx=cruise_idx,
            fish_category=fish_category,
        )
        while True:
            box_idx = random.randint(0, len(school_boxes) - 1)
            box = school_boxes[box_idx]
            x_min = max(0, box[0] - self._window_size[0] // 2)
            x_max = box[2] - self.window_size[0] // 2
            y_min = max(0, box[1] - self._window_size[0] // 2)
            y_max = box[3] - self.window_size[1] // 2
            if (x_max + self._window_size[0]) > ds.cruise(cruise_idx).num_pings:
                x_max = ds.cruise(cruise_idx).num_pings - self._window_size[0]
                x_min = min(x_min, x_max)
            if (y_max + self._window_size[1]) > ds.cruise(cruise_idx).num_ranges:
                y_max = ds.cruise(cruise_idx).num_ranges - self._window_size[1]
                y_min = min(y_min, y_max)
            if x_max < x_min or y_max < y_min:
                continue
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            window = ds.crop(
                cruise_idx=cruise_idx,
                box=[x, y, x + self.window_size[0], y + self.window_size[1]],
            )

            # TODO: remove asserts in prod
            assert window["echogram"].ping_time.size == self._window_size[0]
            assert window["echogram"].range.size == self._window_size[1]
            assert window["annotations"].ping_time.size == self._window_size[0]
            assert window["annotations"].range.size == self._window_size[1]
            assert window["bottom"].ping_time.size == self._window_size[0]
            assert window["bottom"].range.size == self._window_size[1]

            if window["annotations"]["annotation"].isnull().any().compute():
                continue
            if window["echogram"]["sv"].isnull().any().compute():
                continue

            if window["annotations"]["annotation"].any().compute():
                return window


# class GriddedSampler(IStatefulSampler):
#     _grid_size: tuple[int, int]
#     _boxes: list[tuple[int, int, int, int]] | None
#
#     def __init__(
#         self,
#         grid_size: int | Sequence[int],
#         boxes: Optional[Sequence[Sequence[int]]] = None,
#     ) -> None:
#         self.grid_size: tuple[int, int] = grid_size
#         self.boxes: list[tuple[int, int, int, int]] = boxes
#
#     @property
#     def grid_size(self) -> tuple[int, int]:
#         return self._grid_size
#
#     @grid_size.setter
#     def grid_size(self, val: int | Sequence[int]) -> None:
#         if isinstance(val, int):
#             self._grid_size = (val, val)
#         elif (
#             isinstance(val, Sequence)
#             and len(val) == 2
#             and all([isinstance(v, int) for v in val])
#         ):
#             self._grid_size = tuple(val)
#         else:
#             raise ValueError(
#                 f"Type int or a sequence of two int values is expected. Got {type(val)}."
#             )
#
#     @property
#     def boxes(self) -> list[tuple[int, int, int, int]]:
#         return self._boxes
#
#     @boxes.setter
#     def boxes(self, vals: Sequence[Sequence[int]] | None) -> None:
#         if vals is None:
#             self._boxes = None
#             return
#         self._boxes = list()
#         for val in vals:
#             if len(val) == 4 and all(isinstance(v, int) for v in val):
#                 if box_is_consistent(val):
#                     self._boxes.append(tuple(val))
#                 else:
#                     raise ValueError(
#                         "Some boxes are inconsistent: x_min >= x_max or y_min >= y_max. Box format is [x_min, y_min, x_max, y_max]."
#                     )
#             else:
#                 raise TypeError(
#                     f"Type sequence of 4 int expected for box. Got {type(val)}."
#                 )
#
#     def __len__(self) -> int:
#         raise NotImplementedError
#
#     def __iter__(self):
#         raise NotImplementedError
#
#     def __next__(self) -> dict[str, xr.Dataset]:
#         raise NotImplementedError
#
#
# class StrideSampler(IStatefulSampler):
#     pass
#
#
# class ISampler:
#     _window_size: tuple[int, int]
#     _categories: list[int, ...]
#
#     def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
#         raise NotImplementedError
#
#     def init(self, categories: Sequence[int]) -> None:
#         self._categories = list(categories)
#
#     @property
#     def window_size(self) -> tuple[int, int]:
#         return self._window_size
#
#
# class RandomSchoolSampler(ISampler):
#     def __init__(self, window_size: Sequence[int]) -> None:
#         if len(window_size) == 2 and all(isinstance(v, int) for v in window_size):
#             # noinspection PyTypeChecker
#             self._window_size = tuple(window_size)
#         else:
#             raise Exception("Must be a sequence of exactly two integers")
#
#     def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
#         if self._categories is None:
#             raise ValueError
#         cruise_idx = random.randint(0, ds.num_cruises - 1)
#         valid_categories = [
#             c for c in ds.cruise(cruise_idx).categories if c in self._categories
#         ]
#         category_idx = random.randint(0, len(valid_categories) - 1)
#         fish_category = valid_categories[category_idx]
#         school_boxes = ds.schools(
#             cruise_idx=cruise_idx,
#             fish_category=fish_category,
#         )
#         while True:
#             box_idx = random.randint(0, len(school_boxes) - 1)
#             box = school_boxes[box_idx]
#             x_min = max(0, box[0] - self._window_size[0] // 2)
#             x_max = box[2] - self.window_size[0] // 2
#             y_min = max(0, box[1] - self._window_size[0] // 2)
#             y_max = box[3] - self.window_size[1] // 2
#             if (x_max + self._window_size[0]) > ds.cruise(cruise_idx).num_pings:
#                 x_max = ds.cruise(cruise_idx).num_pings - self._window_size[0]
#                 x_min = min(x_min, x_max)
#             if (y_max + self._window_size[1]) > ds.cruise(cruise_idx).num_ranges:
#                 y_max = ds.cruise(cruise_idx).num_ranges - self._window_size[1]
#                 y_min = min(y_min, y_max)
#             if x_max < x_min or y_max < y_min:
#                 continue
#             x = random.randint(x_min, x_max)
#             y = random.randint(y_min, y_max)
#             window = ds.crop(
#                 cruise_idx=cruise_idx,
#                 box=[x, y, x + self.window_size[0], y + self.window_size[1]],
#             )
#
#             # TODO: remove asserts in prod
#             assert window["echogram"].ping_time.size == self._window_size[0]
#             assert window["echogram"].range.size == self._window_size[1]
#             assert window["annotations"].ping_time.size == self._window_size[0]
#             assert window["annotations"].range.size == self._window_size[1]
#             assert window["bottom"].ping_time.size == self._window_size[0]
#             assert window["bottom"].range.size == self._window_size[1]
#
#             if window["annotations"]["annotation"].isnull().any().compute():
#                 continue
#             if window["echogram"]["sv"].isnull().any().compute():
#                 continue
#
#             if window["annotations"]["annotation"].any().compute():
#                 return window
#
#
# class RandomBackgroundSampler(ISampler):
#     def __init__(self, window_size: Sequence[int]) -> None:
#         if len(window_size) == 2 and all(isinstance(v, int) for v in window_size):
#             # noinspection PyTypeChecker
#             self._window_size = tuple(window_size)
#         else:
#             raise Exception("Must be a sequence of exactly two integers")
#
#     def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
#         if self._categories is None:
#             raise ValueError
#         x_max = ds.total_num_pings - self._window_size[0]
#         while True:
#             while True:
#                 x = random.randint(0, x_max)
#                 max_ping = None
#                 for i, k in enumerate(ds.ping_range_map):
#                     if (x + self._window_size[0]) <= k:
#                         max_ping = k
#                         break
#                 assert i is not None
#                 assert max_ping is not None
#                 break
#             y = random.randint(0, ds.ping_range_map[max_ping] - self.window_size[1])
#             window = ds.crop(
#                 cruise_idx=i,
#                 box=[
#                     max_ping - x,
#                     y,
#                     max_ping - x + self._window_size[0],
#                     y + self._window_size[1],
#                 ],
#             )
#
#             # window = ds.crop(
#             #     cruise_idx=i,
#             #     box=[
#             #         ds.cruise(i).num_pings - self._window_size[0],
#             #         ds.cruise(i).num_ranges - self._window_size[1],
#             #         ds.cruise(i).num_pings,
#             #         ds.cruise(i).num_ranges,
#             #     ],
#             # )
#
#             # TODO: remove asserts in prod
#             cond = [
#                 window["echogram"].ping_time.size == self._window_size[0],
#                 window["echogram"].range.size == self._window_size[1],
#                 window["annotations"].ping_time.size == self._window_size[0],
#                 window["annotations"].range.size == self._window_size[1],
#                 window["bottom"].ping_time.size == self._window_size[0],
#                 window["bottom"].range.size == self._window_size[1],
#             ]
#             if sum(cond) != len(cond):
#                 continue
#
#             if window["annotations"]["annotation"].isnull().any().compute():
#                 continue
#             if window["echogram"]["sv"].isnull().any().compute():
#                 continue
#
#             if not window["annotations"]["annotation"].any().compute():
#                 return window
#
#     def _generate_point(self) -> list[int, int]:
#         raise NotImplementedError
#
#
# class RandomBottomSampler(ISampler):
#     def __init__(self) -> None:
#         raise NotImplementedError
#
#     def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
#         raise NotImplementedError
#
#     def _generate_point(self) -> list[int, int]:
#         raise NotImplementedError
#
#
# class RandomNoiseSampler(ISampler):
#     def __init__(self) -> None:
#         raise NotImplementedError
#
#     def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
#         raise NotImplementedError
#
#     def _generate_point(self) -> list[int, int]:
#         raise NotImplementedError
