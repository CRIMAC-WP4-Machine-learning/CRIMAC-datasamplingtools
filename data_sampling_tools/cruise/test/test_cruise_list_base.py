from ..base import CruiseBase, CruiseListBase
from ...core import CruiseConfig

import pytest


valid_parameters = [
    # Default
    [pytest.data_paths["default"], True, True, "test-trip", 2017],
    [pytest.data_paths["default"], False, True, "test-trip", 2024],
    [pytest.data_paths["default"], True, False, "test-trip", 2018],
    [pytest.data_paths["default"], False, False, "test-trip", 2019],
    # No annotations
    [pytest.data_paths["without_annotation"], False, True, "test-trip", 2020],
    [pytest.data_paths["without_annotation"], False, False, "test-trip", 2019],
    # No bottom
    [pytest.data_paths["without_bottom"], True, False, "test-trip", 2019],
    [pytest.data_paths["without_bottom"], False, False, "test-trip", 2021],
    # No annotations, no bottom
    [
        pytest.data_paths["without_bottom_and_annotation"],
        False,
        False,
        "test-trip",
        2023,
    ],
]


@pytest.fixture(params=[valid_parameters[0]])
def single_valid_cruise(request) -> CruiseBase:
    path, require_annotations, require_bottom, name, year = request.param
    return CruiseBase(
        conf=CruiseConfig(
            path=path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            name=name,
            year=year,
        )
    )


@pytest.fixture(params=[valid_parameters])
def valid_cruises(request) -> list[CruiseBase, ...]:
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


@pytest.fixture
def pseudo_cruises(single_valid_cruise: CruiseBase) -> tuple[CruiseBase, CruiseBase]:
    return (
        single_valid_cruise.from_box(x1=8000, y1=1000, x2=13000, y2=3000, category=24),
        single_valid_cruise.from_box(x1=9000, y1=1000, x2=13000, y2=2000, category=24),
    )


class TestCruiseListBase:
    def test_one(self, single_valid_cruise: CruiseBase) -> None:
        """Single valid cruise."""
        _ = CruiseListBase(cruises=[single_valid_cruise])

    def test_two(
        self,
        pseudo_cruises: tuple[CruiseBase, CruiseBase],
    ) -> None:
        """Pseudo-cruises created from box."""
        _ = CruiseListBase(cruises=pseudo_cruises)

    def test_three(self, valid_cruises: list[CruiseBase, ...]) -> None:
        """Two valid cruises but they are the same."""
        cl = CruiseListBase(cruises=[valid_cruises[0], valid_cruises[0]])
        assert len(cl.table) == 2
        assert len(cl) == 2

    def test_five(
        self,
        valid_cruises: list[CruiseBase, ...],
        pseudo_cruises: tuple[CruiseBase, CruiseBase],
    ) -> None:
        """Multiple cruises including cruises with missing data."""
        _ = CruiseListBase(cruises=[*valid_cruises, *pseudo_cruises])
