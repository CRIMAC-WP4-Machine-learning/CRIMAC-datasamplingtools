from typing import Sequence


__all__ = ["box_is_consistent"]


def box_is_consistent(box: Sequence[int]) -> bool:
    x = (box[2] - box[0]) > 0
    y = (box[3] - box[1]) > 0
    return x and y
