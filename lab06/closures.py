"""Reusable closures for state, logging, and retry statistics."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True, slots=True)
class RetrySnapshot:
    attempts: int
    calls: int
    successes: int
    failures: int


class RetryMetrics(TypedDict):
    record_attempt: Callable[[], None]
    record_call: Callable[[bool], None]
    snapshot: Callable[[], RetrySnapshot]
    reset: Callable[[], None]


def make_counter(start: int = 0) -> Callable[[], int]:
    """Return a stateful counter closure."""
    value = start

    def increment() -> int:
        nonlocal value
        value += 1
        return value

    return increment


def make_logger(
    prefix: str, sink: Callable[[str], None] = print
) -> Callable[[str], None]:
    """Return a logger closure that prefixes messages and injects its sink."""

    def log(message: str) -> None:
        sink(f"[{prefix}] {message}")

    return log


def make_retry_metrics() -> RetryMetrics:
    """Create closure-backed mutable counters for retry attempts and calls."""
    attempts = 0
    calls = 0
    successes = 0
    failures = 0

    def record_attempt() -> None:
        nonlocal attempts
        attempts += 1

    def record_call(success: bool) -> None:
        nonlocal calls, successes, failures
        calls += 1
        if success:
            successes += 1
        else:
            failures += 1

    def snapshot() -> RetrySnapshot:
        return RetrySnapshot(attempts, calls, successes, failures)

    def reset() -> None:
        nonlocal attempts, calls, successes, failures
        attempts = calls = successes = failures = 0

    return {
        "record_attempt": record_attempt,
        "record_call": record_call,
        "snapshot": snapshot,
        "reset": reset,
    }
