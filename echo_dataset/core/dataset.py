from ..utils.dataset_config import is_valid
from .sampler import ISampler
from .cruise import ICruise

import datatable as dt
import xarray as xr
import yaml

from collections import defaultdict
from typing import Sequence


class IEchoDataset:
    _cruises: list[ICruise, ...]
    _table: dt.Frame
    _summary: dt.Frame
    _ping_range_map: dict[int, int]
    _total_num_pings: int

    @property
    def table(self) -> dt.Frame:
        return self._table

    @property
    def summary(self) -> dt.Frame:
        return self._summary

    @property
    def num_cruises(self) -> int:
        return len(self._cruises)

    @property
    def ping_range_map(self) -> dict[int, int]:
        return self._ping_range_map

    @property
    def total_num_pings(self) -> int:
        return self._total_num_pings

    def schools(
            self,
            cruise_idx: int,
            fish_category: int
    ) -> list[list[int, int, int, int], ...]:
        raise NotImplementedError

    def crop(
            self,
            cruise_idx: int,
            box: list[int, int, int, int]
    ) -> dict[str, xr.Dataset]:
        raise NotImplementedError


class EchoDataset(IEchoDataset):
    def __init__(
        self,
        cruises: Sequence[ICruise],
        sampler: Union[ISampler, ICompoundSampler],
        cfg: str,
        pseudo_length: int = 1,
    ) -> None:
        super().__init__()
        self._cruises = list(cruises)
        self._sampler = sampler
        self._pseudo_length = pseudo_length
        self._cfg = self._load_cfg(cfg)
        self._sampler.init(self._cfg["filters"]["categories"])
        self._filter_conf = {
            "name": self._cfg["filters"]["names"],
            "year": self._cfg["filters"]["years"],
            "categories": list(set(self._cfg["filters"]["categories"])),
            "frequencies": list(set(self._cfg["filters"]["frequencies"])),
            "with_annotations_only": self._cfg["filters"]["with_annotations_only"],
            "with_bottom_only": self._cfg["filters"]["with_bottom_only"]
        }
        self._table = dt.Frame(
            {
                "id": [*range(len(cruises))],
                "path": [str(c.path) for c in cruises]
            }
        )
        self._summary = self._summarise(cruises)
        self._valid_ids = self._filter()
        self._ping_range_map, self._total_num_pings = self._assemble_ping_range_map()

    def __len__(self) -> int:
        return self._pseudo_length

    def __getitem__(self, _: any) -> dict[str, any]:
        return self._sampler(self)

    def __repr__(self) -> str:
        return str(self._summary[self._valid_ids, :])

    @staticmethod
    def _load_cfg(cfg: str) -> dict[str, any]:
        with open(cfg, "r") as f:
            cfg = yaml.load(f, yaml.FullLoader)
        if is_valid(cfg):
            return cfg
        else:
            raise Exception("Invalid dataset config")

    @staticmethod
    def _summarise(cruises: Sequence[ICruise]) -> dt.Frame:
        summary = defaultdict(list)
        for i, c in enumerate(cruises):
            summary["id"].append(i)
            info = c.info
            summary["name"].append(info["name"])
            summary["year"].append(info["year"])
            summary["annotations_available"].append(c.annotations_available)
            summary["bottom_available"].append(c.bottom_available)
            summary["num_pings"].append(c.num_pings)
            summary["categories"].append(c.categories)
            summary["frequencies"].append(c.frequencies)
        return dt.Frame(
            summary,
            types=[int, str, int, bool, bool, int, object, object]
        )

    def _filter(self) -> list[int, ...]:
        table = self._summary
        special_filters = ["with_annotations_only", "with_bottom_only", "categories", "frequencies"]
        for key, val in self._filter_conf.items():
            if val is None or key in special_filters:
                continue
            row_filter = [dt.f[key] == v for v in val]
            table = table[row_filter, :]
        if self._filter_conf["with_annotations_only"]:
            table = table[dt.f["annotations_available"] == True, :]
        if self._filter_conf["with_bottom_only"]:
            table = table[dt.f["bottom_available"] == True, :]
        if self._filter_conf["categories"] is not None:
            valid_rows = list()
            for row_idx in range(table.nrows):
                for c in table[row_idx, "categories"]:
                    if c in self._filter_conf["categories"]:
                        valid_rows.append(row_idx)
                        break
            table = table[valid_rows, :]
        if self._filter_conf["frequencies"] is not None:
            valid_rows = list()
            for row_idx in range(table.nrows):
                next_row = False
                for i, f in enumerate(self._filter_conf["frequencies"]):
                    if f not in table[row_idx, "frequencies"]:
                        next_row = True
                        break
                if next_row:
                    break
                valid_rows.append(row_idx)
            table = table[valid_rows, :]
        return table["id"].to_numpy().flatten().tolist()

    def _assemble_ping_range_map(self) -> tuple[dict[int, int], int]:
        ping_range_map = OrderedDict()
        previous_ping = 0
        for i in self._valid_ids:
            num_pings = previous_ping + self._cruises[i].num_pings
            ping_range_map[num_pings] = self._cruises[i].num_ranges
            previous_ping = num_pings
        return ping_range_map, previous_ping

    def schools(
            self,
            cruise_idx: int,
            fish_category: int
    ) -> list[list[int, int, int, int], ...]:
        return self._cruises[cruise_idx].school_boxes[fish_category]

    def crop(
            self,
            cruise_idx: int,
            box: list[int, int, int, int]
    ) -> dict[str, xr.Dataset]:
        return self._cruises[cruise_idx].crop(*box)
