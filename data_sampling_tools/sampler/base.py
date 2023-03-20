from ..core.sampler import IStatelessSampler, IStatefulSampler, SamplerItem
from ..utils.samplers import count_grid_cells
from ..core.cruise import ICruiseList

import numpy as np

from typing import Sequence, Mapping, Optional, Iterable
import random


class BaseCompoundRandomSampler(IStatelessSampler):
    _samplers: tuple[IStatelessSampler, ...]
    _weights: tuple[float, ...]

    def __init__(
        self,
        samplers: Sequence,
        sampler_args: Optional[Sequence[Mapping[str, any]]] = None,
        weights: Optional[Sequence[float]] = None,
    ) -> None:
        if weights is None:
            self._weights = tuple([1 / len(samplers)] * len(samplers))
        else:
            assert len(weights) == len(
                samplers
            ), "Number of weights doesn't match the number of samplers"
            assert abs(sum(weights) - 1) < 1e-3, "Weights must sum to 1"
            self._weights = tuple(weights)
        self._samplers = tuple([s(a) for s, a in zip(samplers, sampler_args)])

    def full_init(self, *, cruise_list: ICruiseList) -> None:
        [s.full_init(cruise_list=cruise_list) for s in self._samplers]

    def __len__(self) -> int:
        return len(self._samplers)

    def __call__(self, *args, **kwargs) -> SamplerItem:
        sampler_idx = np.random.choice(len(self), p=self._weights)
        return self._samplers[sampler_idx](*args, **kwargs)


class BaseRandomSampler(IStatelessSampler):
    _window_size: dict[str, int]
    _cruise_list: ICruiseList

    def __init__(self, window_height: int, window_width: Optional[int] = None) -> None:
        assert isinstance(window_height, int)
        if window_width is not None:
            assert isinstance(window_width, int)
        self._window_size = {
            "h": window_height,
            "w": window_width if window_width is not None else window_height,
        }

    def full_init(self, *, cruise_list: ICruiseList) -> None:
        self._cruise_list = cruise_list

    def __call__(self, *args, **kwargs) -> SamplerItem:
        cruise_idx = np.random.choice(
            len(self._cruise_list), p=self._cruise_list.cruise_ping_fractions
        )
        cruise = self._cruise_list.cruises[cruise_idx]
        height, width = cruise.num_ranges, cruise.num_pings
        height -= self._window_size["h"]
        width -= self._window_size["w"]
        x = random.randint(0, width)
        y = random.randint(0, height)
        return SamplerItem(
            x=x,
            y=y,
            x_padding=0,
            y_padding=0,
            cruise_idx=cruise_idx,
            cruise_info=cruise.info,
            **self._window_size  # adds "h" and "w" key-value pairs
        )


class BaseGriddedSampler(IStatefulSampler):
    _grid_size: dict[str, int]
    _cruise_list: ICruiseList
    _num_segments_vertical: tuple[int, ...]
    _num_segments_horizontal: tuple[int, ...]
    _vertical_padding: tuple[int, ...]
    _horizontal_padding: tuple[int, ...]
    _num_cells: tuple[int, ...]
    _total_num_cells: int
    _cruise_iter_count: int
    _cell_iter_count: int
    _global_iter_count: int

    def __init__(self, grid_height: int, grid_width: Optional[int] = None) -> None:
        assert isinstance(grid_height, int)
        if grid_width is not None:
            assert isinstance(grid_width, int)
        self._grid_size = {
            "h": grid_height,
            "w": grid_width if grid_width is not None else grid_height,
        }

    def full_init(self, *, cruise_list: ICruiseList) -> None:
        self._cruise_list = cruise_list
        num_segments_vertical = np.empty(shape=len(cruise_list), dtype=int)
        num_segments_horizontal = np.empty(shape=len(cruise_list), dtype=int)
        vertical_padding = np.empty(shape=len(cruise_list), dtype=int)
        horizontal_padding = np.empty(shape=len(cruise_list), dtype=int)
        for i, c in enumerate(cruise_list.cruises):
            (
                num_segments_vertical[i],
                num_segments_horizontal[i],
                vertical_padding[i],
                horizontal_padding[i],
            ) = count_grid_cells(
                domain_height=c.num_ranges,
                domain_width=c.num_pings,
                grid_height=self._grid_size["h"],
                grid_width=self._grid_size["w"],
            )
        self._num_cells = tuple(num_segments_horizontal * num_segments_vertical)
        self._total_num_cells = sum(self._num_cells)
        self._num_segments_vertical = tuple(num_segments_vertical)
        self._num_segments_horizontal = tuple(num_segments_horizontal)
        self._vertical_padding = tuple(vertical_padding)
        self._horizontal_padding = tuple(horizontal_padding)

    def __len__(self) -> int:
        return self._total_num_cells

    def __iter__(self) -> Iterable[SamplerItem]:
        self._cruise_iter_count = 0
        self._cell_iter_count = 0
        self._global_iter_count = 0
        return self

    def __next__(self) -> SamplerItem:
        item = self[self._global_iter_count]
        self._global_iter_count += 1
        self._cell_iter_count += 1
        if self._cell_iter_count == self._num_cells[self._cruise_iter_count]:
            self._cell_iter_count = 0
            self._cruise_iter_count += 1
        elif self._cell_iter_count > self._num_cells[self._cruise_iter_count]:
            raise IndexError
        return item

    def __getitem__(self, index: int) -> SamplerItem:
        assert isinstance(index, int)
        if index >= len(self):
            raise IndexError("Index out of bounds")
        for cruise_idx, num_cells in enumerate(self._num_cells):
            if index < num_cells:
                y_idx = index // self._num_segments_horizontal[cruise_idx]
                x_idx = index % self._num_segments_horizontal[cruise_idx]
                return SamplerItem(
                    x=x_idx * self._grid_size["w"],
                    y=y_idx * self._grid_size["h"],
                    x_padding=self._horizontal_padding[cruise_idx]
                    if x_idx == (self._num_segments_horizontal[cruise_idx] - 1)
                    else 0,
                    y_padding=self._vertical_padding[cruise_idx]
                    if y_idx == (self._num_segments_vertical[cruise_idx] - 1)
                    else 0,
                    cruise_idx=cruise_idx,
                    cruise_info=self._cruise_list.cruises[cruise_idx].info,
                    **self._grid_size  # adds "h" and "w" key-value pairs
                )
            else:
                index -= num_cells
        raise IndexError("Can't find correct cell")

    def __call__(self, *args, **kwargs) -> SamplerItem:
        return self[kwargs.get("index", self._global_iter_count)]


# TODO: finish this sampler one day
# class BaseStrideSampler(IStatefulSampler):
#     pass


__all__ = ["BaseCompoundRandomSampler", "BaseRandomSampler", "BaseGriddedSampler"]
