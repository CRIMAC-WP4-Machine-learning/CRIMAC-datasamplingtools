from .cruise import Cruise

import datatable as dt
import xarray as xr

from pathlib import Path
from typing import Union


class ISurvey:
    @property
    def cruises(self) -> list[Cruise, ...]:
        raise NotImplementedError

    def crop(
            self,
            cruise_idx: int,
            x1: int,
            y1: int,
            x2: int,
            y2: int
    ) -> list[xr.Dataset, xr.Dataset, xr.Dataset]:
        raise NotImplementedError


class Survey(ISurvey):
    def __init__(self, table: dt.Frame) -> None:
        self._table = table
        self._cruises = self._init_cruises(table)

    @classmethod
    def from_root_dir(cls, root_path: Union[str, Path]):
        raise NotImplementedError

    @classmethod
    def from_cruises(cls, cruises: list[Cruise, ...]):
        raise NotImplementedError

    def __len__(self) -> int:
        return len(self._cruises)

    def _init_cruises(self, table: dt.Frame) -> list[Cruise, ...]:
        pass

    @property
    def cruises(self) -> list[Cruise, ...]:
        return self._cruises

    def crop(
            self,
            cruise_idx: int,
            x1: int,
            y1: int,
            x2: int,
            y2: int
    ) -> list[xr.Dataset, xr.Dataset, xr.Dataset]:
        return self._cruises[cruise_idx].crop(x1, y1, x2, y2)


