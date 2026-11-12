import pytest

from decorators import cached


def test_cached_ttl_hit_and_expiration() -> None:
    now = [100.0]
    computations = 0

    @cached(ttl=2.0, time_fn=lambda: now[0])
    def double(value: int) -> int:
        nonlocal computations
        computations += 1
        return value * 2

    assert double(10) == 20
    assert double(10) == 20
    assert computations == 1
    now[0] += 2.0
    assert double(10) == 20
    assert computations == 2


def test_cached_invalidate_by_predicate_and_clear() -> None:
    calls = 0

    @cached()
    def find_user(*, user_id: int) -> str:
        nonlocal calls
        calls += 1
        return f"user-{user_id}"

    assert find_user(user_id=42) == "user-42"
    assert find_user(user_id=7) == "user-7"
    removed = find_user.cache_invalidate(
        lambda args, kwargs: kwargs.get("user_id") == 42
    )
    assert removed == 1
    assert find_user(user_id=42) == "user-42"
    assert calls == 3
    find_user.cache_clear()
    assert find_user(user_id=7) == "user-7"
    assert calls == 4


def test_cached_normalizes_keyword_order_and_preserves_metadata() -> None:
    calls = 0

    @cached()
    def combine(*, left: int, right: int) -> int:
        """Combine two values."""
        nonlocal calls
        calls += 1
        return left + right

    assert combine(left=2, right=3) == 5
    assert combine(right=3, left=2) == 5
    assert calls == 1
    assert combine.__name__ == "combine"
    assert combine.__doc__ == "Combine two values."
    assert combine.__wrapped__(left=4, right=5) == 9


def test_cached_requires_hashable_arguments() -> None:
    @cached()
    def count_items(items: list[int]) -> int:
        return len(items)

    with pytest.raises(TypeError):
        count_items([1, 2])
