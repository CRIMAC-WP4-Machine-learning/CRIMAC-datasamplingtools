from ..core import ICruise

from typing import Union, Sequence


def validate_window_size(window_size: Union[int, Sequence[int]]) -> None:
    try:
        assert isinstance(window_size, int) or (
            len(window_size) == 2 and all([isinstance(val, int) for val in window_size])
        )
    except AssertionError:
        raise Exception(
            "Integers or a sequence of two integers must be passed for `window_size` argument."
        )


def count_grid_cells(
    domain_height: int, domain_width: int, grid_height: int, grid_width: int
) -> tuple[int, int, int, int]:
    assert isinstance(domain_height, int)
    assert isinstance(domain_width, int)
    assert isinstance(grid_height, int)
    assert isinstance(grid_width, int)
    vertical_num_cells, vertical_padding = count_segments(
        domain_len=domain_height, segment_size=grid_height
    )
    horizontal_num_cells, horizontal_padding = count_segments(
        domain_len=domain_width, segment_size=grid_width
    )
    return (
        vertical_num_cells,
        horizontal_num_cells,
        vertical_padding,
        horizontal_padding,
    )


def count_segments(domain_len: int, segment_size: int) -> tuple[int, int]:
    assert isinstance(domain_len, int)
    assert isinstance(segment_size, int)
    dim_mod = domain_len % segment_size
    padding = (segment_size - dim_mod) % segment_size
    correction = int(bool(padding))
    num_segments = domain_len // segment_size + correction
    return num_segments, padding


def extend_school_box(
    box: tuple[int, int, int, int],
    cruise: ICruise,
    window_width: int,
    window_height: int,
) -> tuple[int, int, int, int]:
    x_min = max(box[0] - window_width // 2, 0)
    y_min = max(box[1] - window_height // 2, 0)
    x_max = min(
        box[2] - window_width // 2,
        cruise.num_pings - window_width // 2,
    )
    y_max = min(
        box[3] - window_height["h"] // 2,
        cruise.num_ranges - window_height["h"] // 2,
    )
    return x_min, y_min, x_max, y_max


__all__ = ["validate_window_size", "count_grid_cells", "extend_school_box"]
