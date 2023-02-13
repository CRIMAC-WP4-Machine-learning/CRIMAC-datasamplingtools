from typing import Union, Sequence


__all__ = ["validate_window_size"]


def validate_window_size(window_size: Union[int, Sequence[int]]) -> None:
    try:
        assert isinstance(window_size, int) or (
            len(window_size) == 2 and all([isinstance(val, int) for val in window_size])
        )
    except AssertionError:
        raise Exception(
            "Integers or a sequence of two integers must be passed for `window_size` argument."
        )
