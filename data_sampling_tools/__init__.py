from .module_config import ModuleConfig
import yaml

from pathlib import Path
import os


_self_path = Path(__file__)
_default_config_name = "config.yaml"
_user_config_name = ".data_sampling_tools.yaml"
_default_config_path = _self_path.parent / _default_config_name
_user_config_path = Path(os.getcwd()) / _user_config_name

with open(_default_config_path, "r") as f:
    _default_config = ModuleConfig(**yaml.load(f, yaml.FullLoader))

if os.path.exists(_user_config_path):
    with open(_user_config_path, "r") as f:
        _user_config = ModuleConfig(**yaml.load(f, yaml.FullLoader))
        CONFIG = _default_config.merge(_user_config)
else:
    CONFIG = _default_config

del (
    _self_path,
    _default_config_name,
    _user_config_name,
    _default_config_path,
    _user_config_path,
    _default_config,
    f,
)

try:
    del _user_config
except NameError:
    pass

__all__ = ["CONFIG", "ModuleConfig"]
