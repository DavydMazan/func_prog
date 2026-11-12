from itertools import count

import pytest

from streams import drop, take


def test_take_preserves_stream_position() -> None:
    values = count(1)
    assert take(5, values) == [1, 2, 3, 4, 5]
    assert take(3, values) == [6, 7, 8]


def test_drop_on_infinite_count() -> None:
    assert take(3, drop(10, count(0))) == [10, 11, 12]


def test_zero_and_invalid_sizes() -> None:
    assert take(0, count()) == []
    assert take(3, drop(0, [4, 5, 6])) == [4, 5, 6]
    with pytest.raises(ValueError):
        take(-1, [1])
    with pytest.raises(ValueError):
        drop(-1, [1])
