from data_sampling_tools.sampler import BaseRandomSampler, BaseGriddedSampler
from data_sampling_tools.utils.samplers import extend_school_box
from data_sampling_tools.core.sampler import SamplerItem
from data_sampling_tools.core.cruise import ICruiseList
from data_sampling_tools.cruise import CruiseListBase

import datatable as dt
import numpy as np

from typing import Optional, Sequence
import random


class RandomSchoolSampler(BaseRandomSampler):
    __allowed_category_weights_modes = ("uniform", "freq")
    _category_weights_mode: str
    _unvalidated_category_weights: tuple[float, ...]
    _category_weights: tuple[float, ...]
    _categories: tuple[int, ...]
    _state_category_weights_initialized: bool
    _state_category_weights_validated: bool
    _cruise_list: ICruiseList
    _school_weights: tuple[float, ...]

    def __init__(
        self,
        window_height: int,
        window_width: Optional[int] = None,
        category_weights: Optional[Sequence[float]] = None,
        category_weights_mode: Optional[str] = None,
    ) -> None:
        super().__init__(window_height=window_height, window_width=window_width)
        self._state_category_weights_validated = False
        self._state_category_weights_initialized = False
        if category_weights is not None:
            self._unvalidated_category_weights = tuple(category_weights)
            self._state_category_weights_initialized = True
        else:
            if category_weights_mode is None:
                self._category_weights_mode = "uniform"
            elif category_weights_mode in self.__allowed_category_weights_modes:
                self._category_weights_mode = category_weights_mode

    def full_init(self, *, cruise_list: ICruiseList) -> None:
        self._cruise_list = cruise_list
        self._categories, category_counts = np.unique(
            self._cruise_list.table[:, "category"].to_numpy().flatten(),
            return_counts=True,
        )
        self._categories = tuple(self._categories)
        if self._state_category_weights_initialized:
            if self._state_category_weights_validated:
                self._category_weights = self._unvalidated_category_weights
            else:
                valid = len(self._categories) == len(self._unvalidated_category_weights)
                valid *= abs(sum(self._unvalidated_category_weights) - 1) <= 1e-3
                if valid:
                    self._category_weights = self._unvalidated_category_weights
                    self._state_category_weights_validated = True
                else:
                    self._category_weights = self._init_category_weights(
                        categories=self._categories, counts=category_counts
                    )
                    self._state_category_weights_validated = True
        else:
            self._category_weights = self._init_category_weights(
                categories=self._categories, counts=category_counts
            )
            self._state_category_weights_initialized = True
            self._state_category_weights_validated = True

    def _init_category_weights(
        self, categories: tuple[int, ...], counts: Optional[np.ndarray[int]] = None
    ) -> tuple[float, ...]:
        if self._category_weights_mode == self.__allowed_category_weights_modes[0]:
            return tuple([1 / len(categories)] * len(categories))
        elif (
            self._category_weights_mode == self.__allowed_category_weights_modes[1]
            and counts is not None
        ):
            return tuple(counts.sum() / counts)
        else:
            raise ValueError("Unsupported category weights mode")

    def __call__(self, *args, **kwargs) -> SamplerItem:
        # Select a category and filter the ICruiseList.table by it
        category = np.random.choice(self._categories, p=self._category_weights)
        table = self._cruise_list.table[dt.f.category == category, :]
        # Select a random row
        row_idx = np.random.randint(0, table.nrows)
        row = table[row_idx, :]
        cruise = self._cruise_list.cruises[row[0, "index"]]
        # Select a random school box of the corresponding ICruise and category
        box_idx = np.random.randint(0, len(cruise.school_boxes[category]))
        box = cruise.school_boxes[category][box_idx]
        # Sample a point within a selected school box
        x_min, y_min, x_max, y_max = extend_school_box(
            box=box,
            cruise=cruise,
            window_width=self._window_size["w"],
            window_height=self._window_size["h"],
        )
        # x_min = max(box[0] - self._window_size["w"] // 2, 0)
        # y_min = max(box[1] - self._window_size["h"] // 2, 0)
        # x_max = min(
        #     box[2] - self._window_size["w"] // 2,
        #     cruise.num_pings - self._window_size["w"] // 2,
        # )
        # y_max = min(
        #     box[3] - self._window_size["h"] // 2,
        #     cruise.num_ranges - self._window_size["h"] // 2,
        # )
        try:
            assert x_min < x_max
            assert y_min < y_max
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
        except AssertionError:
            x = x_min
            y = y_min
        return SamplerItem(
            x=x,
            y=y,
            x_padding=0,
            y_padding=0,
            cruise_idx=row[0, "index"],
            cruise_info=cruise.info,
            **self._window_size
        )


class GriddedSchoolSampler(BaseGriddedSampler):
    _orig_cruise_list: ICruiseList

    def full_init(self, *, cruise_list: ICruiseList) -> None:
        self._orig_cruise_list = cruise_list
        cruise_list = self._make_new_cruise_list_from_school_boxes(cruise_list)
        super().full_init(cruise_list=cruise_list)

    def _make_new_cruise_list_from_school_boxes(
        self,
        cruise_list: ICruiseList,
    ) -> ICruiseList:
        new_cruises = list()
        for cruise in cruise_list.cruises:
            for category in cruise.categories:
                for box in cruise.school_boxes[category]:
                    enlarged_box = extend_school_box(
                        box=box,
                        cruise=cruise,
                        window_width=self._grid_size["w"],
                        window_height=self._grid_size["h"],
                    )
                    new_cruises.append(
                        cruise.from_box(*enlarged_box, category=category)
                    )
        return CruiseListBase(cruises=new_cruises)

    @property
    def cruise_list(self) -> ICruiseList:
        return self._orig_cruise_list


__all__ = ["RandomSchoolSampler", "GriddedSchoolSampler"]
