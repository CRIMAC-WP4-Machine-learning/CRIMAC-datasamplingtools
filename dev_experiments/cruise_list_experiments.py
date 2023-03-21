from data_sampling_tools import dst

from pathlib import Path
import os


base_path = Path(os.path.abspath(__file__)).parent.parent
valid_cruise_path = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs = {
    "path": valid_cruise_path,
    "require_annotations": False,
    "require_bottom": False,
    "name": "SCH72_2019241",
    "year": 2019,
}
valid_cruise_config = dst.CruiseConfig(**valid_cruise_config_kwargs)
first_school_box = [8233, 1826, 12163, 2471]
school_category = 24
crop_window = (1000, 1000, 3000, 2000)
cruise_1 = dst.CruiseBase(conf=valid_cruise_config)
cruise_2 = cruise_1.from_box(
    x1=8000, y1=1000, x2=13000, y2=3000, category=school_category
)
cruise_3 = cruise_1.from_box(
    x1=9000, y1=1000, x2=13000, y2=2000, category=school_category
)
cruise_4 = dst.CruiseBase(
    conf=dst.CruiseConfig(
        path=base_path / "data/2019/SCH72_2019240/ACOUSTIC/GRIDDED",
        require_annotations=False,
        require_bottom=True,
        name="SCH72_2019240",
        year=None,
    )
)
cruise_5 = dst.CruiseBase(
    conf=dst.CruiseConfig(
        path=base_path / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED",
        require_annotations=True,
        require_bottom=True,
        name="SCH72_2019242",
        year=2019,
    )
)

cl = dst.CruiseListBase(cruises=[cruise_1, cruise_2, cruise_3, cruise_4, cruise_5])
print(cl)
