from ...core import FilterConfig, PartitionFilterConfig, CruiseConfig
from ...cruise import CruiseBase, CruiseListBase

import pytest


frequencies = [
    [38000],
]
categories = [
    [],
]
names = [
    [],
]
years = [
    [],
]
annotations_flag = [
    True,
]
bottom_flag = [
    True,
]
result_len = [500]
filter_args = [
    (f, c, n, y, a, b, r)
    for f, c, n, y, a, b, r in zip(
        frequencies, categories, names, years, annotations_flag, bottom_flag, result_len
    )
]

valid_parameters = [
    # Default
    [pytest.data_paths["default"], True, True, "test-trip", 2000],
    [pytest.data_paths["default"], False, True, "test-trip", 20018],
    [pytest.data_paths["default"], True, False, "test-trip1", 2019],
    [pytest.data_paths["default"], False, False, "test-trip2", 2023],
    # No annotations
    [pytest.data_paths["without_annotation"], False, True, "test-trip3", 2030],
    [pytest.data_paths["without_annotation"], False, False, "test-trip4", 2049],
    # No bottom
    [pytest.data_paths["without_bottom"], True, False, "test-trip5", None],
    [pytest.data_paths["without_bottom"], False, False, None, 2021],
    # No annotations, no bottom
    [
        pytest.data_paths["without_bottom_and_annotation"],
        False,
        False,
        "test-trip7",
        2023,
    ],
]


@pytest.fixture(params=[valid_parameters])
def cruises(request) -> list[CruiseBase, ...]:
    result = list()
    for params in request.param:
        path, require_annotations, require_bottom, name, year = params
        cruise_cfg = CruiseConfig(
            path=path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            name=name,
            year=year,
        )
        result.append(CruiseBase(conf=cruise_cfg))
    return result


@pytest.fixture(params=filter_args)
def filter_config(request) -> tuple[FilterConfig, int]:
    """Various corner cases to that trigger custom validators."""
    f, c, n, y, a, b, r = request.param
    config = FilterConfig(
        frequencies=f,
        categories=c,
        partition_filters={
            "partition_name": PartitionFilterConfig(
                names=n,
                years=y,
                with_annotations_only=a,
                with_bottom_only=b,
            )
        },
    )
    return config, r


class TestCruiseListFromFilter:
    def test_one(
        self, cruises: list[CruiseBase, ...], filter_config: tuple[FilterConfig, int]
    ):
        expected = filter_config[1]
        cruise_list = CruiseListBase(cruises=cruises)
        new_cruise_list = cruise_list.from_filter(
            filter_conf=filter_config[0],
            partition_name=next(iter(filter_config[0].partition_filters.keys())),
        )
        assert len(new_cruise_list) == expected
