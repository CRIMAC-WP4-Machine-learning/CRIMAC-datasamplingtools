from ..core import ICruise, FilterConfig, CruiseConfig, CRUISE_TABLE_COLUMNS

import polars as pl

from typing import Sequence
import math as m
import re


def filter_cruise_table(
    cruise_table: pl.DataFrame, filter_conf: FilterConfig, partition_name: str
) -> pl.DataFrame:
    # First apply global filters
    for col, val in filter_conf:
        # Skip partition specific filters (applied later)
        if isinstance(val, dict):
            continue
        # Empty list indicates that there is no filter to apply
        if len(val) == 0:
            continue
        predicate = filter_conf.predicates.__getattribute__(col)(val)
        cruise_table = cruise_table.filter(predicate)
    # Apply partition specific filters
    partition_filter_conf = filter_conf.partition_filters[partition_name]
    for col, val in partition_filter_conf:
        if isinstance(val, set) and len(val) == 0:
            continue
        else:
            predicate = partition_filter_conf.predicates.__getattribute__(col)(val)
            cruise_table = cruise_table.filter(predicate)
    return cruise_table


def parse_cruises(
    cruises: Sequence[ICruise],
) -> tuple[
    pl.DataFrame, int, tuple[float, ...], int, int, tuple[int, ...], tuple[int, ...]
]:
    (
        name_col,
        year_col,
        index_col,
        category_col,
        frequencies_col,
        full_path_col,
        cruise_ping_fractions,
        frequencies,
        categories,
        annotations_available,
        bottom_available,
    ) = (list() for _ in range(11))
    total_num_pings = 0
    min_range_len = m.inf
    max_range_len = -m.inf
    for i, cruise in enumerate(cruises):
        total_num_pings += cruise.num_pings
        cruise_ping_fractions.append(cruise.num_pings)
        min_range_len = min(min_range_len, cruise.num_ranges)
        max_range_len = max(max_range_len, cruise.num_ranges)
        frequencies.extend(cruise.frequencies)
        categories.extend(cruise.categories)
        annotations_available.append(cruise.annotations_available)
        bottom_available.append(cruise.bottom_available)
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
            annotations_available,
            bottom_available
        ],
        schema=CRUISE_TABLE_COLUMNS,
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


__all__ = [
    "parse_cruises",
    "generate_data_filename_patterns",
    "filter_cruise_table",
]
