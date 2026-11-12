"""Typed parameterized decorators for timing, retries, caching, and metrics."""

from __future__ import annotations

import random
import threading
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, Literal, ParamSpec, Protocol, TypeVar, cast

from closures import RetryMetrics

P = ParamSpec("P")
R = TypeVar("R")
R_co = TypeVar("R_co", covariant=True)
Unit = Literal["s", "ms", "us"]
CacheKey = tuple[tuple[Any, ...], tuple[tuple[str, Any], ...]]
CachePredicate = Callable[[tuple[Any, ...], dict[str, Any]], bool]


class CachedFunction(Protocol[P, R_co]):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...

    cache_clear: Callable[[], None]
    cache_invalidate: Callable[[CachePredicate], int]


def _silent_logger(_: str) -> None:
    return None


def timed(
    label: str | None = None,
    *,
    unit: Unit = "ms",
    logger: Callable[[str], None] = print,
    clock: Callable[[], float] = time.perf_counter,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Measure a call using an injectable clock and logger."""
    factors: dict[str, float] = {"s": 1.0, "ms": 1_000.0, "us": 1_000_000.0}
    factor = factors[unit]

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        name = label or function.__name__

        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started = clock()
            try:
                return function(*args, **kwargs)
            finally:
                duration = (clock() - started) * factor
                logger(f"[timed] {name} took {duration:.3f} {unit}")

        return wrapper

    return decorate


def retries(
    attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    backoff: float = 1.0,
    jitter: float = 0.0,
    *,
    sleep: Callable[[float], None] = time.sleep,
    logger: Callable[[str], None] = _silent_logger,
    random_fn: Callable[[], float] = random.random,
    on_attempt: Callable[[], None] | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Retry selected exceptions with injectable sleep, randomness, and logging."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if delay < 0 or backoff < 0 or jitter < 0:
        raise ValueError("delay, backoff, and jitter must be nonnegative")

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(1, attempts + 1):
                if on_attempt is not None:
                    on_attempt()
                try:
                    return function(*args, **kwargs)
                except exceptions as error:
                    if attempt == attempts:
                        logger(f"[retries] failed after {attempt} attempts: {error!r}")
                        raise
                    wait = delay * (backoff ** (attempt - 1))
                    if jitter:
                        wait += random_fn() * jitter
                    logger(
                        f"[retries] attempt {attempt} failed: {error!r}; "
                        f"sleeping {wait:.3f}s"
                    )
                    sleep(wait)
            raise RuntimeError("unreachable retry state")

        return wrapper

    return decorate


def retry_statistics(
    metrics: RetryMetrics,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Count completed calls around a retrying operation."""

    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                result = function(*args, **kwargs)
            except BaseException:
                metrics["record_call"](False)
                raise
            metrics["record_call"](True)
            return result

        return wrapper

    return decorate


def _make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> CacheKey:
    key: CacheKey = (args, tuple(sorted(kwargs.items())))
    hash(key)  # Fail clearly if any argument is not hashable.
    return key


def cached(
    *,
    ttl: float | None = None,
    time_fn: Callable[[], float] = time.time,
) -> Callable[[Callable[P, R]], CachedFunction[P, R]]:
    """Cache results with optional TTL and selective/full invalidation."""
    if ttl is not None and ttl < 0:
        raise ValueError("ttl must be nonnegative or None")

    def decorate(function: Callable[P, R]) -> CachedFunction[P, R]:
        cache: dict[CacheKey, tuple[float | None, R]] = {}
        lock = threading.RLock()

        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = _make_key(args, kwargs)
            now = time_fn()
            with lock:
                cached_value = cache.get(key)
                if cached_value is not None:
                    expiry, value = cached_value
                    if expiry is None or now < expiry:
                        return value
                    del cache[key]
            value = function(*args, **kwargs)
            expiry = None if ttl is None else time_fn() + ttl
            with lock:
                cache[key] = (expiry, value)
            return value

        typed_wrapper = cast(CachedFunction[P, R], wrapper)

        def cache_clear() -> None:
            with lock:
                cache.clear()

        def cache_invalidate(predicate: CachePredicate) -> int:
            with lock:
                stale_keys = [key for key in cache if predicate(key[0], dict(key[1]))]
                for key in stale_keys:
                    del cache[key]
                return len(stale_keys)

        typed_wrapper.cache_clear = cache_clear
        typed_wrapper.cache_invalidate = cache_invalidate
        return typed_wrapper

    return decorate
