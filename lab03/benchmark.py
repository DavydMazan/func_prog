"""Compare representative mutable and immutable update costs with timeit."""

from __future__ import annotations

from timeit import timeit

from baseline import mutable_booking, mutate_booking
from core import add_service
from main import sample_booking
from model import Service


def main() -> None:
    rounds = 20_000
    service = Service("Паркінг", 400.0)
    before = timeit(lambda: mutate_booking(mutable_booking()), number=rounds)
    after = timeit(lambda: add_service(sample_booking(), service), number=rounds)
    print(f"Операцій на підхід: {rounds}")
    print(f"Mutable baseline: {before:.4f} s")
    print(f"Immutable update: {after:.4f} s")
    print(f"Відношення immutable/mutable: {after / before:.2f}x")


if __name__ == "__main__":
    main()
