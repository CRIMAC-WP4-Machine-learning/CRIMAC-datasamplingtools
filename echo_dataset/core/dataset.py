from .config import DatasetConfig

import datatable as dt


class IEchoDataset:
    @property
    def table(self) -> dt.Frame:
        raise NotImplementedError

    @property
    def years(self) -> list[int, ...]:
        raise NotImplementedError

    @property
    def num_cruises(self) -> int:
        raise NotImplementedError


class EchoDataset(IEchoDataset):
    def __init__(self, cfg: DatasetConfig) -> None:
        super().__init__()
        self.data_root = cfg.data_root
        self.years = cfg.years
        self.surveys = cfg.surveys
        self.selected_frequencies = cfg.frequencies
        self.available_frequencies = self._collect_frequencies()
        self._survey_map = dict()
        raise NotImplementedError

    def __len__(self) -> int:
        return self._pseudo_len

    def __getitem__(self, index: int) -> dict[str, any]:
        raise NotImplementedError

    def filter_table(self) -> dt.Frame:
        raise NotImplementedError
