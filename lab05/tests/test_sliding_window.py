import pytest

from core import first_sliding_sums
from streams import moving_average, sliding_window


def test_sliding_windows_basic_and_empty_edges() -> None:
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]
    assert list(sliding_window([], 2)) == []
    assert list(sliding_window([1], 2)) == []


def test_window_size_must_be_positive() -> None:
    with pytest.raises(ValueError):
        list(sliding_window([1, 2], 0))
    with pytest.raises(ValueError):
        list(sliding_window([1, 2], -2))
    with pytest.raises(ValueError):
        first_sliding_sums([], 0, 0)


def test_moving_average() -> None:
    assert list(moving_average([10.0, 20.0, 30.0, 40.0], 2)) == [15.0, 25.0, 35.0]
    assert list(moving_average([], 2)) == []
    with pytest.raises(ValueError):
        list(moving_average([1.0], 0))
