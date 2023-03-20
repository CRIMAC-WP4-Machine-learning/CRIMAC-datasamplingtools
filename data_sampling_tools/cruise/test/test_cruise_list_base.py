from ..base import CruiseBase

from ...utils.cruise import CruiseConfig

from pathlib import Path
import os


# Shared test data
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
first_school_box = [8233, 1826, 12163, 2471]
school_category = 24
crop_window = (1000, 1000, 3000, 2000)
