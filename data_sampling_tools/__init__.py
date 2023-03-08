from .utils.module_config import module_cfg_is_valid

import yaml

from pathlib import Path
import os


__all__ = ["CONFIG"]


_self_path = Path(__file__)
_default_config_name = "config.yaml"
_default_config_path = _self_path.parent / _default_config_name
_user_config_name = ".echo_dataset.yaml"
_user_config_path = Path(os.getcwd()) / _user_config_name

with open(_default_config_path, "r") as f:
    _default_config = yaml.load(f, yaml.FullLoader)

if os.path.exists(_user_config_path):
    with open(_user_config_path, "r") as f:
        _user_config = yaml.load(f, yaml.FullLoader)
        if module_cfg_is_valid(_user_config):
            CONFIG = {**_default_config, **_user_config}
        else:
            raise ValueError("Invalid user config")
else:
    CONFIG = _default_config

del (
    _self_path,
    _default_config_name,
    _default_config_path,
    _user_config_name,
    _user_config_path,
    _default_config,
    f,
)

try:
    del _user_config
except NameError:
    pass
