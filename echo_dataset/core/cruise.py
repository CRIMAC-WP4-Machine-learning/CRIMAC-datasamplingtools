from ..utils import config, generate_data_filename_patterns
from .. import CONFIG

import xarray as xr

from dataclasses import dataclass, MISSING
from typing import Union, Optional
from pathlib import Path
import os


__all__ = ["ICruise", "CruiseConfig", "Cruise"]


class ICruise:
    @property
    def info(self) -> str:
        raise NotImplementedError

    @property
    def echogram(self) -> xr.Dataset:
        raise NotImplementedError

    @property
    def annotations_available(self) -> bool:
        raise NotImplementedError

    @property
    def annotations(self) -> xr.Dataset:
        raise NotImplementedError

    @property
    def categories(self) -> int:
        raise NotImplementedError

    @property
    def bottom_available(self) -> bool:
        raise NotImplementedError

    @property
    def bottom(self) -> xr.Dataset:
        raise NotImplementedError

    @property
    def pulse_length(self) -> float:
        raise NotImplementedError

    @property
    def frequencies(self) -> list[int, ...]:
        raise NotImplementedError

    @property
    def num_of_pings(self) -> int:
        raise NotImplementedError

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> xr.Dataset:
        """
                    Ping time
        (x1, y1)    ---->
                ┌──────────────┐
        Range │ │              │
              ▼ │              │
                └──────────────┘
                                (x2, y2)

        :param x1: array index
        :param y1: array index
        :param x2: array index
        :param y2: array index
        :return: xarray.Dataset containing the slice

        **Note**: x2 and y2 are excluded
        """
        raise NotImplementedError


@dataclass(init=False)
class CruiseConfig:
    path: Path = MISSING
    settings: dict[str, any]
    name: str = ""
    year: int = -1
    require_annotations: bool = True
    require_bottom: bool = False

    def __init__(
            self,
            path: Union[str, Path],
            name: Optional[str] = None,
            year: Optional[int] = None,
            require_annotations: Optional[bool] = None,
            require_bottom: Optional[bool] = None,
            settings: Optional[dict[str, any]] = None
    ) -> None:
        self.path = Path(path)
        self.name = name if name is not None else self.name
        self.year = year if isinstance(year, int) else self.year
        # if not isinstance(year, int):
        #     raise ValueError("Year must be int")
        # self.year = year
        if settings is not None:
            if config.is_valid(settings):
                self.settings = settings
        else:
            self.settings = CONFIG
        if require_annotations is not None:
            self.require_annotations = require_annotations
        if require_bottom is not None:
            self.require_bottom = require_bottom


class Cruise(ICruise):
    def __init__(self, conf: CruiseConfig) -> None:
        self._conf = conf
        data_filename, annotation_filename, bottom_filename = self._scan_path()
        self._data = self._read_data(data_filename, True)
        self._annotations = self._read_data(annotation_filename, self._conf.require_annotations)
        self._bottom = self._read_data(bottom_filename, self._conf.require_bottom)

    @classmethod
    def from_path(cls, path: Union[Path, str]) -> "Cruise":
        conf = CruiseConfig(path)
        return cls(conf)

    def _scan_path(self) -> list[str, str, str]:
        patterns = generate_data_filename_patterns(self._conf.settings)
        filenames = os.listdir(self._conf.path)
        match_count = 0
        out = list()
        for p in patterns:
            for name in filenames:
                if p.fullmatch(name):
                    out.append(name)
                    break
            match_count += 1
            if match_count != len(out):
                out.append("")
        return out

    def _read_data(self, filename: str, required: bool) -> xr.Dataset:
        try:
            return xr.open_zarr(
                store=self._conf.path / filename,
                chunks={'frequency': 'auto'}
            )
        except FileNotFoundError:
            if required:
                raise Exception(f"Required file not found in {self._conf.path}")
            else:
                return xr.Dataset()

    @staticmethod
    def _crop_data(
            data: xr.Dataset,
            box: list[int, int, int, int]
    ) -> xr.Dataset:
        try:
            res = data.isel(
                {
                    "ping_time": slice(box[0], box[2]),
                    "range": slice(box[1], box[3])
                }
            )
        except ValueError:
            res = data
        return res

    @property
    def path(self) -> Path:
        return self._conf.path

    @property
    def echogram(self) -> xr.Dataset:
        return self._data

    @property
    def annotations_available(self) -> bool:
        return len(self._annotations) > 0

    @property
    def annotations(self) -> xr.Dataset:
        return self._annotations

    @property
    def categories(self) -> int:
        if self.annotations_available:
            return self._annotations.category.compute().echogram.tolist()
        else:
            return -1

    @property
    def bottom_available(self) -> bool:
        return len(self._bottom) > 0

    @property
    def bottom(self) -> xr.Dataset:
        return self._bottom

    @property
    def pulse_length(self) -> float:
        try:
            return self._data.pulse_length.compute().echogram[0]
        except AttributeError:
            raise KeyError("No `pulse_length` coordinate is found")

    @property
    def frequencies(self) -> list[int, ...]:
        try:
            return self._data.frequency.compute().astype(int).to_numpy().tolist()
        except AttributeError:
            raise KeyError("No `frequency` coordinate is found")

    @property
    def num_of_pings(self) -> int:
        try:
            return len(self._data.ping_time)
        except AttributeError:
            raise KeyError("No `ping_time` coordinate is found")

    def crop(
            self,
            x1: int,
            y1: int,
            x2: int,
            y2: int
    ) -> list[xr.Dataset, xr.Dataset, xr.Dataset]:
        res = list()
        box = [x1, y1, x2, y2]
        res.append(self._crop_data(self._data, box))
        res.append(self._crop_data(self._annotations, box))
        res.append(self._crop_data(self._bottom, box))
        return res
