from ..module_config import CruiseNamings
from .. import CONFIG

from pydantic import BaseModel, validator

from typing import Optional
from pathlib import Path
from enum import Enum


class SchoolBoxesOrigin(Enum):
    NOT_AVAILABLE = 1
    CSV = 2
    CONTOUR_SEARCH = 3


class PartitionFilterConfig(BaseModel):
    names: Optional[list[str, ...]] = None
    years: Optional[list[int, ...]] = None
    with_annotations_only: Optional[bool] = False
    with_bottom_only: Optional[bool] = False


class FilterConfig(BaseModel):
    frequencies: list[int, ...]
    categories: list[int, ...]
    partition_filters: dict[str, PartitionFilterConfig]


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


__all__ = ["SchoolBoxesOrigin", "PartitionFilterConfig", "FilterConfig", "CruiseConfig"]
