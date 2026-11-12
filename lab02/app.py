from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from core import Book, analyze_books, take


def load_books(path: Path) -> list[Book]:
    """Завантажує записи книг з JSON-файлу (I/O-шар)."""
    with path.open(encoding="utf-8") as source:
        data = json.load(source)
    if not isinstance(data, list):
        raise ValueError("JSON має містити список книг")
    return cast(list[Book], data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Функціональний рейтинг книг")
    parser.add_argument("--data", type=Path, default=Path("sample_data.json"))
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--boost-genre", default="Fantasy")
    parser.add_argument("--factor", type=float, default=1.1)
    parser.add_argument("--min-rating", type=float, default=3.5)
    args = parser.parse_args()
    if args.top < 0 or args.factor < 0:
        parser.error("--top і --factor мають бути невід'ємними")

    ranked, stats = analyze_books(
        load_books(args.data),
        genre=args.boost_genre,
        factor=args.factor,
        min_rating=args.min_rating,
    )
    print("=== Рейтинг книг ===")
    for book in take(args.top)(ranked):
        print(
            f"#{book.get('id')} {book.get('title')} | {book.get('genre')} | "
            f"оцінка: {float(book.get('adjusted_rating', 0.0)):.2f}"
        )
    print(
        f"Статистика допущених книг: count={stats['count']}, "
        f"rating_sum={stats['rating_sum']:.2f}, "
        f"avg_rating={stats['avg_rating']:.2f}"
    )


if __name__ == "__main__":
    main()

