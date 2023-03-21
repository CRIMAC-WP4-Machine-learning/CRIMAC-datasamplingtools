from ..base import CruiseBase, CruiseListBase

from ...utils.cruise import CruiseConfig

from pathlib import Path
import os


# Shared test data
# Normal cruise with bottom and annotation
base_path = Path(os.path.abspath(__file__)).parent.parent.parent.parent
valid_cruise_path_1 = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs_1 = {
    "path": valid_cruise_path_1,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
school_category = 24
valid_cruise_config_1 = CruiseConfig(**valid_cruise_config_kwargs_1)
valid_cruise_1 = CruiseBase(conf=valid_cruise_config_1)
pseudo_cruise_1 = valid_cruise_1.from_box(
    x1=8000, y1=1000, x2=13000, y2=3000, category=school_category
)
pseudo_cruise_2 = valid_cruise_1.from_box(
    x1=9000, y1=1000, x2=13000, y2=2000, category=school_category
)

valid_cruise_path_2 = base_path / "data/2019/SCH72_2019240/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs_2 = {
    "path": valid_cruise_path_2,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
valid_cruise_config_2 = CruiseConfig(**valid_cruise_config_kwargs_2)
valid_cruise_2 = CruiseBase(conf=valid_cruise_config_2)

valid_cruise_path_3 = base_path / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs_3 = {
    "path": valid_cruise_path_1,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
valid_cruise_config_3 = CruiseConfig(**valid_cruise_config_kwargs_3)
valid_cruise_3 = CruiseBase(conf=valid_cruise_config_3)

# Normal cruise but without annotation and without year
no_annot_cruise_path = (
    base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED_WITHOUT_ANNOTATION"
)
no_annot_cruise_config_kwargs = {
    "path": no_annot_cruise_path,
    "require_annotations": False,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": None,
}
no_annot_cruise_config = CruiseConfig(**no_annot_cruise_config_kwargs)
no_annot_cruise = CruiseBase(conf=no_annot_cruise_config)

# Normal cruise but without bottom and without name
no_bottom_cruise_path = (
    base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED_WITHOUT_BOTTOM"
)
no_bottom_cruise_config_kwargs = {
    "path": no_bottom_cruise_path,
    "require_annotations": True,
    "require_bottom": False,
    "name": None,
    "year": 2019,
}
no_bottom_cruise_config = CruiseConfig(**no_bottom_cruise_config_kwargs)
no_bottom_cruise = CruiseBase(conf=no_bottom_cruise_config)

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
no_bottom_no_annot_cruise = CruiseBase(conf=no_bottom_no_annot_cruise_config)


class TestCruiseListBase:
    def test_one(self) -> None:
        """Single valid cruise."""
        _ = CruiseListBase(cruises=[valid_cruise_1])

    def test_two(self) -> None:
        """With pseudo-cruises created from box."""
        _ = CruiseListBase(cruises=[valid_cruise_1, pseudo_cruise_1, pseudo_cruise_2])

    def test_three(self) -> None:
        """Two valid cruises but they are the same."""
        cl = CruiseListBase(cruises=[valid_cruise_1, valid_cruise_1])
        assert len(cl.table) == 2
        assert len(cl) == 2

    def test_four(self) -> None:
        """Three different cruises."""
        _ = CruiseListBase(cruises=[valid_cruise_1, valid_cruise_2, valid_cruise_3])

    def test_five(self) -> None:
        """Multiple cruises including cruises with missing data."""
        _ = CruiseListBase(
            cruises=[
                valid_cruise_1,
                valid_cruise_2,
                valid_cruise_3,
                pseudo_cruise_1,
                pseudo_cruise_2,
                no_bottom_cruise,
                no_annot_cruise,
                no_bottom_no_annot_cruise,
            ]
        )
