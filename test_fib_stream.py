from streams import drop, fib_stream, take


def test_first_ten_fibonacci_values() -> None:
    assert take(10, fib_stream()) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_drop_then_take_fibonacci_values() -> None:
    assert take(8, drop(5, fib_stream())) == [5, 8, 13, 21, 34, 55, 89, 144]
