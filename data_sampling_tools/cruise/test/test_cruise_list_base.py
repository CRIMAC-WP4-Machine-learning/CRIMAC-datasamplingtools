from ..base import CruiseBase, CruiseListBase

from ...core.core import CruiseConfig

import pytest

from pathlib import Path
import os


@pytest.fixture
def valid_cruise(data_paths: dict[str, Path]) -> CruiseBase:
    """Valid CruiseBase without missing information."""
    cruise_cfg = CruiseConfig(
        **{
            "path": data_paths["default"],
            "require_annotations": True,
            "require_bottom": True,
            "name": "SCH72_2019241",
            "year": 2019,
        }
    )
    return CruiseBase(conf=cruise_cfg)


@pytest.fixture
def pseudo_cruises(valid_cruise: CruiseBase) -> tuple[CruiseBase, CruiseBase]:
    """
    A tuple of two pseudo-cruises created from different boxes;
    no missing information
    """
    return (
        valid_cruise.from_box(x1=8000, y1=1000, x2=13000, y2=3000, category=24),
        valid_cruise.from_box(x1=9000, y1=1000, x2=13000, y2=2000, category=24),
    )


@pytest.fixture
def valid_cruise_no_annotation(data_paths: dict[str, Path]) -> CruiseBase:
    """Valid CruiseBase without annotation and year."""
    cruise_cfg = CruiseConfig(
        **{
            "path": data_paths["without_annotation"],
            "require_annotations": False,
            "require_bottom": True,
            "name": "SCH72_2019241",
            "year": None,
        }
    )
    return CruiseBase(conf=cruise_cfg)


@pytest.fixture
def valid_cruise_no_bottom(data_paths: dict[str, Path]) -> CruiseBase:
    """Valid CruiseBase without bottom and name."""
    cruise_cfg = CruiseConfig(
        **{
            "path": data_paths["without_bottom"],
            "require_annotations": True,
            "require_bottom": False,
            "name": None,
            "year": 2019,
        }
    )
    return CruiseBase(conf=cruise_cfg)


@pytest.fixture
def valid_cruise_no_bottom_no_annotation(data_paths: dict[str, Path]) -> CruiseBase:
    """Valid CruiseBase without missing bottom and annotation."""
    cruise_cfg = CruiseConfig(
        **{
            "path": data_paths["without_bottom_and_annotation"],
            "require_annotations": False,
            "require_bottom": False,
            "name": "SCH72_2019241",
            "year": 2019,
        }
    )
    return CruiseBase(conf=cruise_cfg)


base_path = Path(os.path.abspath(__file__)).parent.parent.parent.parent
# valid_cruise_path_1 = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
# valid_cruise_config_kwargs_1 = {
#     "path": valid_cruise_path_1,
#     "require_annotations": True,
#     "require_bottom": True,
#     "name": "SCH72_2019241",
#     "year": 2019,
# }
# school_category = 24
# valid_cruise_config_1 = CruiseConfig(**valid_cruise_config_kwargs_1)
# valid_cruise_1 = CruiseBase(conf=valid_cruise_config_1)
# pseudo_cruise_1 = valid_cruise_1.from_box(
#     x1=8000, y1=1000, x2=13000, y2=3000, category=school_category
# )
# pseudo_cruise_2 = valid_cruise_1.from_box(
#     x1=9000, y1=1000, x2=13000, y2=2000, category=school_category
# )

# valid_cruise_path_2 = base_path / "data/2019/SCH72_2019240/ACOUSTIC/GRIDDED"
# valid_cruise_config_kwargs_2 = {
#     "path": valid_cruise_path_2,
#     "require_annotations": True,
#     "require_bottom": True,
#     "name": "SCH72_2019241",
#     "year": 2019,
# }
# valid_cruise_config_2 = CruiseConfig(**valid_cruise_config_kwargs_2)
# valid_cruise_2 = CruiseBase(conf=valid_cruise_config_2)
#
# valid_cruise_path_3 = base_path / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED"
# valid_cruise_config_kwargs_3 = {
#     "path": valid_cruise_path_3,
#     "require_annotations": True,
#     "require_bottom": True,
#     "name": "SCH72_2019241",
#     "year": 2019,
# }
# valid_cruise_config_3 = CruiseConfig(**valid_cruise_config_kwargs_3)
# valid_cruise_3 = CruiseBase(conf=valid_cruise_config_3)

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
    def test_one(self, valid_cruise) -> None:
        """Single valid cruise."""
        _ = CruiseListBase(cruises=[valid_cruise])

    def test_two(
        self, valid_cruise: CruiseBase, pseudo_cruises: tuple[CruiseBase, CruiseBase]
    ) -> None:
        """With pseudo-cruises created from box."""
        _ = CruiseListBase(cruises=[valid_cruise, *pseudo_cruises])

    def test_three(self, valid_cruise: CruiseBase) -> None:
        """Two valid cruises but they are the same."""
        cl = CruiseListBase(cruises=[valid_cruise, valid_cruise])
        assert len(cl.table) == 2
        assert len(cl) == 2

    def test_four(
        self,
        no_bottom_cruise: CruiseBase,
        no_annot_cruise: CruiseBase,
        no_bottom_no_annot_cruise: CruiseBase,
    ) -> None:
        """Cruises with missing data."""
        _ = CruiseListBase(
            cruises=[
                no_bottom_cruise,
                no_annot_cruise,
                no_bottom_no_annot_cruise,
            ]
        )

    def test_five(
        self, valid_cruise: CruiseBase, pseudo_cruises: tuple[CruiseBase, CruiseBase]
    ) -> None:
        """Multiple cruises including cruises with missing data."""
        _ = CruiseListBase(
            cruises=[
                valid_cruise,
                *pseudo_cruises,
                no_bottom_cruise,
                no_annot_cruise,
                no_bottom_no_annot_cruise,
            ]
        )
