from schema import Schema, Optional


schema = Schema(
    {
        Optional("survey_suffix"): str,
        Optional("bottom_suffix"): str,
        Optional("labels_suffix"): str,
        Optional("schools_suffix"): str,
    }
)


def module_cfg_is_valid(cfg: dict[str, any]) -> bool:
    return schema.is_valid(cfg)


__all__ = ["module_cfg_is_valid"]
