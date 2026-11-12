import pytest

from decorators import timed


def test_timed_uses_injected_clock_and_preserves_metadata() -> None:
    ticks = iter((1.0, 1.012345))
    logs: list[str] = []

    @timed("work", unit="ms", logger=logs.append, clock=lambda: next(ticks))
    def square(value: int) -> int:
        """Return a square for the timing test."""
        return value * value

    assert square(5) == 25
    assert square.__name__ == "square"
    assert square.__doc__ == "Return a square for the timing test."
    assert square.__wrapped__(4) == 16
    assert "work took 12.345 ms" in logs[0]


def test_timed_logs_when_wrapped_function_raises() -> None:
    ticks = iter((0.0, 0.25))
    logs: list[str] = []

    @timed(unit="s", logger=logs.append, clock=lambda: next(ticks))
    def fail() -> None:
        raise RuntimeError("problem")

    with pytest.raises(RuntimeError, match="problem"):
        fail()
    assert "fail took 0.250 s" in logs[0]
