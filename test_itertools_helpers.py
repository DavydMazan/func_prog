from itertools import islice

from streams import cycle_values, dropwhile_values, repeat_value, takewhile_values


def test_takewhile_and_dropwhile_are_lazy_itertools_wrappers() -> None:
    assert list(takewhile_values(lambda value: value < 5, [1, 3, 5, 2])) == [1, 3]
    assert list(dropwhile_values(lambda value: value <= 0, [-2, 0, 4, 5])) == [4, 5]


def test_cycle_and_repeat_can_be_bounded_by_islice() -> None:
    assert list(islice(cycle_values(["A", "B"]), 5)) == ["A", "B", "A", "B", "A"]
    assert list(repeat_value("x", 3)) == ["x", "x", "x"]
