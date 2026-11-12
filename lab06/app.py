"""Demonstrate closure state and decorators with a simulated file operation."""

from closures import make_counter, make_logger, make_retry_metrics
from decorators import cached, retries, retry_statistics, timed


def run_demo() -> None:
    logs: list[str] = []
    sleeps: list[float] = []
    logger = make_logger("file", logs.append)
    metrics = make_retry_metrics()
    call_number = make_counter()
    ticks = iter((10.0, 10.005))

    @timed("simulated_read", unit="ms", logger=logger, clock=lambda: next(ticks))
    @retry_statistics(metrics)
    @retries(
        attempts=3,
        exceptions=(OSError,),
        delay=0.01,
        backoff=2.0,
        sleep=sleeps.append,
        logger=logger,
        on_attempt=metrics["record_attempt"],
    )
    def read_simulated_file(path: str) -> str:
        if call_number() < 3:
            raise OSError("temporary read error")
        return f"contents of {path}"

    content = read_simulated_file("report.txt")

    current_time = [100.0]
    calculations = make_counter()
    calculation_numbers: list[int] = []

    @cached(ttl=5.0, time_fn=lambda: current_time[0])
    def file_size(path: str) -> int:
        calculation_numbers.append(calculations())
        return len(path) * 10

    first_size = file_size("report.txt")
    second_size = file_size("report.txt")
    invalidated = file_size.cache_invalidate(
        lambda args, kwargs: args == ("report.txt",)
    )
    third_size = file_size("report.txt")

    print("=== Замикання та декоратори: варіант 6 ===")
    print(f"Результат операції: {content}")
    print(f"Затримки між повторами: {sleeps}")
    print(f"Статистика повторів: {metrics['snapshot']()}")
    print(f"Кешовані розміри: {first_size}, {second_size}, {third_size}")
    print(f"Видалено з кешу: {invalidated}; " f"обчислень: {len(calculation_numbers)}")
    print("Лог:")
    for entry in logs:
        print(entry)


if __name__ == "__main__":
    run_demo()
