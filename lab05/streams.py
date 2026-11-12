"""Lazy stream helpers for finite and infinite iterables."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from itertools import count, cycle, dropwhile, islice, repeat, takewhile
from typing import TypeVar

T = TypeVar("T")


def fib_stream() -> Iterator[int]:
    """Yield Fibonacci values forever, starting with 0 and 1."""
    left, right = 0, 1
    while True:
        yield left
        left, right = right, left + right


def naturals(start: int = 1) -> Iterator[int]:
    """Yield an infinite stream of integers from start onward."""
    yield from count(start)


def take(n: int, iterable: Iterable[T]) -> list[T]:
    """Materialize only the first n values from an iterable."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    return list(islice(iterable, n))


def drop(n: int, iterable: Iterable[T]) -> Iterator[T]:
    """Return an iterator after skipping its first n values."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    iterator = iter(iterable)
    next(islice(iterator, n, n), None)
    return iterator


def sliding_window(iterable: Iterable[T], k: int) -> Iterator[tuple[T, ...]]:
    """Yield overlapping k-element tuples without materializing the source."""
    if k <= 0:
        raise ValueError("window size k must be positive")
    iterator = iter(iterable)
    window: deque[T] = deque(maxlen=k)
    for _ in range(k):
        try:
            window.append(next(iterator))
        except StopIteration:
            return
    yield tuple(window)
    for value in iterator:
        window.append(value)
        yield tuple(window)


def moving_average(iterable: Iterable[float], k: int) -> Iterator[float]:
    """Yield arithmetic means of consecutive windows of size k."""
    for window in sliding_window(iterable, k):
        yield sum(window) / k


def takewhile_values(
    predicate: Callable[[T], bool], iterable: Iterable[T]
) -> Iterator[T]:
    """Yield values until predicate first becomes false."""
    yield from takewhile(predicate, iterable)


def dropwhile_values(
    predicate: Callable[[T], bool], iterable: Iterable[T]
) -> Iterator[T]:
    """Skip values while predicate is true, then yield the rest."""
    yield from dropwhile(predicate, iterable)


def cycle_values(iterable: Iterable[T]) -> Iterator[T]:
    """Repeat a finite pattern lazily using itertools.cycle."""
    yield from cycle(iterable)


def repeat_value(value: T, times: int | None = None) -> Iterator[T]:
    """Yield a value repeatedly, optionally a finite number of times."""
    if times is not None and times < 0:
        raise ValueError("times must be nonnegative or None")
    if times is None:
        yield from repeat(value)
    else:
        yield from repeat(value, times)
