from ..utils.patterns import generate_data_filename_patterns
from ..utils.module_config import module_cfg_is_valid
from ..utils.cruise import parse_cruises
from ..core import ICruise, ICruiseList
from .. import CONFIG

import datatable as dt
import xarray as xr
import cv2 as cv

from typing import Union, TypeVar, Optional, Sequence
from dataclasses import dataclass, MISSING
from collections import defaultdict
from pathlib import Path
import warnings
import os


Self = TypeVar("Self", bound="CruiseBase")


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
        settings: Optional[dict[str, any]] = None,
    ) -> None:
        self.path = Path(path)
        self.name = name
        self.year = year
        self.require_annotations = require_annotations
        self.require_bottom = require_bottom
        if settings is not None:
            merged_settings = CONFIG | settings
            if module_cfg_is_valid(merged_settings):
                self.settings = merged_settings
        else:
            self.settings = CONFIG


class CruiseBase(ICruise):
    __echogram_key = "echogram"
    __annotations_key = "annotations"
    __bottom_key = "bottom"
    __ping_time_key = "ping_key"
    __range_key = "range"

    def __init__(
        self, conf: CruiseConfig, force_find_school_boxes: bool = False
    ) -> None:
        self._conf = conf
        self._info = dict()
        self._info["name"] = self._conf.name
        self._info["year"] = self._conf.year
        (
            echogram_filename,
            annotation_filename,
            bottom_filename,
            schools_filename,
        ) = self._scan_path()
        self._echogram = self._read_data(
            filename=echogram_filename, required=True, data_name=self.__echogram_key
        )
        self._annotations = self._read_data(
            filename=annotation_filename,
            required=self._conf.require_annotations,
            data_name=self.__annotations_key,
        )
        self._bottom = self._read_data(
            filename=bottom_filename,
            required=self._conf.require_bottom,
            data_name=self.__bottom_key,
        )
        self._school_boxes_origin = "not available"
        if (not force_find_school_boxes) and schools_filename != "":
            self._school_boxes = self._load_school_boxes(schools_filename)
            self._school_boxes_origin = "csv"
        else:
            self._school_boxes = self._find_school_boxes()
            self._school_boxes_origin = "contour search"

    @classmethod
    def from_path(
        cls,
        path: Union[Path, str],
        require_annotations: bool = False,
        require_bottom: bool = False,
    ) -> Self:
        conf = CruiseConfig(
            path=path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
        )
        return cls(conf)

    def __repr__(self) -> str:
        return str(self.info)

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

    # TODO: add data validation -- basic checks for NaN and other breaking conditions
    def _read_data(self, filename: str, required: bool, data_name: str) -> xr.Dataset:
        try:
            return xr.open_zarr(
                store=self._conf.path / filename, chunks={"frequency": "auto"}
            )
        except FileNotFoundError:
            if required:
                raise Exception(f"Required data `{data_name}` not found in {self.path}")
            else:
                warnings.warn(
                    f"Optional data `{data_name}` is not found for {self.path} cruise"
                )
                return xr.Dataset()

    def _find_school_boxes(
        self,
    ) -> dict[int, list[tuple[int, int, int, int], ...]]:
        schools = dict()
        if not self.annotations_available:
            return schools
        for c in self._annotations.category:
            c = c.data.item()
            if c == -1:
                continue
            c = int(c) if not isinstance(c, int) else c
            schools[c] = list()
            mask = self._annotations.sel({"category": c}).annotation.compute().data.T
            contours, _ = cv.findContours(
                image=mask.astype("B"),
                mode=cv.RETR_EXTERNAL,
                method=cv.CHAIN_APPROX_SIMPLE,
            )
            for cont in contours:
                x, y, w, h = cv.boundingRect(array=cont)
                schools[c].append((x, y, x + w, y + h))
        return dict(schools)

    def _load_school_boxes(
        self, filepath: str
    ) -> dict[int, list[tuple[int, int, int, int], ...]]:
        if not self.annotations_available:
            return dict()
        schools = dt.fread(file=self._conf.path / filepath, header=True)
        schools = schools[
            (dt.f.category > 0)
            & (dt.f.startpingindex >= 0)
            & (dt.f.endpingindex >= 0)
            & (dt.f.upperdepthindex >= 0)
            & (dt.f.lowerdepthindex >= 0),
            :,
        ]
        boxes = defaultdict(list)
        for i in range(schools.nrows):
            boxes[schools[i, "category"]].append(
                (
                    schools[i, "startpingindex"],
                    schools[i, "upperdepthindex"],
                    schools[i, "endpingindex"],
                    schools[i, "lowerdepthindex"],
                )
            )
        return boxes

    @property
    def info(self) -> dict[str, any]:
        return self._info

    @property
    def path(self) -> Path:
        return self._conf.path

    @property
    def echogram(self) -> xr.Dataset:
        return self._echogram

    @property
    def frequencies(self) -> tuple[int, ...]:
        try:
            return self._echogram.frequency.compute().astype(int).to_numpy().tolist()
        except AttributeError:
            raise KeyError("No `frequency` coordinate is found")

    @property
    def num_pings(self) -> int:
        try:
            return len(self._echogram.ping_time)
        except AttributeError:
            raise KeyError("No `ping_time` coordinate is found")

    @property
    def num_ranges(self) -> int:
        try:
            return len(self._echogram.range)
        except AttributeError:
            raise KeyError("No `range` coordinate is found")

    @property
    def annotations_available(self) -> bool:
        return len(self._annotations) > 0

    @property
    def annotations(self) -> xr.Dataset:
        return self._annotations

    @property
    def categories(self) -> tuple[int, ...]:
        if self.annotations_available:
            return tuple(self._school_boxes.keys())
        else:
            return tuple()

    @property
    def school_boxes(
        self,
    ) -> dict[int, list[tuple[int, int, int, int], ...]]:
        raise self._school_boxes

    @property
    def school_boxes_origin(self) -> str:
        return self._school_boxes_origin

    @property
    def bottom_available(self) -> bool:
        return len(self._bottom) > 0

    @property
    def bottom(self) -> xr.Dataset:
        return self._bottom

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> dict[str, xr.Dataset]:
        res = dict()
        box = (x1, y1, x2, y2)
        res[self.__echogram_key] = self._crop_data(self._echogram, box)
        res[self.__annotations_key] = self._crop_data(self._annotations, box)
        res[self.__bottom_key] = self._crop_data(self._bottom, box)
        return res

    def _crop_data(
        self, data: xr.Dataset, box: tuple[int, int, int, int]
    ) -> xr.Dataset:
        return data.isel(
            {
                self.__ping_time_key: slice(box[0], box[2]),
                self.__range_key: slice(box[1], box[3]),
            }
        )


