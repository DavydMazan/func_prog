import pytest

from decorators import retries


def test_retries_success_after_failures_without_real_sleep() -> None:
    attempts = 0
    waits: list[float] = []
    logs: list[str] = []

    @retries(
        attempts=3,
        exceptions=(OSError,),
        delay=0.1,
        backoff=2.0,
        jitter=0.2,
        sleep=waits.append,
        random_fn=lambda: 0.5,
        logger=logs.append,
    )
    def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise OSError("temporary")
        return "ok"

    assert flaky() == "ok"
    assert attempts == 3
    assert waits == pytest.approx([0.2, 0.3])
    assert len(logs) == 2


def test_retries_reraises_last_exception_after_limit() -> None:
    waits: list[float] = []

    @retries(attempts=2, exceptions=(OSError,), sleep=waits.append)
    def unavailable() -> None:
        raise OSError("offline")

    with pytest.raises(OSError, match="offline"):
        unavailable()
    assert waits == [0.0]


def test_retries_do_not_catch_unlisted_exceptions() -> None:
    @retries(attempts=4, exceptions=(TimeoutError,))
    def invalid() -> None:
        raise ValueError("not retryable")

    with pytest.raises(ValueError, match="not retryable"):
        invalid()


def test_retries_preserves_metadata_and_validates_attempts() -> None:
    @retries(attempts=1)
    def named() -> str:
        """Function documentation."""
        return "done"

    assert named.__name__ == "named"
    assert named.__doc__ == "Function documentation."
    assert named.__wrapped__() == "done"
    with pytest.raises(ValueError):
        retries(attempts=0)
