from ..misc import box_contains

import pytest


input_parameters = [
    # Test when boxes overlap
    [(2, 2, 5, 5), (3, 3, 6, 6), (3, 3, 5, 5)],
    # Test when boxes do not overlap
    [(2, 2, 5, 5), (6, 6, 7, 7), ()],
    # Test when one box is entirely inside the other
    [(2, 2, 6, 6), (3, 3, 4, 4), (3, 3, 4, 4)],
    # Test when boxes share an edge but do not otherwise overlap
    [(2, 2, 5, 5), (5, 5, 7, 7), ()],
    # Test when boxes share a corner but do not otherwise overlap
    [(2, 2, 5, 5), (5, 2, 7, 5), ()],
    # Test when boxes share part of an edge but do not otherwise overlap
    [(2, 2, 5, 5), (5, 3, 7, 4), ()],
    # Test when boxes are identical
    [(2, 2, 5, 5), (2, 2, 5, 5), (2, 2, 5, 5)],
    # Test when boxes overlap but one edge of the overlapping region is shared by the two boxes
    [(2, 2, 5, 5), (3, 3, 5, 5), (3, 3, 5, 5)],
    # Test when one box is a single point inside the other box
    [(2, 2, 5, 5), (3, 3, 3, 3), ()],
    # Test when one box is a single point on the edge of the other box
    [(2, 2, 5, 5), (5, 5, 5, 5), ()],
]


@pytest.mark.parametrize("box, other, expect", input_parameters)
def test_box_contains(
    box: tuple[int, int, int, int],
    other: tuple[int, int, int, int],
    expect: tuple[int, int, int, int],
) -> None:
    assert box_contains(box, other) == expect
