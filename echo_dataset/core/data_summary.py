from .cruise import Cruise

import datatable as dt

import os
import re


__all__ = ["DataSummary", "Filter"]


class Filter:
    def __init__(self) -> None:
        raise NotImplementedError


class DataSummary:
    _data_pattern_map = {
        "zarr": re.compile(".*(\.zarr)$"),
    }
    _year_pattern = re.compile("[1,2][0-9]{3}")
    _index_col_names = ["id", "data_path", "frequencies"]
    _index_col_types = [dt.Type.int16, dt.Type.str32, dt.Type.obj64]

    def __init__(self, data_root: str, data_format: str) -> None:
        assert (os.path.isdir(data_root))
        self.data_root = data_root
        try:
            self._data_pattern = self._data_pattern_map[data_format]
        except KeyError:
            raise KeyError(
                f"Not supported data format '{data_format}`. "
                f"Supported formats {self._data_pattern_map.keys()}"
            )
        self._index = dt.Frame(
            self._scan(),
            names=self._index_col_names,
            types=self._index_col_types
        )

    @property
    def index(self) -> dt.Frame:
        return self._index

    def _scan_for_data(self) -> list[str, ...]:
        paths = list()
        for root, dirs, files in os.walk(self.data_root, followlinks=True):
            for d in dirs:
                if self._data_pattern.match(d):
                    paths.append(root)
                    break
        return paths

    def _scan(self) -> tuple[list[any, ...], ...]:
        paths = self._scan_for_data()
        ids = [*range(len(paths))]
        frequencies = list()
        for p in paths:
            cruise = Cruise.from_path(p)
            frequencies.append(cruise.frequencies)
        return ids, paths, frequencies

    def add_summary_row(self, item_id: int, **kwargs: dict[str, any]) -> None:
        raise NotImplementedError

    def filter(self) -> dt.Frame:
        for f in self._filters:
            f.apply(self._index)
