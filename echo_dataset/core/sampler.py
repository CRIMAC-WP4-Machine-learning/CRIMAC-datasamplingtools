import xarray as xr


__all__ = ["ISampler"]


class ISampler:
    def __call__(self, *args, **kwargs) -> dict[str, any]:
        raise NotImplementedError


class RandomSchoolSampler(ISampler):
    def __init__(self) -> None:
        raise NotImplementedError

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