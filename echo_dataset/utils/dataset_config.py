from schema import Schema

import typing

__all__ = ["is_valid"]


schema = Schema(
    {
        "filters": {
            "frequencies": lambda x: isinstance(x, list)
            and all(isinstance(v, int) for v in x)
            or x is None,
            "categories": lambda x: isinstance(x, list)
            and all(isinstance(v, int) for v in x)
            or x is None,
            "names": lambda x: (
                isinstance(x, list) and all(isinstance(v, str) for v in x)
            )
            or x is None,
            "years": lambda x: (
                isinstance(x, list) and all(isinstance(v, int) for v in x)
            )
            or x is None,
            "with_annotations_only": bool,
            "with_bottom_only": bool,
        }
    }
)


def is_valid(config: dict[str, any]) -> bool:
    return schema.is_valid(config)
