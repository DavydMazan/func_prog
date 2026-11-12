from closures import make_retry_metrics
from decorators import retries, retry_statistics


def test_retry_statistics_counts_attempts_and_completed_call() -> None:
    metrics = make_retry_metrics()
    calls = 0

    @retry_statistics(metrics)
    @retries(
        attempts=3,
        exceptions=(OSError,),
        sleep=lambda _: None,
        on_attempt=metrics["record_attempt"],
    )
    def read() -> str:
        """Simulate a read with one transient failure."""
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError("retry")
        return "data"

    assert read() == "data"
    assert read.__name__ == "read"
    assert read.__doc__ == "Simulate a read with one transient failure."
    assert callable(read.__wrapped__)
    snapshot = metrics["snapshot"]()
    assert snapshot.attempts == 2
    assert snapshot.calls == 1
    assert snapshot.successes == 1
    assert snapshot.failures == 0


def test_retry_statistics_records_terminal_failure() -> None:
    metrics = make_retry_metrics()

    @retry_statistics(metrics)
    @retries(attempts=1, exceptions=(OSError,), on_attempt=metrics["record_attempt"])
    def fail() -> None:
        raise OSError("failed")

    try:
        fail()
    except OSError:
        pass
    snapshot = metrics["snapshot"]()
    assert snapshot.attempts == 1
    assert snapshot.calls == 1
    assert snapshot.failures == 1
