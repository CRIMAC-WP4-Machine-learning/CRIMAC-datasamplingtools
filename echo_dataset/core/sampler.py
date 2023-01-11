import xarray as xr

from typing import Sequence
import random


__all__ = ["ISampler", "RandomSchoolSampler", "RandomBackgroundSampler"]


class ISampler:
    _window_size: tuple[int, int]
    _categories: list[int, ...] = None

    def __call__(self, ds: any) -> dict[str, xr.Dataset]:
        raise NotImplementedError

    def init(self, categories: Sequence[int]) -> None:
        self._categories = list(categories)

    @property
    def window_size(self) -> tuple[int, int]:
        return self._window_size


class RandomSchoolSampler(ISampler):
    def __init__(self, window_size: Sequence[int]) -> None:
        if len(window_size) == 2 and all(isinstance(v, int) for v in window_size):
            self._window_size = tuple(window_size)
        else:
            raise Exception("Must be a sequence of two integers")

    def __call__(self, ds: any) -> dict[str, xr.Dataset]:
        if self._categories is None:
            raise ValueError
        category_idx = random.randint(1, len(self._categories))
        cruise_idx = random.randint(1, ds.num_cruises)
        school_boxes = ds.schools(
            cruise_idx=cruise_idx - 1,
            fish_category=self._categories[category_idx - 1]
        )
        while True:
            box_idx = random.randint(1, len(school_boxes))
            box = school_boxes[box_idx - 1]
            x_min = box[0]
            x_max = box[2] - self.window_size[0] - 1
            y_min = box[1]
            y_max = box[3] - self.window_size[1] - 1
            if x_max < x_min or y_max < y_min:
                continue
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            x += random.randint(
                -self.window_size[0] // 2, self.window_size[0] // 2
            )
            y += random.randint(
                -self.window_size[1] // 2, self.window_size[1] // 2
            )
            return ds.crop(
                cruise_idx=cruise_idx - 1,
                box=[x, y, x + self.window_size[0], y + self.window_size[1]]
            )


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
        x_max = ds.total_num_pings - self._window_size[0] - 1
        while True:
            while True:
                x = random.randint(0, x_max)
                max_ping = None
                for i, k in enumerate(ds.ping_range_map):
                    if x < k:
                        max_ping = k
                        break
                assert i is not None
                assert max_ping is not None
                if (x + self._window_size[0]) < max_ping:
                    break
            y = random.randint(0, ds.ping_range_map[max_ping] - self.window_size[1] - 1)
            window = ds.crop(
                cruise_idx=i,
                box=[
                    x,
                    y,
                    x + self._window_size[0],
                    y + self._window_size[1],
                ],
            )
            if not window["annotations"]["annotation"].any().compute():
                return window

    def _generate_point(self) -> list[int, int]:
        raise NotImplementedError


class RandomBackgroundSampler(ISampler):
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
