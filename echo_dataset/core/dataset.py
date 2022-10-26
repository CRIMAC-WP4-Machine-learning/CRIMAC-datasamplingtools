from .sampler import ISampler
from .cruise import ICruise

import datatable as dt

from typing import Sequence, Optional
from collections import defaultdict


class IEchoDataset:
    @property
    def summary(self) -> dt.Frame:
        raise NotImplementedError

    @property
    def num_cruises(self) -> int:
        raise NotImplementedError


class EchoDataset(IEchoDataset):
    def __init__(
            self,
            cruises: Sequence[ICruise],
            sampler: ISampler,
            pseudo_length: int = 1,
            names: Optional[Sequence[str]] = None,
            years: Optional[Sequence[int]] = None,
            categories: Optional[Sequence[int]] = None,
            frequencies: Optional[Sequence[int]] = None,
            with_annotations_only: bool = False,
            with_bottom_only: bool = False
    ) -> None:
        super().__init__()
        self._cruises = cruises
        self._sampler = sampler
        self._pseudo_length = pseudo_length
        self._filter_conf = {
            "names": names,
            "years": years,
            "categories": categories,
            "frequencies": frequencies,
            "with_annotation_only": with_annotations_only,
            "with_bottom_only": with_bottom_only
        }
        self._table = dt.Frame(
            {
                "id": [*range(len(cruises))],
                "path": [str(c.path) for c in cruises]
            }
        )
        self._summary = self._summarise(cruises)

    def __len__(self) -> int:
        return self._pseudo_length

    def __getitem__(self, index: int) -> dict[str, any]:
        return self._sampler(self, index)

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

    def filter_table(self) -> dt.Frame:
        filters = list()
        for key, val in self._filter_conf.items():
            pass

        raise NotImplementedError

    @property
    def table(self) -> dt.Frame:
        return self._table

    @property
    def summary(self) -> dt.Frame:
        return self._summary

    @property
    def num_cruises(self) -> int:
        return len(self._cruises)
