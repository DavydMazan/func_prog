"""Recursive and iterative algorithms for laboratory work 4, variant 6."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from functools import lru_cache
from random import choice
from typing import TypeAlias

NestedValue: TypeAlias = int | float | list["NestedValue"] | tuple["NestedValue", ...]
FrozenNested: TypeAlias = int | float | tuple["FrozenNested", ...]
Summary: TypeAlias = tuple[float, int, int]


def quicksort(values: list[int]) -> list[int]:
    """Return a sorted copy using recursive three-way quicksort."""
    if len(values) <= 1:
        return values.copy()
    pivot = choice(values)
    left = [value for value in values if value < pivot]
    middle = [value for value in values if value == pivot]
    right = [value for value in values if value > pivot]
    return quicksort(left) + middle + quicksort(right)


@dataclass(frozen=True, slots=True)
class Node:
    key: int
    left: Node | None = None
    right: Node | None = None


def preorder(tree: Node | None):
    """Yield node keys in root-left-right order."""
    if tree is None:
        return
    yield tree.key
    yield from preorder(tree.left)
    yield from preorder(tree.right)


def inorder(tree: Node | None):
    """Yield node keys in left-root-right order."""
    if tree is None:
        return
    yield from inorder(tree.left)
    yield tree.key
    yield from inorder(tree.right)


def postorder(tree: Node | None):
    """Yield node keys in left-right-root order."""
    if tree is None:
        return
    yield from postorder(tree.left)
    yield from postorder(tree.right)
    yield tree.key


def bfs_level_order(tree: Node | None) -> list[int]:
    """Return breadth-first, level-order traversal using an explicit queue."""
    if tree is None:
        return []
    queue = deque([tree])
    result: list[int] = []
    while queue:
        node = queue.popleft()
        result.append(node.key)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return result


def dfs_preorder_iter(tree: Node | None) -> list[int]:
    """Return root-left-right traversal using an explicit stack."""
    if tree is None:
        return []
    stack = [tree]
    result: list[int] = []
    while stack:
        node = stack.pop()
        result.append(node.key)
        if node.right is not None:
            stack.append(node.right)
        if node.left is not None:
            stack.append(node.left)
    return result


@lru_cache(maxsize=None)
def fib(n: int) -> int:
    """Return Fibonacci(n) recursively, memoizing each nonnegative index."""
    if isinstance(n, bool) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_naive(n: int) -> int:
    """Naive recursive Fibonacci for small demonstration inputs only."""
    if isinstance(n, bool) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_iter(n: int) -> int:
    """Return Fibonacci(n) iteratively, without recursive stack growth."""
    if isinstance(n, bool) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def analyze_nested(value: NestedValue) -> Summary:
    """Recursively return (numeric sum, number count, maximum container depth)."""
    if isinstance(value, bool):
        raise TypeError("boolean values are not accepted as numbers")
    if isinstance(value, (int, float)):
        return float(value), 1, 0
    if isinstance(value, (list, tuple)):
        if not value:
            return 0.0, 0, 1
        summaries = [analyze_nested(item) for item in value]
        return (
            sum(item[0] for item in summaries),
            sum(item[1] for item in summaries),
            1 + max(item[2] for item in summaries),
        )
    raise TypeError(f"unsupported nested value: {type(value).__name__}")


def analyze_nested_iterative(value: NestedValue) -> Summary:
    """Analyze nested numeric sequences with an explicit stack."""
    stack: list[tuple[NestedValue, int]] = [(value, 0)]
    total = 0.0
    count = 0
    max_depth = 0
    while stack:
        current, parent_depth = stack.pop()
        if isinstance(current, bool):
            raise TypeError("boolean values are not accepted as numbers")
        if isinstance(current, (int, float)):
            total += float(current)
            count += 1
        elif isinstance(current, (list, tuple)):
            depth = parent_depth + 1
            max_depth = max(max_depth, depth)
            stack.extend((item, depth) for item in current)
        else:
            raise TypeError(f"unsupported nested value: {type(current).__name__}")
    return total, count, max_depth


def freeze_nested(value: NestedValue) -> FrozenNested:
    """Convert mutable nested lists to hashable tuples without changing input."""
    if isinstance(value, bool):
        raise TypeError("boolean values are not accepted as numbers")
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, (list, tuple)):
        return tuple(freeze_nested(item) for item in value)
    raise TypeError(f"unsupported nested value: {type(value).__name__}")


@lru_cache(maxsize=None)
def _analyze_frozen(value: FrozenNested) -> Summary:
    """Memoized summary for immutable subtrees, including repeated equal ones."""
    if isinstance(value, (int, float)):
        return float(value), 1, 0
    if not value:
        return 0.0, 0, 1
    summaries = [_analyze_frozen(item) for item in value]
    return (
        sum(item[0] for item in summaries),
        sum(item[1] for item in summaries),
        1 + max(item[2] for item in summaries),
    )


def analyze_nested_memoized(value: NestedValue) -> Summary:
    """Freeze an input then analyze it using a cache of immutable subtrees."""
    return _analyze_frozen(freeze_nested(value))


def clear_nested_cache() -> None:
    """Clear cached summaries for immutable subtrees."""
    _analyze_frozen.cache_clear()


def nested_cache_info():
    """Return hit, miss, size, and limit statistics for nested summaries."""
    return _analyze_frozen.cache_info()
