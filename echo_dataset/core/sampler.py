import xarray as xr

from typing import Sequence
import random


__all__ = ["ISampler", "RandomSchoolSampler", "RandomBackgroundSampler"]


class ISampler:
    _window_size: tuple[int, int]
    _categories: list[int, ...]

    def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
        raise NotImplementedError

    def init(self, categories: Sequence[int]) -> None:
        self._categories = list(categories)

    @property
    def window_size(self) -> tuple[int, int]:
        return self._window_size


class RandomSchoolSampler(ISampler):
    def __init__(self, window_size: Sequence[int]) -> None:
        if len(window_size) == 2 and all(
            isinstance(v, int) for v in window_size
        ):
            # noinspection PyTypeChecker
            self._window_size = tuple(window_size)
        else:
            raise Exception("Must be a sequence of exactly two integers")

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
            if (y_max + self._window_size[1]) > ds.cruise(
                cruise_idx
            ).num_ranges:
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


class RandomBackgroundSampler(ISampler):
    def __init__(self, window_size: Sequence[int]) -> None:
        if len(window_size) == 2 and all(
            isinstance(v, int) for v in window_size
        ):
            # noinspection PyTypeChecker
            self._window_size = tuple(window_size)
        else:
            raise Exception("Must be a sequence of exactly two integers")

    def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
        if self._categories is None:
            raise ValueError
        x_max = ds.total_num_pings - self._window_size[0]
        while True:
            while True:
                x = random.randint(0, x_max)
                max_ping = None
                for i, k in enumerate(ds.ping_range_map):
                    if (x + self._window_size[0]) <= k:
                        max_ping = k
                        break
                assert i is not None
                assert max_ping is not None
                break
            y = random.randint(
                0, ds.ping_range_map[max_ping] - self.window_size[1]
            )
            window = ds.crop(
                cruise_idx=i,
                box=[
                    max_ping - x,
                    y,
                    max_ping - x + self._window_size[0],
                    y + self._window_size[1],
                ],
            )

            # window = ds.crop(
            #     cruise_idx=i,
            #     box=[
            #         ds.cruise(i).num_pings - self._window_size[0],
            #         ds.cruise(i).num_ranges - self._window_size[1],
            #         ds.cruise(i).num_pings,
            #         ds.cruise(i).num_ranges,
            #     ],
            # )

            # TODO: remove asserts in prod
            cond = [
                window["echogram"].ping_time.size == self._window_size[0],
                window["echogram"].range.size == self._window_size[1],
                window["annotations"].ping_time.size == self._window_size[0],
                window["annotations"].range.size == self._window_size[1],
                window["bottom"].ping_time.size == self._window_size[0],
                window["bottom"].range.size == self._window_size[1],
            ]
            if sum(cond) != len(cond):
                continue

            if window["annotations"]["annotation"].isnull().any().compute():
                continue
            if window["echogram"]["sv"].isnull().any().compute():
                continue

            if not window["annotations"]["annotation"].any().compute():
                return window

    def _generate_point(self) -> list[int, int]:
        raise NotImplementedError


class RandomBottomSampler(ISampler):
    def __init__(self) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
        raise NotImplementedError

    def _generate_point(self) -> list[int, int]:
        raise NotImplementedError


class RandomNoiseSampler(ISampler):
    def __init__(self) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
        raise NotImplementedError

    def _generate_point(self) -> list[int, int]:
        raise NotImplementedError
