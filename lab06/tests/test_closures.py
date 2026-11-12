from closures import make_counter, make_logger, make_retry_metrics


def test_counter_closure_keeps_mutable_state() -> None:
    counter = make_counter(10)
    assert counter() == 11
    assert counter() == 12


def test_logger_closure_injects_prefix_and_sink() -> None:
    messages: list[str] = []
    logger = make_logger("test", messages.append)
    logger("ready")
    assert messages == ["[test] ready"]


def test_retry_metrics_closure_tracks_attempts_and_calls() -> None:
    metrics = make_retry_metrics()
    metrics["record_attempt"]()
    metrics["record_attempt"]()
    metrics["record_call"](True)
    assert metrics["snapshot"]().attempts == 2
    assert metrics["snapshot"]().successes == 1
    metrics["reset"]()
    assert metrics["snapshot"]().calls == 0
