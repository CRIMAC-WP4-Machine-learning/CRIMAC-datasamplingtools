from ...utils.cruise import CruiseConfig
from ..base import CruiseBase

import pytest

from pathlib import Path
import os


# Shared test data
# Normal cruise with bottom and annotation
base_path = Path(os.path.abspath(__file__)).parent.parent.parent.parent
valid_cruise_path = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs = {
    "path": valid_cruise_path,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
valid_cruise_config = CruiseConfig(**valid_cruise_config_kwargs)
first_school_box = [0, 1826, 12164, 2471]
school_category = 24
crop_window = (1000, 1000, 3000, 2000)

# Normal cruise but without annotation
no_annot_cruise_path = (
    base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED_WITHOUT_ANNOTATION"
)
no_annot_cruise_config_kwargs = {
    "path": no_annot_cruise_path,
    "require_annotations": False,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
no_annot_cruise_config = CruiseConfig(**no_annot_cruise_config_kwargs)

# Normal cruise but without bottom
no_bottom_cruise_path = (
    base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED_WITHOUT_BOTTOM"
)
no_bottom_cruise_config_kwargs = {
    "path": no_bottom_cruise_path,
    "require_annotations": True,
    "require_bottom": False,
    "name": "SCH72_2019241",
    "year": 2019,
}
no_bottom_cruise_config = CruiseConfig(**no_bottom_cruise_config_kwargs)

# Normal cruise but without bottom and annotation
no_bottom_no_annot_cruise_path = (
    base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED_WITHOUT_BOTTOM_AND_ANNOTATION"
)
no_bottom_no_annot_cruise_config_kwargs = {
    "path": no_bottom_no_annot_cruise_path,
    "require_annotations": False,
    "require_bottom": False,
    "name": "SCH72_2019241",
    "year": 2019,
}
no_bottom_no_annot_cruise_config = CruiseConfig(
    **no_bottom_no_annot_cruise_config_kwargs
)


class TestCruiseBase:
    def test_one(self) -> None:
        """Normal scenario with valid inputs."""
        _ = CruiseBase(conf=valid_cruise_config)

    def test_two(self) -> None:
        """Instantiate from path."""
        _ = CruiseBase.from_path(valid_cruise_path)

    def test_three(self) -> None:
        """Instantiate from box."""
        cruise = CruiseBase(conf=valid_cruise_config)
        _ = cruise.from_box(x1=50, y1=0, x2=1000, y2=550)

    def test_four(self) -> None:
        """Instantiate from box and check for correct school boxes crop."""
        cruise = CruiseBase(conf=valid_cruise_config)
        new_cruise = cruise.from_box(
            x1=0, y1=1000, x2=13000, y2=3000, category=school_category
        )
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        target_school_box = (0, 826, 12164, 1471)
        assert new_school_box == target_school_box

    def test_five(self) -> None:
        """
        Instantiate from box and check for correct school boxes crop.
        X1 cuts the school box.
        """
        cruise = CruiseBase(conf=valid_cruise_config)
        new_cruise = cruise.from_box(
            x1=9000, y1=1000, x2=13000, y2=3000, category=school_category
        )
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        target_school_box = (0, 826, 3164, 1471)
        assert new_school_box == target_school_box

    def test_six(self) -> None:
        """
        Instantiate from box and check for correct school boxes crop.
        Y1 cuts the school box.
        """
        cruise = CruiseBase(conf=valid_cruise_config)
        new_cruise = cruise.from_box(
            x1=8000, y1=2000, x2=13000, y2=3000, category=school_category
        )
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        target_school_box = (0, 0, 4164, 471)
        assert new_school_box == target_school_box

    def test_seven(self) -> None:
        """
        Instantiate from box and check for correct school boxes crop.
        X2 cuts the school box.
        """
        cruise = CruiseBase(conf=valid_cruise_config)
        new_cruise = cruise.from_box(
            x1=8000, y1=1000, x2=10000, y2=3000, category=school_category
        )
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        target_school_box = (0, 826, 2000, 1471)
        assert new_school_box == target_school_box

    def test_eight(self) -> None:
        """
        Instantiate from box and check for correct school boxes crop.
        Y2 cuts the school box.
        """
        cruise = CruiseBase(conf=valid_cruise_config)
        new_cruise = cruise.from_box(
            x1=8000, y1=1000, x2=13000, y2=2000, category=school_category
        )
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        target_school_box = (0, 826, 4164, 1000)
        assert new_school_box == target_school_box

    def test_nine(self) -> None:
        """
        Instantiate from box and check for correct school boxes crop.
        Box is smaller than the school box.
        """
        cruise = CruiseBase(conf=valid_cruise_config)
        new_cruise = cruise.from_box(
            x1=9000, y1=2000, x2=12000, y2=2200, category=school_category
        )
        new_school_boxes = new_cruise.school_boxes[school_category]
        assert len(new_school_boxes) == 1
        new_school_box = new_school_boxes[0]
        target_school_box = (0, 0, 3000, 200)
        assert new_school_box == target_school_box

    def test_ten(self) -> None:
        """Verify crop returns correctly sized data."""
        len_pings = crop_window[2] - crop_window[0]
        len_ranges = crop_window[3] - crop_window[1]
        cruise = CruiseBase(conf=valid_cruise_config)
        cropped = cruise.crop(*crop_window)
        for _, v in cropped.items():
            assert v.dims["ping_time"] == len_pings
            assert v.dims["range"] == len_ranges

    def test_eleven(self) -> None:
        """Cruise without annotation."""
        _ = CruiseBase(conf=no_annot_cruise_config)

    def test_twelve(self) -> None:
        """Cruise without bottom."""
        _ = CruiseBase(conf=no_bottom_cruise_config)

    def test_thirteen(self) -> None:
        """Cruise with neither bottom nor annotation."""
        _ = CruiseBase(conf=no_bottom_no_annot_cruise_config)

    def test_fourteen(self) -> None:
        """Cruise without annotation, but it is required."""
        custom_config_kwargs = dict(no_annot_cruise_config)
        custom_config_kwargs["require_annotations"] = True
        custom_config = CruiseConfig(**custom_config_kwargs)
        with pytest.raises(FileNotFoundError):
            _ = CruiseBase(conf=custom_config)

    def test_fifteen(self) -> None:
        """Cruise without bottom, but it is required."""
        custom_config_kwargs = dict(no_bottom_cruise_config)
        custom_config_kwargs["require_bottom"] = True
        custom_config = CruiseConfig(**custom_config_kwargs)
        with pytest.raises(FileNotFoundError):
            _ = CruiseBase(conf=custom_config)
