import random

from algorithms import quicksort


def test_quicksort_boundaries_and_duplicates() -> None:
    assert quicksort([]) == []
    assert quicksort([1]) == [1]
    assert quicksort([3, 2, 1]) == [1, 2, 3]
    assert quicksort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


def test_quicksort_matches_sorted_and_preserves_input() -> None:
    generator = random.Random(42)
    values = [generator.randint(-1000, 1000) for _ in range(1000)]
    original = values.copy()
    assert quicksort(values) == sorted(values)
    assert values == original
