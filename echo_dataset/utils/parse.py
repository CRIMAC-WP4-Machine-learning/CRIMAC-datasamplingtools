from typing import Sequence, Union


__all__ = ["parse_values"]


def parse_values(
        vals: Union[Sequence[str], str],
        valid_vals: Sequence[str],
        field_name: str = "unnamed"
) -> list[str, ...]:
    if isinstance(vals, str):
        if vals == "all":
            return list(valid_vals)
        else:
            raise ValueError(f"Invalid input for '{field_name}' field")
    elif isinstance(vals, Sequence) and all(isinstance(x, str) for x in vals):
        return list(set(vals) & set(valid_vals))
    else:
        raise ValueError(f"Invalid input for '{field_name}' field")


# def parse_values(
#         vals: Union[Sequence[int], str],
#         valid_vals: Sequence[int],
#         field_name: str = "unnamed"
# ) -> list[int, ...]:
#     pass
