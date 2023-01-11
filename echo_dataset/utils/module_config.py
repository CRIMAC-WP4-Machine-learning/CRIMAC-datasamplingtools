from schema import Schema, Optional


__all__ = ["is_valid"]


schema = Schema(
    {
        Optional("survey_suffix"): str,
        Optional("bottom_suffix"): str,
        Optional("labels_suffix"): str,
    }
)


def is_valid(config: dict[str, any]) -> bool:
    return schema.is_valid(config)
