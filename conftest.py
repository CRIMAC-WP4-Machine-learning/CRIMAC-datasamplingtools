import pytest

from pathlib import Path


def pytest_addoption(parser):
    parser.addoption(
        "--resources_root",
        action="append",
        help="path to the test resources",
        required=True,
    )


def pytest_sessionstart(session):
    pytest.resources_root = Path(session.config.getoption("resources_root")[0])
    base_path = pytest.resources_root / "data/test_trip/ACOUSTIC"
    pytest.data_paths = {
        "default": base_path / "GRIDDED",
        "without_annotation": base_path / "GRIDDED_WITHOUT_ANNOTATION",
        "without_bottom": base_path / "GRIDDED_WITHOUT_BOTTOM",
        "without_bottom_and_annotation": base_path
        / "GRIDDED_WITHOUT_BOTTOM_AND_ANNOTATION",
    }
