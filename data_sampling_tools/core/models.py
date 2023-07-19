from ..module_config import CruiseNamings
from .. import CONFIG

from pydantic import BaseModel, validator
import polars as pl

from typing import Optional, Union, Callable
from pathlib import Path
from enum import Enum


class SchoolBoxesOrigin(Enum):
    NOT_AVAILABLE = 1
    CSV = 2
    CONTOUR_SEARCH = 3


CRUISE_TABLE_COLUMNS: dict[str, pl.PolarsDataType] = {
    "name": pl.Utf8,
    "year": pl.UInt16,
    "index": pl.UInt16,
    "category": pl.UInt16,
    "frequencies": pl.List(pl.UInt32),
    "full_path": pl.Utf8,
    "annotations_available": pl.Boolean,
    "bottom_available": pl.Boolean,
}
FILTER2TABLE_MAP: dict[str, str] = {
    "names": "name",
    "years": "year",
    "indices": "index",
    "categories": "category",
    "frequencies": "frequencies",
    "full_paths": "full_path",
    "with_annotations_only": "annotations_available",
    "with_bottom_only": "bottom_available",
}
PSEUDO_CRUISE_NAMING = (
    lambda n, c, x1, y1, x2, y2: f"{n}-cat[{c}]-box[{x1},{y1},{x2},{y2}]"
)
# PSEUDO_CRUISE_NAME_PATTERN = r".*-cat\[(-?\d+)\]-box\[(\d+),(\d+),(\d+),(\d+)\]"


class PartitionFilterPredicates:
    names: Callable[[list[int, ...]], bool] = lambda _, ref_names: pl.col(
        FILTER2TABLE_MAP["names"]
    ).apply(lambda x: x in ref_names, return_dtype=pl.Boolean)
    years: Callable[[list[int, ...]], bool] = lambda _, ref_years: pl.col(
        FILTER2TABLE_MAP["years"]
    ).apply(lambda x: x in ref_years, return_dtype=pl.Boolean)
    with_annotations_only: Callable[[bool], bool] = lambda _, flag: pl.col(
        FILTER2TABLE_MAP["with_annotations_only"]
    ).apply(lambda x: x is flag if flag is True else True, return_dtype=pl.Boolean)
    with_bottom_only: Callable[[bool], bool] = lambda _, flag: pl.col(
        FILTER2TABLE_MAP["with_bottom_only"]
    ).apply(lambda x: x is flag if flag is True else True, return_dtype=pl.Boolean)


class PartitionFilterConfig(BaseModel):
    _predicates: PartitionFilterPredicates = PartitionFilterPredicates()
    names: set[str, ...] = {}
    years: set[int, ...] = {}
    with_annotations_only: bool = False
    with_bottom_only: bool = False

    @validator("names", "years", pre=True)
    def convert_inputs(cls, val: any) -> Union[set[str, ...], set[int, ...], set[()]]:
        if val is None:
            return set()
        if isinstance(val, str) or isinstance(val, int):
            return {val}
        if isinstance(val, list) or isinstance(val, set):
            if all(v is None for v in val):
                return set()
            else:
                return set(val)
        return val

    @validator("years")
    def valid_years(cls, vals: set[int, ...]) -> set[int, ...]:
        for v in vals:
            if v < 0:
                raise ValueError("Year cannot be negative.")
        return vals

    @property
    def predicates(self) -> PartitionFilterPredicates:
        return self._predicates

    class Config:
        underscore_attrs_are_private = True


class FilterPredicates:
    frequencies: Callable[[list[int, ...]], bool] = lambda _, ref_frequencies: pl.col(
        FILTER2TABLE_MAP["frequencies"]
    ).apply(lambda x: ref_frequencies.issubset(set(x)), return_dtype=pl.Boolean)
    categories: Callable[[list[int, ...]], bool] = lambda _, ref_categories: pl.col(
        FILTER2TABLE_MAP["categories"]
    ).apply(
        lambda x: x in ref_categories,
        return_dtype=pl.Boolean,
    )


class FilterConfig(BaseModel):
    _predicates: FilterPredicates = FilterPredicates()
    frequencies: set[int, ...] = set()
    categories: set[int, ...] = set()
    partition_filters: dict[str, PartitionFilterConfig] = dict()

    @validator("frequencies", "categories", pre=True)
    def convert_inputs(cls, val) -> Union[set[int, ...], set[()]]:
        if val is None:
            return set()
        if isinstance(val, int):
            return {val}
        if isinstance(val, list) or isinstance(val, set):
            if all(v is None for v in val):
                return set()
            else:
                return set(val)
        return val

    @property
    def predicates(self) -> FilterPredicates:
        return self._predicates

    class Config:
        underscore_attrs_are_private = True


class DatasetConfig(BaseModel):
    data_filter: FilterConfig


class ZARRKeys(BaseModel):
    echogram_key: str = "echogram"
    annotations_key: str = "annotations"
    bottom_key: str = "bottom"
    ping_time_key: str = "ping_time"
    range_key: str = "range"


class CruiseConfig(BaseModel):
    path: Path
    require_annotations: bool
    require_bottom: bool
    force_find_school_boxes: bool = False
    namings: CruiseNamings = CONFIG.cruise_namings
    zarr_keys: ZARRKeys = ZARRKeys()
    name: Optional[str] = None
    year: Optional[int] = None
    # TODO: add the features below one day...
    # mask_bottom: bool
    # bottom_mask_values: float
    # trim_zeros: bool
    # annotation_post_filter_cycles: int = 0 # Open-Close cycles
    # trim_bottom: bool
    # ...

    @validator("path")
    def valid_path(cls, val: Path) -> Path:
        if val.exists():
            if val.is_dir():
                return val
            else:
                raise ValueError(f"{val} is not a directory")
        else:
            raise ValueError(f"{val} doesn't exist")


__all__ = [
    "SchoolBoxesOrigin",
    "PartitionFilterConfig",
    "FilterConfig",
    "CruiseConfig",
    "DatasetConfig",
    "CRUISE_TABLE_COLUMNS",
    "FILTER2TABLE_MAP",
    "PSEUDO_CRUISE_NAMING",
]
