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


class PartitionFilterConfig(BaseModel):
    names: list[str, ...] = []
    years: list[int, ...] = []
    with_annotations_only: bool = False
    with_bottom_only: bool = False

    @validator("names", "years", pre=True)
    def convert_inputs(cls, val) -> Union[list[str, ...], list[int, ...], list[()]]:
        if val is None:
            return []
        if isinstance(val, str) or isinstance(val, int):
            return [val]
        if isinstance(val, list):
            if all(v is None for v in val):
                return []
        return val

    @validator("years")
    def valid_years(cls, vals: list[int, ...]) -> None:
        for v in vals:
            if v < 0:
                raise ValueError("Year cannot be negative.")


class FilterConfig(BaseModel):
    frequencies: list[int, ...] = []
    frequencies_predicate: Callable[
        [list[int, ...], str], bool
    ] = lambda f_list, col: pl.col(col).apply(
        lambda x: all(v in x for v in f_list), return_dtype=pl.Boolean
    ).alias("res")
    categories: list[int, ...] = []
    partition_filters: dict[str, PartitionFilterConfig] = {}

    @validator("frequencies", "categories", pre=True)
    def convert_inputs(cls, val) -> Union[list[int, ...], list[()]]:
        if val is None:
            return []
        if isinstance(val, int):
            return [val]
        if isinstance(val, list):
            if all(v is None for v in val):
                return []
        return val


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
]
