from core import first_sliding_sums
from streams import take


def test_take_requests_only_requested_items() -> None:
    requested: list[int] = []

    def source():
        for value in range(1000):
            requested.append(value)
            yield value

    assert take(3, source()) == [0, 1, 2]
    assert requested == [0, 1, 2]


def test_transaction_window_pipeline_stops_after_requested_windows() -> None:
    requested: list[int] = []

    def source():
        for value in range(1, 1000):
            requested.append(value)
            yield float(value)

    assert first_sliding_sums(source(), window_size=2, n=2) == [3.0, 5.0]
    assert requested == [1, 2, 3]
