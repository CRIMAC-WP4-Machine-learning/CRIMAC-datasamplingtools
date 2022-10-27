from ..utils import generate_data_filename_patterns
from ..utils.module_config import is_valid
from .. import CONFIG

import xarray as xr
import numpy as np
import cv2 as cv

from dataclasses import dataclass, MISSING
from typing import Union, Optional
from pathlib import Path
import warnings
import os


__all__ = ["ICruise", "CruiseConfig", "Cruise"]


class ICruise:
    _echogram_key: str
    _annotations_key: str
    _bottom_key: str
    _school_boxes: dict[int, list[list[int, int, int, int], ...]]

    @property
    def info(self) -> dict[str, any]:
        raise NotImplementedError

    @property
    def path(self) -> Path:
        raise NotImplementedError

    @property
    def echogram_key(self) -> str:
        raise NotImplementedError

    @property
    def annotations_key(self) -> str:
        raise NotImplementedError

    @property
    def bottom_key(self) -> str:
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
    def categories(self) -> list[int, ...]:
        raise NotImplementedError

    @property
    def bottom_available(self) -> bool:
        raise NotImplementedError

    @property
    def bottom(self) -> xr.Dataset:
        raise NotImplementedError

    @property
    def frequencies(self) -> list[int, ...]:
        raise NotImplementedError

    @property
    def num_pings(self) -> int:
        raise NotImplementedError

    @property
    def num_ranges(self) -> int:
        raise NotImplementedError

    @property
    def school_boxes(self) -> dict[int, list[list[int, int, int, int], ...]]:
        return self._school_boxes

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> dict[str, xr.Dataset]:
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
    name: str
    year: int
    require_annotations: bool
    require_bottom: bool

    def __init__(
            self,
            path: Union[str, Path],
            name: Optional[str] = None,
            year: Optional[int] = None,
            require_annotations: bool = False,
            require_bottom: bool = False,
            settings: Optional[dict[str, any]] = None
    ) -> None:
        self.path = Path(path)
        self.name = name
        self.year = year
        self.require_annotations = require_annotations
        self.require_bottom = require_bottom
        if settings is not None:
            if is_valid(settings):
                self.settings = settings
        else:
            self.settings = CONFIG


class Cruise(ICruise):
    def __init__(self, conf: CruiseConfig) -> None:
        self._echogram_key = "echogram"
        self._annotations_key = "annotations"
        self._bottom_key = "bottom"
        self._conf = conf
        data_filename, annotation_filename, bottom_filename = self._scan_path()
        self._data = self._read_data(
            filename=data_filename,
            required=True,
            data_name=self._echogram_key
        )
        self._annotations = self._read_data(
            filename=annotation_filename,
            required=self._conf.require_annotations,
            data_name=self._annotations_key
        )
        self._bottom = self._read_data(
            filename=bottom_filename,
            required=self._conf.require_bottom,
            data_name=self._bottom_key
        )
        self._school_boxes = self._find_school_boxes()

    @classmethod
    def from_path(
            cls,
            path: Union[Path, str],
            require_annotations: bool = False,
            require_bottom: bool = False
    ) -> "Cruise":
        conf = CruiseConfig(
            path=path,
            require_annotations=require_annotations,
            require_bottom=require_bottom
        )
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

    def _read_data(self, filename: str, required: bool, data_name: str) -> xr.Dataset:
        try:
            return xr.open_zarr(
                store=self._conf.path / filename,
                chunks={'frequency': 'auto'}
            )
        except FileNotFoundError:
            if required:
                raise Exception(f"Required file not found in {self.path}")
            else:
                warnings.warn(
                    f"Optional data ({data_name}) is not found for {self.path} cruise"
                )
                return xr.Dataset()

    def _find_school_boxes(self) -> dict[int, list[list[int, int, int, int], ...]]:
        schools = dict()
        for c in self._annotations.category:
            if c == -1:
                continue
            c = int(c)
            schools[c] = list()
            mask = self._annotations.sel({"category": c}).annotation.compute().data.T
            contours, _ = cv.findContours(
                mask.astype(np.uint8), cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
            )
            for cont in contours:
                x, y, w, h = cv.boundingRect(cont)
                schools[c].append([x, y, x + w, y + h])
        return schools

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
    def echogram_key(self) -> str:
        return self._echogram_key

    @property
    def annotations_key(self) -> str:
        return self._annotations_key

    @property
    def bottom_key(self) -> str:
        return self._bottom_key

    @property
    def info(self) -> dict[str, any]:
        res = dict()
        res["name"] = self._conf.name
        res["year"] = self._conf.year
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
    def categories(self) -> list[int, ...]:
        if self.annotations_available:
            return self._annotations.category.compute().to_numpy().tolist()
        else:
            return []

    @property
    def bottom_available(self) -> bool:
        return len(self._bottom) > 0

    @property
    def bottom(self) -> xr.Dataset:
        return self._bottom

    @property
    def frequencies(self) -> list[int, ...]:
        try:
            return self._data.frequency.compute().astype(int).to_numpy().tolist()
        except AttributeError:
            raise KeyError("No `frequency` coordinate is found")

    @property
    def num_pings(self) -> int:
        try:
            return len(self._data.ping_time)
        except AttributeError:
            raise KeyError("No `ping_time` coordinate is found")

    @property
    def num_ranges(self) -> int:
        try:
            return len(self._data.range)
        except AttributeError:
            raise KeyError("No `range` coordinate is found")

    def crop(
            self,
            x1: int,
            y1: int,
            x2: int,
            y2: int
    ) -> dict[str, xr.Dataset]:
        res = dict()
        box = [x1, y1, x2, y2]
        res[self._echogram_key] = self._crop_data(self._data, box)
        res[self._annotations_key] = self._crop_data(self._annotations, box)
        res[self._bottom_key] = self._crop_data(self._bottom, box)
        return res
