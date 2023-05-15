from typing import Union


def box_contains(
    domain_box: tuple[int, int, int, int], other_box: tuple[int, int, int, int]
) -> Union[tuple[int, int, int, int], tuple[()]]:
    x_min = max(domain_box[0], other_box[0])
    y_min = max(domain_box[1], other_box[1])
    x_max = min(domain_box[2], other_box[2])
    y_max = min(domain_box[3], other_box[3])
    if x_min < x_max and y_min < y_max:
        return tuple([x_min, y_min, x_max, y_max])
    return tuple()


__all__ = ["box_contains"]
