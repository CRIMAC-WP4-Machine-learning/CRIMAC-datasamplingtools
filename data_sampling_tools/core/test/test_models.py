from ..models import CruiseConfig, FilterConfig, PartitionFilterConfig

from pydantic import ValidationError
import pytest

from itertools import product
from pathlib import Path


# =================================== CruiseConfig =================================== #
# TODO: refine tests; remove redundant cases;
#  focus on corner cases to check custom validation logic of CruiseConfig model
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


# =================================== FilterConfig =================================== #
# Valid parameters
valid_frequencies = [[], [None], None, 120000]
valid_categories = [[], [None], None, 24]
valid_names = [[], [None], None, "name1"]
valid_years = [[], [None], None, 2019]

valid_filter_params = [
    (f, c, n, y, True, True)
    for f, c, n, y in zip(valid_frequencies, valid_categories, valid_names, valid_years)
]
# =================================== FilterConfig =================================== #


# TODO: add filter for invalid values, especially invalid years
class TestFilterConfig:
    def test_one(self) -> None:
        """Totally empty object."""
        _ = FilterConfig()

    @pytest.mark.parametrize(
        "frequencies, categories, names, years, with_annotations_only, with_bottom_only",
        valid_filter_params,
    )
    def test_two(
        self,
        frequencies,
        categories,
        names,
        years,
        with_annotations_only,
        with_bottom_only,
    ) -> None:
        """Various corner cases to that trigger custom validators."""
        _ = FilterConfig(
            frequencies=frequencies,
            categories=categories,
            partition_filters={
                "partition_name": PartitionFilterConfig(
                    names=names,
                    years=years,
                    with_annotations_only=with_annotations_only,
                    with_bottom_only=with_bottom_only,
                )
            },
        )
