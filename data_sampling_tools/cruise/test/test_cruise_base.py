from ...core import CruiseConfig
from ..base import CruiseBase

import pytest


valid_parameters = [
    # Default
    [pytest.data_paths["default"], True, True, "test-trip", 2019],
    [pytest.data_paths["default"], False, True, "test-trip", 2019],
    [pytest.data_paths["default"], True, False, "test-trip", 2019],
    [pytest.data_paths["default"], False, False, "test-trip", 2019],
    # No annotations
    [pytest.data_paths["without_annotation"], False, True, "test-trip", 2019],
    [pytest.data_paths["without_annotation"], False, False, "test-trip", 2019],
    # No bottom
    [pytest.data_paths["without_bottom"], True, False, "test-trip", 2019],
    [pytest.data_paths["without_bottom"], False, False, "test-trip", 2019],
    # No annotations, no bottom
    [
        pytest.data_paths["without_bottom_and_annotation"],
        False,
        False,
        "test-trip",
        2019,
    ],
]

invalid_parameters = [
    # No annotations
    [pytest.data_paths["without_annotation"], True, True, "test-trip", 2019],
    [pytest.data_paths["without_annotation"], True, False, "test-trip", 2019],
    # No bottom
    [pytest.data_paths["without_bottom"], True, True, "test-trip", 2019],
    [pytest.data_paths["without_bottom"], False, True, "test-trip", 2019],
    # No annotations, no bottom
    [
        pytest.data_paths["without_bottom_and_annotation"],
        True,
        False,
        "test-trip",
        2019,
    ],
    [
        pytest.data_paths["without_bottom_and_annotation"],
        False,
        True,
        "test-trip",
        2019,
    ],
    [
        pytest.data_paths["without_bottom_and_annotation"],
        True,
        True,
        "test-trip",
        2019,
    ],
]

boxes = [
    (9000, 1000, 13000, 3000),
    (8000, 2000, 13000, 3000),
    (8000, 1000, 10000, 3000),
    (8000, 1000, 13000, 2000),
    (9000, 2000, 12000, 2200),
]

crop_parameters = [
    # X1 cuts the school box
    [boxes[0], (0, 826, 3164, 1471), 24],
    # Y1 cuts the school box
    [boxes[1], (0, 0, 4164, 471), 24],
    # X2 cuts the school box
    [boxes[2], (0, 826, 2000, 1471), 24],
    # Y2 cuts the school box
    [boxes[3], (0, 826, 4164, 1000), 24],
    # Box is smaller than the school box
    [boxes[4], (0, 0, 3000, 200), 24],
]


@pytest.fixture(params=valid_parameters)
def valid_cruise_config(request) -> CruiseConfig:
    path, require_annotations, require_bottom, name, year = request.param
    conf = CruiseConfig(
        path=path,
        require_annotations=require_annotations,
        require_bottom=require_bottom,
        name=name,
        year=year,
    )
    return conf


@pytest.fixture(params=invalid_parameters)
def invalid_cruise_config(request) -> CruiseConfig:
    path, require_annotations, require_bottom, name, year = request.param
    conf = CruiseConfig(
        path=path,
        require_annotations=require_annotations,
        require_bottom=require_bottom,
        name=name,
        year=year,
    )
    return conf


@pytest.fixture
def valid_cruise_base() -> CruiseBase:
    # takes the first combination of the valid_parameters list from the outer scope
    path, require_annotations, require_bottom, name, year = valid_parameters[0]
    return CruiseBase(
        conf=CruiseConfig(
            path=path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            name=name,
            year=year,
        )
    )


class TestCruiseBase:
    def test_one(self, valid_cruise_config) -> None:
        """Normal scenario with valid inputs."""
        _ = CruiseBase(conf=valid_cruise_config)

    def test_two(self, invalid_cruise_config) -> None:
        """
        Valid CruiseConfig, but invalid combination of parameters
        to create a new CruiseBase object.
        """
        with pytest.raises(FileNotFoundError):
            _ = CruiseBase(conf=invalid_cruise_config)

    def test_three(self, valid_cruise_config) -> None:
        """Instantiate from box."""
        cruise = CruiseBase(conf=valid_cruise_config)
        _ = cruise.from_box(x1=50, y1=0, x2=1000, y2=550)

    @pytest.mark.parametrize(
        "crop_box, target_school_box, school_category", crop_parameters
    )
    def test_four(
        self,
        valid_cruise_base: CruiseBase,
        crop_box: tuple[int, int, int, int],
        target_school_box: tuple[int, int, int, int],
        school_category: int,
    ) -> None:
        """Instantiate from box and check for correct school box crops."""
        new_cruise = valid_cruise_base.from_box(*crop_box, category=school_category)
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        assert new_school_box == target_school_box

    @pytest.mark.parametrize("box", boxes)
    def test_ten(
        self, valid_cruise_base: CruiseBase, box: tuple[int, int, int, int]
    ) -> None:
        """Verify crop returns correctly sized data."""
        len_pings = box[2] - box[0]
        len_ranges = box[3] - box[1]
        cropped = valid_cruise_base.crop(*box)
        for _, v in cropped.items():
            assert v.dims["ping_time"] == len_pings
            assert v.dims["range"] == len_ranges
