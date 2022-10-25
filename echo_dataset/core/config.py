from .data_summary import DataSummary

from echo_dataset.utils import parse_values

from typing import Union, Sequence
from pathlib import Path


__all__ = ["DatasetConfig"]


class DatasetConfig:
    def __init__(self, data_root: str, **kwargs) -> None:
        self.summary = DataSummary(
            data_root=data_root,
            data_format=kwargs.get("data_format", "zarr")
        )
        self.selected_years = self._parse_years(kwargs.get("years", "all"))
        self.selected_surveys = self._parse_surveys(kwargs.get("surveys", "all"))
        self.frequencies = kwargs.get("frequencies", "all")
        raise NotImplementedError

    @classmethod
    def from_file(cls, path_to_config: Union[str, Path]):
        raise NotImplementedError

    def _parse_years(
            self,
            years: Union[Sequence[str], str],
    ) -> list[str, ...]:
        return parse_values(years, self.summary.valid_years, "years")

    def _parse_surveys(
            self,
            surveys: Union[Sequence[str], str]
    ) -> list[str, ...]:
        return parse_values(surveys, self.summary.valid_surveys, "surveys")

    def _parse_frequencies(
            self,
            frequencies: Union[Sequence[str], str]
    ) -> list[str, ...]:
        pass
