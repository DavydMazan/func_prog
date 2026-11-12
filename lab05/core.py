"""Lazy transaction-stream operations for laboratory variant 6."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from itertools import accumulate, islice

from streams import sliding_window


def positive_transactions(amounts: Iterable[float]) -> Iterator[float]:
    """Lazily select positive transaction amounts."""
    return (amount for amount in amounts if amount > 0)


def running_balance(amounts: Iterable[float]) -> Iterator[float]:
    """Yield the cumulative balance of positive incoming transactions."""
    return accumulate(positive_transactions(amounts))


def first_sliding_sums(
    amounts: Iterable[float], window_size: int, n: int
) -> list[float]:
    """Return the first n sums of overlapping windows of positive amounts."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    if window_size <= 0:
        raise ValueError("window size must be positive")
    windows = sliding_window(positive_transactions(amounts), window_size)
    return list(islice(map(sum, windows), n))


def first_balances(amounts: Iterable[float], n: int) -> list[float]:
    """Materialize only the first n cumulative balance values."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    return list(islice(running_balance(amounts), n))
