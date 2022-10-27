import xarray as xr

from typing import Sequence


__all__ = ["ISampler"]


class ISampler:
    _window_size: tuple[int, int]

    def __call__(self, *args, **kwargs) -> dict[str, any]:
        raise NotImplementedError

    @property
    def window_size(self) -> tuple[int, int]:
        return self._window_size


class RandomSchoolSampler(ISampler):
    def __init__(self, window_size: Sequence[int]) -> None:
        if len(window_size) == 2 and all(isinstance(v, int) for v in window_size):
            self._window_size = tuple(window_size)
        else:
            raise TypeError

    def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:

        raise NotImplementedError

    def _generate_point(self) -> list[int, int]:
        raise NotImplementedError


class RandomBottomSampler(ISampler):
    def __init__(self) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
        raise NotImplementedError

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