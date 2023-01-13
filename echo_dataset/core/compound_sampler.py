from ..core.sampler import ISampler

import xarray as xr
import numpy as np

from typing import Sequence, Optional


__all__ = ["ICompoundSampler", "CompoundSampler"]


class ICompoundSampler:
    _window_size: tuple[int, int]
    _sampler_objs: list[type, ...]
    _samplers: list[ISampler, ...]
    _weights: list[float, ...]

    def __len__(self) -> int:
        return len(self._samplers)

    def _init_samplers(self) -> list[ISampler, ...]:
        samplers = list()
        for so in self._sampler_objs:
            samplers.append(so(self._window_size))
        return samplers

    def __call__(self, ds: "IEchoDataset") -> dict[str, xr.Dataset]:
        sampler_idx = np.random.choice(len(self), p=self._weights)
        return self._samplers[sampler_idx](ds)

    def init(self, categories: Sequence[int]) -> None:
        for s in self._samplers:
            s.init(categories)

    @property
    def window_size(self) -> tuple[int, int]:
        return self._window_size


class CompoundSampler(ICompoundSampler):
    def __init__(
        self,
        samplers: Sequence[type],
        window_size: tuple[int, int],
        weights: Optional[Sequence[float]] = None,
    ) -> None:
        super()._window_size = window_size
        super()._sampler_objs = samplers
        self._samplers = super()._init_samplers()
        if weights is None:
            self._weights = [1 / len(self)] * len(self)
        else:
            assert len(weights) == len(
                self
            ), "Number of weights doesn't match the number of samplers"
            assert sum(weights) == 1, "Weights must sum to 1"
            self._weights = list(weights)
