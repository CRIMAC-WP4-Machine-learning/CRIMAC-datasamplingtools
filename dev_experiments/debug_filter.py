from data_sampling_tools import dst

import yaml

from pathlib import Path
import os


base_path = Path(os.path.abspath(__file__)).parent.parent
valid_cruise_path_1 = base_path / "data/2019/SCH72_2019241/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs_1 = {
    "path": valid_cruise_path_1,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
school_category = 24
valid_cruise_config_1 = dst.CruiseConfig(**valid_cruise_config_kwargs_1)
valid_cruise_1 = dst.CruiseBase(conf=valid_cruise_config_1)
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
valid_cruise_config_2 = dst.CruiseConfig(**valid_cruise_config_kwargs_2)
valid_cruise_2 = dst.CruiseBase(conf=valid_cruise_config_2)

valid_cruise_path_3 = base_path / "data/2019/SCH72_2019242/ACOUSTIC/GRIDDED"
valid_cruise_config_kwargs_3 = {
    "path": valid_cruise_path_1,
    "require_annotations": True,
    "require_bottom": True,
    "name": "SCH72_2019241",
    "year": 2019,
}
valid_cruise_config_3 = dst.CruiseConfig(**valid_cruise_config_kwargs_3)
valid_cruise_3 = dst.CruiseBase(conf=valid_cruise_config_3)

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
no_annot_cruise_config = dst.CruiseConfig(**no_annot_cruise_config_kwargs)
no_annot_cruise = dst.CruiseBase(conf=no_annot_cruise_config)

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
no_bottom_cruise_config = dst.CruiseConfig(**no_bottom_cruise_config_kwargs)
no_bottom_cruise = dst.CruiseBase(conf=no_bottom_cruise_config)

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
no_bottom_no_annot_cruise_config = dst.CruiseConfig(
    **no_bottom_no_annot_cruise_config_kwargs
)
no_bottom_no_annot_cruise = dst.CruiseBase(conf=no_bottom_no_annot_cruise_config)

all_cruises = [
    valid_cruise_1,
    valid_cruise_2,
    valid_cruise_3,
    pseudo_cruise_1,
    pseudo_cruise_2,
    no_annot_cruise,
    no_bottom_cruise,
    no_bottom_no_annot_cruise,
]

cruise_list = dst.CruiseListBase(cruises=all_cruises)

with open(base_path / "dev_experiments/config.yaml") as f:
    filter_kwargs = yaml.safe_load(f)

filter_conf = dst.FilterConfig()
cruise_list_filtered = cruise_list.from_filter(filter_conf=filter_conf, mode="train")
print(cruise_list)
