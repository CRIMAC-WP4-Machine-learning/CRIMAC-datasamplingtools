from data_sampling_tools import dst

from pathlib import Path


base_path = Path("/Users/andrei/WUR/Projects/pelAcoustics/data-sampling-tools")
valid_cruise_path = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs = {
    "path": valid_cruise_path,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
valid_cruise_config = dst.CruiseConfig(**valid_cruise_config_kwargs)
cruise = dst.CruiseBase(conf=valid_cruise_config)
new_cruise = cruise.from_box(x1=8000, y1=2000, x2=10000, y2=2200, category=24, force_find_school_boxes=False)

print(new_cruise)

# cl = dst.CruiseListBase(cruises=[c])
# print(cl)
# [8233, 1826, 12163, 2471] cat 24
