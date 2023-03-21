from ..core import (
    ICruiseList,
    IStatelessSampler,
    IStatefulSampler,
    IDataset,
    FilterConfig,
)
from ..utils.dataset import eval_dataset_length

from pydantic import BaseModel
import polars as pl
import xarray as xr
import yaml

from typing import Union, Optional
from pathlib import Path


class DatasetConfig(BaseModel):
    filter: FilterConfig

    def __init__(self, cfg: Union[str, Path]) -> None:
        with open(cfg, "r") as f:
            cfg_dict = yaml.load(f, yaml.FullLoader)
        super().__init__(filter=FilterConfig(**cfg_dict.get("filter", None)))


class BaseDataset(IDataset):
    _cruise_list: ICruiseList
    _filtered_cruise_list: ICruiseList
    _sampler: Union[IStatelessSampler, IStatefulSampler]
    _cfg: DatasetConfig
    _pseudo_len: int

    def __init__(
        self,
        cruise_list: ICruiseList,
        sampler: Union[IStatelessSampler, IStatefulSampler],
        cfg: Union[str, Path],
        pseudo_length: Optional[int] = None,
    ) -> None:
        super().__init__()
        self._cruise_list = cruise_list
        self._dataset_len = eval_dataset_length(
            sampler=sampler, pseudo_length=pseudo_length
        )
        self._cfg = DatasetConfig(cfg)
        self._filtered_cruise_list = None
        self._sampler = sampler
        self._sampler.full_init(cruise_list=self._filtered_cruise_list)

    @property
    def table(self) -> pl.DataFrame:
        return self._filtered_cruise_list.table

    @property
    def cruise_list(self) -> ICruiseList:
        return self._filtered_cruise_list

    def __getitem__(self, index: int) -> dict[str, xr.Dataset]:
        raise NotImplementedError

    def __len__(self) -> int:
        return self._dataset_len

    # TODO: make this actually useful
    def __repr__(self) -> str:
        return str(self._summary[self._valid_ids, :])

    # def _filter(self) -> list[int, ...]:
    #     table = self._summary
    #     special_filters = [
    #         "with_annotations_only",
    #         "with_bottom_only",
    #         "categories",
    #         "frequencies",
    #     ]
    #     for key, val in self._filter_conf.items():
    #         if val is None or key in special_filters:
    #             continue
    #         row_filter = [dt.f[key] == v for v in val]
    #         table = table[row_filter, :]
    #     if self._filter_conf["with_annotations_only"]:
    #         table = table[dt.f["annotations_available"] == True, :]
    #     if self._filter_conf["with_bottom_only"]:
    #         table = table[dt.f["bottom_available"] == True, :]
    #     if self._filter_conf["categories"] is not None:
    #         valid_rows = list()
    #         for row_idx in range(table.nrows):
    #             for c in table[row_idx, "categories"]:
    #                 if c in self._filter_conf["categories"]:
    #                     valid_rows.append(row_idx)
    #                     break
    #         table = table[valid_rows, :]
    #     if self._filter_conf["frequencies"] is not None:
    #         valid_rows = list()
    #         for row_idx in range(table.nrows):
    #             next_row = False
    #             for i, f in enumerate(self._filter_conf["frequencies"]):
    #                 if f not in table[row_idx, "frequencies"]:
    #                     next_row = True
    #                     break
    #             if next_row:
    #                 break
    #             valid_rows.append(row_idx)
    #         table = table[valid_rows, :]
    #     return table["id"].to_numpy().flatten().tolist()
