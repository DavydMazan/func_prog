import sys

import pytest

from algorithms import (
    analyze_nested,
    analyze_nested_iterative,
    analyze_nested_memoized,
    clear_nested_cache,
    freeze_nested,
    nested_cache_info,
)


def test_nested_summary_and_pure_input() -> None:
    value = [1, (2, [3, 4]), ((2, (3, 4)),), []]
    original = [1, (2, [3, 4]), ((2, (3, 4)),), []]
    assert analyze_nested(value) == (19.0, 7, 4)
    assert value == original


def test_nested_recursive_and_iterative_versions_agree() -> None:
    value = [1, (2, [3, 4]), ((2, (3, 4)),), []]
    assert analyze_nested(value) == analyze_nested_iterative(value)
    assert analyze_nested_memoized(value) == analyze_nested(value)


def test_memoized_summary_reuses_equal_frozen_subtrees() -> None:
    clear_nested_cache()
    value = [(1, (2, 3)), (1, (2, 3))]
    assert analyze_nested_memoized(value) == (12.0, 6, 3)
    assert nested_cache_info().hits > 0


def test_freeze_converts_nested_lists_without_mutation() -> None:
    value = [1, [2, 3]]
    frozen = freeze_nested(value)
    assert frozen == (1, (2, 3))
    assert isinstance(frozen, tuple)
    assert value == [1, [2, 3]]


def test_iterative_version_handles_depth_past_recursion_limit() -> None:
    value = 1
    for _ in range(sys.getrecursionlimit() + 20):
        value = [value]
    assert analyze_nested_iterative(value) == (1.0, 1, sys.getrecursionlimit() + 20)


def test_booleans_are_not_treated_as_numbers() -> None:
    with pytest.raises(TypeError):
        analyze_nested([1, True])
    with pytest.raises(TypeError):
        analyze_nested_iterative([1, True])
