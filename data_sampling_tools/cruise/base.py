from ..utils.cruise import (
    parse_cruises,
    generate_data_filename_patterns,
    filter_cruise_table,
)
from ..core import (
    ICruise,
    ICruiseList,
    SchoolBoxesOrigin,
    FilterConfig,
    CruiseConfig,
    PSEUDO_CRUISE_NAMING,
)
from ..utils.misc import box_contains

import polars as pl
import xarray as xr
import cv2 as cv

from typing import Union, TypeVar, Optional, Sequence, Iterable, Callable
from collections import defaultdict
from pprint import PrettyPrinter
from pathlib import Path
import warnings
import os


class CruiseBase(ICruise):
    Self = TypeVar("Self", bound="CruiseBase")

    _conf: CruiseConfig
    _echogram: xr.Dataset
    _annotations: xr.Dataset
    _bottom: xr.Dataset
    _school_boxes: dict[int, list[tuple[int, int, int, int], ...]]
    _school_boxes_origin: SchoolBoxesOrigin
    _info_formatter: Callable[[object], str]

    def __init__(self, conf: CruiseConfig) -> None:
        self._conf = conf
        filenames = self._scan_path()
        self._info_formatter = PrettyPrinter(indent=2).pformat
        self._echogram = self._read_data(
            filename=filenames["echogram"],
            required=True,  # data (echogram) is always required
            data_name=self._conf.zarr_keys.echogram_key,
        )
        self._annotations = self._read_data(
            filename=filenames["annotation"],
            required=self._conf.require_annotations,
            data_name=self._conf.zarr_keys.annotations_key,
        )
        self._bottom = self._read_data(
            filename=filenames["bottom"],
            required=self._conf.require_bottom,
            data_name=self._conf.zarr_keys.bottom_key,
        )
        self._school_boxes_origin = SchoolBoxesOrigin.NOT_AVAILABLE
        if (not self._conf.force_find_school_boxes) and filenames["schools"] != "":
            self._school_boxes = self._load_school_boxes(filenames["schools"])
            self._school_boxes_origin = SchoolBoxesOrigin.CSV
        else:
            self._school_boxes = self._find_school_boxes()
            self._school_boxes_origin = SchoolBoxesOrigin.CONTOUR_SEARCH

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
        return self._info_formatter(self.info)

    def _scan_path(self) -> dict[str, str]:
        patterns = generate_data_filename_patterns(self._conf)
        filenames = os.listdir(self._conf.path)
        match_count = 0
        out = dict()
        for k, p in patterns.items():
            for name in filenames:
                if p.fullmatch(name):
                    out[k] = name
                    break
            match_count += 1
            if match_count != len(out):
                out[k] = ""
        return out

    def _read_data(self, filename: str, required: bool, data_name: str) -> xr.Dataset:
        try:
            val = xr.open_zarr(
                store=self._conf.path / filename, chunks={"frequency": "auto"}
            )
            if val.isnull().any():
                warnings.warn(
                    f"NaN values encountered while reading `{data_name}` data in cruise:\n{self}",
                    RuntimeWarning,
                )
            return val
        except FileNotFoundError:
            if required:
                raise FileNotFoundError(
                    f"Required data `{data_name}` not found for cruise:\n{self}"
                )
            else:
                warnings.warn(
                    f"Optional data `{data_name}` is not found for cruise:\n{self._conf}"
                )
                return xr.Dataset()

    # TODO: fix to work with correct annotations and test; not recommended for use
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
        schools = pl.read_csv(source=self._conf.path / filepath, has_header=True)
        schools = schools.filter(
            (pl.col("category") > 0)
            & (pl.col("startpingindex") >= 0)
            & (pl.col("endpingindex") >= 0)
            & (pl.col("upperdepthindex") >= 0)
            & (pl.col("lowerdepthindex") >= 0)
        )
        boxes = defaultdict(list)
        for i in range(len(schools)):
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
        return dict(self._conf)

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
        return self._school_boxes

    @property
    def school_boxes_origin(self) -> SchoolBoxesOrigin:
        return self._school_boxes_origin

    @property
    def bottom_available(self) -> bool:
        return len(self._bottom) > 0

    @property
    def bottom(self) -> xr.Dataset:
        return self._bottom

    def from_box(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        *,
        category: int = -1,
        force_find_school_boxes: bool = False,
    ) -> Self:
        try:
            assert x1 < x2
            assert y1 < y2
        except AssertionError:
            raise ValueError("Inconsistent box dimensions")
        new_conf_dict = dict(self._conf)
        new_conf_dict["name"] = PSEUDO_CRUISE_NAMING(
            new_conf_dict["name"], category, x1, y1, x2, y2
        )
        # new_conf_dict["name"] += f"-cat[{category}]-box[{x1},{y1},{x2},{y2}]"
        cruise = self._from_box(conf=CruiseConfig(**new_conf_dict))
        cruise._echogram = cruise._echogram.isel(
            {
                self._conf.zarr_keys.range_key: slice(y1, y2),
                self._conf.zarr_keys.ping_time_key: slice(x1, x2),
            }
        )
        if cruise.annotations_available:
            cruise._annotations = cruise._annotations.isel(
                {
                    self._conf.zarr_keys.range_key: slice(y1, y2),
                    self._conf.zarr_keys.ping_time_key: slice(x1, x2),
                }
            )
        if cruise.bottom_available:
            cruise._bottom = cruise._bottom.isel(
                {
                    self._conf.zarr_keys.range_key: slice(y1, y2),
                    self._conf.zarr_keys.ping_time_key: slice(x1, x2),
                }
            )
        new_school_boxes = list()
        if cruise.annotations_available:
            for box in cruise._school_boxes[category]:
                contained_box = box_contains(
                    domain_box=tuple([x1, y1, x2, y2]), other_box=box
                )
                if len(contained_box) == 4:
                    new_box = tuple(
                        [
                            contained_box[0] - x1,
                            contained_box[1] - y1,
                            contained_box[2] - x1,
                            contained_box[3] - y1,
                        ]
                    )
                    new_school_boxes.append(new_box)
                else:
                    continue
            cruise._school_boxes = {category: new_school_boxes}
        return cruise

    @classmethod
    def _from_box(cls, conf: CruiseConfig) -> Self:
        return cls(conf=conf)

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> dict[str, xr.Dataset]:
        res = dict()
        box = (x1, y1, x2, y2)
        res[self._conf.zarr_keys.echogram_key] = self._crop_data(self._echogram, box)
        res[self._conf.zarr_keys.annotations_key] = self._crop_data(
            self._annotations, box
        )
        res[self._conf.zarr_keys.bottom_key] = self._crop_data(self._bottom, box)
        return res

    def _crop_data(
        self, data: xr.Dataset, box: tuple[int, int, int, int]
    ) -> xr.Dataset:
        return data.isel(
            {
                self._conf.zarr_keys.range_key: slice(box[1], box[3]),
                self._conf.zarr_keys.ping_time_key: slice(box[0], box[2]),
            }
        )


class CruiseListBase(ICruiseList):
    Self = TypeVar("Self", bound="CruiseListBase")

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

    def __iter__(self) -> Iterable[ICruise]:
        return self.cruises

    def __repr__(self) -> str:
        return str(self._table)

    @property
    def table(self) -> pl.DataFrame:
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

    def from_filter(self, filter_conf: FilterConfig, partition_name: str) -> Self:
        new_cruise_list = CruiseListBase(cruises=self._cruises)
        new_cruise_list._table = filter_cruise_table(
            cruise_table=new_cruise_list.table,
            filter_conf=filter_conf,
            partition_name=partition_name,
        )
        return new_cruise_list

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
