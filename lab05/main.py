"""Demonstration of lazy transaction streams and itertools."""

from itertools import accumulate

from core import first_balances, first_sliding_sums, positive_transactions
from streams import (
    drop,
    fib_stream,
    moving_average,
    naturals,
    sliding_window,
    take,
)


def main() -> None:
    transactions = [-12.0, 100.0, 45.5, 0.0, -8.0, 25.0, 60.0, 10.0]
    print("=== Ліниві потоки: фінансові транзакції, варіант 6 ===")
    print(f"Перші 10 чисел Fibonacci: {take(10, fib_stream())}")
    print(f"Перші 5 натуральних чисел від 1: {take(5, naturals())}")
    print(f"Додатні транзакції: {take(20, positive_transactions(transactions))}")
    print(f"Накопичувальний баланс: {first_balances(transactions, 20)}")
    print(f"Перші 3 ковзні суми (вікно 3): {first_sliding_sums(transactions, 3, 3)}")
    print(f"Ковзне середнє: {take(4, moving_average([100, 45.5, 25, 60], 2))}")
    print(f"Префіксні добутки: {list(accumulate([1, 2, 3, 4], lambda a, b: a * b))}")
    fib_windows = sliding_window(drop(2, fib_stream()), 3)
    print(f"Перші два вікна Fibonacci: {take(2, fib_windows)}")


if __name__ == "__main__":
    main()
