import datatable as dt

from pathlib import Path
from typing import Union
import os
import re


__all__ = [
    "scan_data",
    "get_dataset_table",
    "get_valid_years",
    "generate_data_filename_patterns"
]


_YEAR_PATTERN = re.compile("[1,2][0-9]{3}")
_ZARR_PATTERN = re.compile(".*(\.zarr)$")
_COL_NAMES = ["year", "survey", "full_path"]
_COL_TYPES = [dt.Type.int32, dt.Type.str32, dt.Type.str32]
_DATA_TABLE = dt.Frame(names=_COL_NAMES, types=_COL_TYPES)
_SCANNED = False


def generate_data_filename_patterns(
        config: dict[str, any]
) -> list[re.Pattern, re.Pattern, re.Pattern]:
    out = list()
    keys = ["survey_suffix", "labels_suffix", "bottom_suffix"]
    for k in keys:
        pattern = rf".*_{config[k]}(\.zarr)$"
        out.append(re.compile(pattern))
    return out


def _scan_for_zarr(data_root: Union[Path, str]) -> list[str, ...]:
    paths = list()
    for root, dirs, files in os.walk(data_root, followlinks=True):
        for d in dirs:
            if _ZARR_PATTERN.match(d):
                paths.append(root)
                break
    return paths


def _parse_zarr_path(path_to_zarr: str) -> dict[str, Union[int, str, str]]:
    data = dict().fromkeys(_COL_NAMES, None)
    data[_COL_NAMES[2]] = [path_to_zarr]
    dirs = path_to_zarr.split("/")
    for i, dir_name in enumerate(dirs):
        if _YEAR_PATTERN.fullmatch(dir_name):
            data[_COL_NAMES[0]] = [dir_name]
            data[_COL_NAMES[1]] = [dirs[i + 1]]
            break
    return data


def scan_data(data_root: str) -> None:
    global _SCANNED
    for path in _scan_for_zarr(data_root):
        row = dt.Frame(_parse_zarr_path(path), types=_COL_TYPES)
        _DATA_TABLE.rbind(row)
    _SCANNED = True


def get_dataset_table(copy: bool = True) -> None:
    if copy:
        return _DATA_TABLE.deepcopy()
    else:
        return _DATA_TABLE


def get_valid_years() -> list[int, ...]:
    return _DATA_TABLE[:, _COL_NAMES[0]]


def get_valid_surveys() -> list[str, ...]:
    return _DATA_TABLE[:, _COL_NAMES[1]]


# def scan_years(data_root: str) -> Iterator[Path]:
#     dirs = os.listdir(data_root)
#     for d in dirs:
#         if _YEAR_PATTERN.fullmatch(d):
#             yield Path(os.path.join(data_root, d))
#
#
# def scan_surveys(data_root: str, year: str) -> Iterator[Path]:
#     dirs = os.listdir(os.path.join(data_root, year))
#     for d in dirs:
#         survey_path = Path(os.path.join(data_root, year, d, _INTERMEDIATE_PATH))
#         if os.path.exists(survey_path):
#             yield survey_path
#
#
# def _get_all_survey_paths(data_root: str) -> Sequence[str]:
#     print("Gathering all valid surveys")
#     survey_paths = list()
#     for year in scan_years(data_root):
#         survey_paths.extend(_get_survey_paths_per_year(data_root, year))
#     return survey_paths
#
#
# def _get_survey_paths_per_year(data_root: str, year: str) -> Sequence[str]:
#     if _YEAR_PATTERN.fullmatch(year):
#         return [
#             os.path.join(data_root, s) for s in scan_surveys(data_root, year)
#         ]
#     else:
#         warnings.warn(f"Invalid year: {year}")
#         return list()
#
#
# def get_survey_paths(
#         data_root: str,
#         years: Union[Sequence[str], str]
# ) -> Sequence[str]:
#     if years == "all":
#         print("Gathering all valid surveys")
#         return _get_all_survey_paths(data_root)
#     if not isinstance(years, Sequence):
#         years = list([years])
#     print(f"Gathering valid surveys for the following years: {years}")
#     survey_paths = list()
#     for year in years:
#         survey_paths.extend(_get_survey_paths_per_year(data_root, year))
#     return survey_paths


# if __name__ == "__main__":
#     path = "../../data"
#     table = get_available_datasets(path)
#     print(table)
