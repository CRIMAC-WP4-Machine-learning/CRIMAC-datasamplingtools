from ..core.cruise import ICruise

import datatable as dt

from typing import Sequence
import math as m


def parse_cruises(
    cruises: Sequence[ICruise]
) -> tuple[
    dt.Frame, int, tuple[float, ...], int, int, tuple[int, ...], tuple[int, ...]
]:
    table_columns = ("name", "year", "category", "frequencies", "full_path")
    table_types = (
        dt.Type.str32,
        dt.Type.int16,
        dt.Type.int8,
        dt.Type.str32,
        dt.Type.str32,
    )
    table = dt.Frame(names=table_columns, types=table_types)
    total_num_pings = 0
    cruise_ping_fractions = list()
    min_range_len = m.inf
    max_range_len = -m.inf
    frequencies = list()
    categories = list()
    for cruise in cruises:
        total_num_pings += cruise.num_pings
        cruise_ping_fractions.append(cruise.num_pings)
        min_range_len = min(min_range_len, cruise.num_ranges)
        max_range_len = max(max_range_len, cruise.num_ranges)
        frequencies.extend(cruise.frequencies)
        categories.extend(cruise.categories)
        for category in cruise.categories:
            row_data = (
                cruise.info["name"],
                cruise.info["year"],
                category,
                ", ".join([str(f) for f in cruise.frequencies]),
                str(cruise.path),
            )
            row = dt.Frame([row_data], names=table_columns, types=table_types)
            table.rbind(row)
    cruise_ping_fractions = [
        *map(lambda x: x / total_num_pings, cruise_ping_fractions)
    ]
    return (
        table,
        total_num_pings,
        tuple(cruise_ping_fractions),
        min_range_len,
        max_range_len,
        tuple(set(frequencies)),
        tuple(set(categories)),
    )

__all__ = ["parse_cruises"]
