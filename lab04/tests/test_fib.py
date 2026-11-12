import pytest

from algorithms import fib, fib_iter, fib_naive


def test_fibonacci_known_values() -> None:
    assert [fib(index) for index in range(10)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert fib_naive(10) == fib(10)


def test_memoized_and_iterative_fibonacci_match() -> None:
    fib.cache_clear()
    for index in range(50):
        assert fib(index) == fib_iter(index)


def test_fibonacci_cache_info_and_clear() -> None:
    fib.cache_clear()
    assert fib(20) == 6765
    assert fib.cache_info().currsize == 21
    assert fib(20) == 6765
    assert fib.cache_info().hits >= 1
    fib.cache_clear()
    assert fib.cache_info().currsize == 0


@pytest.mark.parametrize("function", [fib, fib_naive, fib_iter])
def test_fibonacci_rejects_negative_values(function) -> None:
    with pytest.raises(ValueError):
        function(-1)