class CruiseListBase(ICruiseList):
    def __init__(self, cruises: Sequence[ICruise]):
        self._cruises = tuple(cruises)
        (
            self._table,
            self._total_num_pings,
            self._cruise_ping_fractions,
            self._min_range_len,
            self._max_range_len,
            self._frequencies,
            self._categories,
        ) = parse_cruises(cruises)

    def __len__(self) -> int:
        return len(self._cruises)

    def __repr__(self) -> str:
        return str(self._table)

    @property
    def table(self) -> dt.Frame:
        return self._table

    @property
    def cruises(self) -> tuple[ICruise, ...]:
        return self._cruises

    @property
    def cruise_ping_fractions(self) -> tuple[float, ...]:
        return self._cruise_ping_fractions

    @property
    def total_num_pings(self) -> int:
        return self._total_num_pings

    @property
    def min_range_len(self) -> int:
        return self._min_range_len

    @property
    def max_range_len(self) -> int:
        return self._max_range_len

    @property
    def is_ping_uniform(self) -> bool:
        return self.max_range_len == self.min_range_len

    @property
    def categories(self) -> tuple[int, ...]:
        return self._categories

    @property
    def frequencies(self) -> tuple[int, ...]:
        return self._frequencies

    def school_boxes(
        self, cruise_idx: int, fish_category: Optional[int] = None
    ) -> Union[
        dict[int, list[tuple[int, int, int, int], ...]], list[tuple[int, int, int, int]]
    ]:
        if fish_category is None:
            return self._cruises[cruise_idx].school_boxes
        else:
            return self._cruises[cruise_idx].school_boxes[fish_category]

    def crop(self, cruise_idx: int, box: Sequence[int]) -> dict[str, xr.Dataset]:
        return self._cruises[cruise_idx].crop(*box)


__all__ = ["CruiseConfig", "CruiseBase", "CruiseListBase"]
