from ..models import CruiseConfig

from pydantic import ValidationError
import pytest

from itertools import product
from pathlib import Path


# =================================== CruiseConfig =================================== #
# Valid parameters
valid_paths = [pytest.data_paths["default"], str(pytest.data_paths["default"])]
require_annotations_flags = [True, False]
require_bottom_flags = [True, False]
valid_names = ["valid_name", "", None, 3242]
valid_years = [100, 0, 20349, "2019", 2019, None]
valid_params = [
    *product(
        valid_paths,
        require_annotations_flags,
        require_bottom_flags,
        valid_names,
        valid_years,
    )
]

# Invalid path parameters
invalid_paths = [
    "sadfa",
    "/fake/path/to/data",
    Path("/another/fake/path"),
    "rel/path/to/fake/place",
    Path("another/fake/rel/path"),
    pytest.data_paths["default"] / "test_trip_labels.parquet.csv",
    str(pytest.data_paths["default"] / "test_trip_labels.parquet.csv"),
]
invalid_paths_params = [
    *product(invalid_paths, require_annotations_flags, require_bottom_flags)
]

# Invalid name and/or year
invalid_names = [{"name": "cruise 1"}, Path("name")]
invalid_years = ["adfasd", "", {"year": 2019}]
invalid_name_year_params = [
    *product(
        valid_paths,
        require_annotations_flags,
        require_bottom_flags,
        invalid_names,
        invalid_years,
    )
]
# =================================== CruiseConfig =================================== #


class TestCruiseConfig:
    @pytest.mark.parametrize(
        "valid_path, require_annotations, require_bottom, valid_name, valid_year",
        valid_params,
    )
    def test_one(
        self, valid_path, require_annotations, require_bottom, valid_name, valid_year
    ) -> None:
        """Normal scenario where everything is correct."""
        _ = CruiseConfig(
            path=valid_path,
            require_annotations=require_annotations,
            require_bottom=require_bottom,
            name=valid_name,
            year=valid_year,
        )

    @pytest.mark.parametrize(
        "invalid_path, require_annotations, require_bottom", invalid_paths_params
    )
    def test_two(self, invalid_path, require_annotations, require_bottom) -> None:
        """Invalid path."""
        with pytest.raises(ValueError):
            _ = CruiseConfig(
                path=invalid_path,
                require_annotations=require_annotations,
                require_bottom=require_bottom,
            )

    @pytest.mark.parametrize(
        "valid_path, require_annotations, require_bottom, name, year",
        invalid_name_year_params,
    )
    def test_three(
        self, valid_path, require_annotations, require_bottom, name, year
    ) -> None:
        """Invalid name and/or year."""
        with pytest.raises(ValidationError):
            _ = CruiseConfig(
                path=valid_path,
                require_annotations=require_annotations,
                require_bottom=require_bottom,
                name=name,
                year=year,
            )


# # =================================== FilterConfig =================================== #
# # Valid parameters
# valid_frequencies = [[1, 2, 3], [0], [-1], [38000, 120000], [1.2, 38000.0]]
# valid_categories = [[1, 2, 3], [0], [-1]]
#
# # =================================== FilterConfig =================================== #
#
#
# class TestFilterConfig:
#     def test_one(self) -> None:
#         pass
