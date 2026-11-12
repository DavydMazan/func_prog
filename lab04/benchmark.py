"""Compare recursive, memoized, and iterative algorithms and save JSON results."""

from __future__ import annotations

import json
from pathlib import Path
from timeit import timeit

from algorithms import (
    NestedValue,
    analyze_nested,
    analyze_nested_iterative,
    fib,
    fib_iter,
    fib_naive,
)


def memoized_fibonacci_once(n: int) -> int:
    fib.cache_clear()
    return fib(n)


def main() -> None:
    nested: NestedValue = [tuple(range(80)), [tuple(range(40)), list(range(40))]]
    results: dict[str, object] = {
        "nested": {
            "recursive_seconds_100_runs": timeit(
                lambda: analyze_nested(nested), number=100
            ),
            "iterative_seconds_100_runs": timeit(
                lambda: analyze_nested_iterative(nested), number=100
            ),
        }
    }
    n = 28
    results["fibonacci"] = {
        "n": n,
        "naive_recursive_seconds": timeit(lambda: fib_naive(n), number=1),
        "memoized_recursive_seconds": timeit(
            lambda: memoized_fibonacci_once(n), number=1
        ),
        "iterative_seconds_10000_runs": timeit(lambda: fib_iter(n), number=10_000),
    }
    path = Path(__file__).with_name("benchmark_results.json")
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
