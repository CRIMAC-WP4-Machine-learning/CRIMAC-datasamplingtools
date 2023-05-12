from pydantic import BaseModel

from typing import TypeVar, Mapping, Optional


def _merge_dict(x: Mapping, y: Mapping, dst: Optional[Mapping] = None) -> dict[any]:
    if dst is None:
        dst = x.copy()
    for key, val in y.items():
        if isinstance(val, Mapping):
            dst[key] = _merge_dict(x.get(key, {}), val, dst[key])
        else:
            dst[key] = val
    return dst


class CruiseNamings(BaseModel):
    echogram_suffix: str = "sv"
    bottom_suffix: str = "bottom"
    annotation_suffix: str = "labels"
    schools_suffix: str = "labels.parquet.csv"


class ModuleConfig(BaseModel):
    _Self = TypeVar("_Self", bound="ModuleConfig")
    cruise_namings: CruiseNamings

    def merge(self, other: _Self) -> _Self:
        return ModuleConfig(**_merge_dict(self.dict(), other.dict()))


__all__ = ["ModuleConfig", "CruiseNamings"]
