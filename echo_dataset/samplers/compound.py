from ..core.sampler import IStatelessSampler, ICompoundSamplerComponent
from ..core.custom_types import TCompoundSamplerComponentObject
from ..utils.samplers import validate_window_size

import datatable as dt
import xarray as xr
import numpy as np

from typing import Sequence, Optional, Union


class CompoundSampler(IStatelessSampler):
    _window_size: tuple[int, int]
    _components: tuple[ICompoundSamplerComponent, ...]
    _weights: tuple[float, ...]

    def __init__(
        self,
        components: Sequence[TCompoundSamplerComponentObject],
        window_size: Union[int, Sequence[int]],
        weights: Optional[Sequence[float]] = None,
        component_options: Optional[Sequence[dict[str, any]]] = None,
    ) -> None:
        validate_window_size(window_size=window_size)
        self._window_size = (
            tuple([window_size, window_size])
            if isinstance(window_size, int)
            else tuple(window_size)
        )
        try:
            assert all([issubclass(c, ICompoundSamplerComponent) for c in components])
        except AssertionError:
            raise Exception("Wrong type is passed for `components` argument.")
        try:
            if component_options is not None:
                assert len(component_options) == len(components)
        except AssertionError:
            raise Exception("The number of options must match the number of components")
        self._components = tuple(
            [c(window_size, **opt) for c, opt in zip(components, component_options)]
        )
        if weights is None:
            self._weights = tuple([1 / len(self._components)] * len(self._components))
        else:
            try:
                assert len(weights) == len(self._components)
            except AssertionError:
                raise Exception(
                    "Number of weights doesn't match the number of samplers."
                )
            try:
                assert sum(weights) == 1
            except AssertionError:
                raise Exception("Weights must sum to 1.")
            self._weights = tuple(weights)

    def full_init(self, *, ds_summary: dt.Frame, **kwargs: any) -> None:
        for c in self._components:
            c.full_init(ds_summary=ds_summary, **kwargs)

    def __call__(self, *args, **kwargs) -> dict[str, xr.Dataset]:
        sampler_idx = np.random.choice(len(self._components), p=self._weights)
        return self._components[sampler_idx](*args, **kwargs)

    @property
    def components(self) -> tuple[ICompoundSamplerComponent, ...]:
        return self._components
