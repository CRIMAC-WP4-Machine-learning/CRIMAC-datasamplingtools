from ..core import ICruise, FilterConfig, CruiseConfig

import polars as pl

from typing import Sequence
import math as m
import re


# TODO: filtering logic goes here...
def filter_cruise_table(
    cruise_table: pl.DataFrame, filter_conf: FilterConfig, mode: str
) -> pl.DataFrame:
    mode_filter = filter_conf.mode_filters[mode]
    for col, val in filter_conf:

        pass
    pass


def parse_cruises(
    cruises: Sequence[ICruise],
) -> tuple[
    pl.DataFrame, int, tuple[float, ...], int, int, tuple[int, ...], tuple[int, ...]
]:
    df_schema = {
        "name": pl.Utf8,
        "year": pl.UInt16,
        "index": pl.UInt16,
        "category": pl.UInt16,
        "frequencies": pl.List(pl.UInt32),
        "full_path": pl.Utf8,
    }
    name_col = list()
    year_col = list()
    index_col = list()
    category_col = list()
    frequencies_col = list()
    full_path_col = list()
    total_num_pings = 0
    cruise_ping_fractions = list()
    min_range_len = m.inf
    max_range_len = -m.inf
    frequencies = list()
    categories = list()
    for i, cruise in enumerate(cruises):
        total_num_pings += cruise.num_pings
        cruise_ping_fractions.append(cruise.num_pings)
        min_range_len = min(min_range_len, cruise.num_ranges)
        max_range_len = max(max_range_len, cruise.num_ranges)
        frequencies.extend(cruise.frequencies)
        categories.extend(cruise.categories)
        if cruise.annotations_available:
            for category in cruise.categories:
                name_col.append(cruise.info["name"])
                year_col.append(cruise.info["year"])
                index_col.append(i)
                category_col.append(category)
                frequencies_col.append(cruise.frequencies)
                full_path_col.append(str(cruise.path))
        else:
            name_col.append(cruise.info["name"])
            year_col.append(cruise.info["year"])
            index_col.append(i)
            category_col.append(None)
            frequencies_col.append(cruise.frequencies)
            full_path_col.append(str(cruise.path))
    cruise_ping_fractions = [*map(lambda x: x / total_num_pings, cruise_ping_fractions)]
    df = pl.DataFrame(
        data=[
            name_col,
            year_col,
            index_col,
            category_col,
            frequencies_col,
            full_path_col,
        ],
        schema=df_schema,
    )
    return (
        df,
        total_num_pings,
        tuple(cruise_ping_fractions),
        min_range_len,
        max_range_len,
        tuple(set(frequencies)),
        tuple(set(categories)),
    )


def generate_data_filename_patterns(
    config: CruiseConfig,
) -> dict[str, re.Pattern]:
    out = dict()
    for k, v in config.namings:
        if k.endswith("_suffix"):
            if v.endswith("csv"):
                pattern = rf".*_{v}"
            else:
                pattern = rf".*_{v}(\.zarr)$"
            out[k.split("_")[0]] = re.compile(pattern)
    return out


def box_contains(
    domain_box: tuple[int, int, int, int], other_box: tuple[int, int, int, int]
) -> tuple:
    x_min = max(domain_box[0], other_box[0])
    y_min = max(domain_box[1], other_box[1])
    x_max = min(domain_box[2], other_box[2])
    y_max = min(domain_box[3], other_box[3])
    if x_min < x_max and y_min < y_max:
        return tuple([x_min, y_min, x_max, y_max])
    return tuple()


__all__ = [
    "parse_cruises",
    "generate_data_filename_patterns",
    "box_contains",
    "filter_cruise_table",
]
