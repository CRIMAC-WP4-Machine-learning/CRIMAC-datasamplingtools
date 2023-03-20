from ..cruise import CruiseConfig

from pydantic import ValidationError
import pytest

from pathlib import Path
import os


# Share test data
base_path = Path(os.path.abspath(__file__)).parent.parent.parent.parent
valid_path = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
valid_path_str = str(base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED")
non_dir_path = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED/SCH72_2019241.png"
non_existing_path = base_path / "data/2019/SCH72_2019300/ACOUSTIC/GRIDDED"
require_annotations = True
require_bottom = True
valid_name = "cruise 1"
valid_name_int = 135
invalid_name = {"name": "cruise 1"}
valid_year = 2019
valid_year_str = str(valid_year)
invalid_year = "twenty nineteen"


class TestCruiseConfig:
    def test_one(self) -> None:
        """Normal scenario where everything is correct."""
        _ = CruiseConfig(
            path=valid_path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            name=valid_name,
            year=valid_year,
        )

    def test_two(self) -> None:
        """Path argument is now a string."""
        cfg = CruiseConfig(
            path=valid_path_str,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
        )
        assert isinstance(cfg.path, Path)

    def test_three(self) -> None:
        """Path points to a file."""
        with pytest.raises(ValueError):
            _ = CruiseConfig(
                path=non_dir_path,
                require_annotations=require_annotations,
                require_bottom=require_bottom,
            )

    def test_four(self) -> None:
        """Non-existing path."""
        with pytest.raises(ValueError):
            _ = CruiseConfig(
                path=non_existing_path,
                require_annotations=require_annotations,
                require_bottom=require_bottom,
            )

    def test_five(self) -> None:
        """Valid non-string name."""
        cfg = CruiseConfig(
            path=valid_path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            name=valid_name_int,
        )
        assert isinstance(cfg.name, str)

    def test_six(self) -> None:
        """Invalid name."""
        with pytest.raises(ValidationError):
            _ = CruiseConfig(
                path=valid_path,
                require_annotations=require_annotations,
                require_bottom=require_bottom,
                name=invalid_name,
            )

    def test_seven(self) -> None:
        """Valid non-int year."""
        cfg = CruiseConfig(
            path=valid_path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            year=valid_year_str,
        )
        assert cfg.year == valid_year

    def test_eight(self) -> None:
        """Invalid year."""
        with pytest.raises(ValidationError):
            _ = CruiseConfig(
                path=valid_path,
                require_annotations=require_annotations,
                require_bottom=require_bottom,
                year=invalid_year,
            )
