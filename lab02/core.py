from __future__ import annotations

from functools import reduce
from itertools import islice
from typing import Any, Callable, Iterable, Iterator, TypedDict, cast


class Book(TypedDict, total=False):
    """Вхідний запис книги та її оброблене представлення."""

    id: int
    title: str
    genre: str
    ratings: list[float]
    average_rating: float
    adjusted_rating: float


class Stats(TypedDict):
    count: int
    rating_sum: float
    avg_rating: float


Transform = Callable[[Any], Any]


def compose(*functions: Transform) -> Transform:
    """Композиція: compose(f, g)(x) == f(g(x))."""

    def composed(value: Any) -> Any:
        for function in reversed(functions):
            value = function(value)
        return value

    return composed


def pipe(value: Any, *functions: Transform) -> Any:
    """Послідовно передає значення функціям зліва направо."""
    return reduce(lambda current, function: function(current), functions, value)


def juxt(*functions: Callable[[Any], Any]) -> Callable[[Any], tuple[Any, ...]]:
    """Застосовує кілька функцій до одного значення."""
    return lambda value: tuple(function(value) for function in functions)


def normalize_titles() -> Callable[[Iterable[Book]], Iterator[Book]]:
    """Повертає копії записів з назвами у форматі Title Case."""
    return lambda books: (
        cast(
            Book,
            {**book, "title": str(book.get("title", "")).strip().title()},
        )
        for book in books
    )


def with_average_rating() -> Callable[[Iterable[Book]], Iterator[Book]]:
    """Додає середню оцінку до нового запису книги."""

    def add_average(books: Iterable[Book]) -> Iterator[Book]:
        for book in books:
            ratings = cast(list[float], book.get("ratings") or [])
            average = sum(ratings) / len(ratings) if ratings else 0.0
            yield cast(Book, {**book, "average_rating": round(average, 2)})

    return add_average


def boost_genre(
    genre: str, factor: float
) -> Callable[[Iterable[Book]], Iterator[Book]]:
    """Застосовує множник до рейтингу книг вибраного жанру."""
    if factor < 0:
        raise ValueError("factor має бути невід'ємним")

    def apply(books: Iterable[Book]) -> Iterator[Book]:
        for book in books:
            rating = float(book.get("average_rating", 0.0))
            adjusted = rating * factor if book.get("genre") == genre else rating
            yield cast(Book, {**book, "adjusted_rating": round(adjusted, 2)})

    return apply


def filter_min_rating(
    minimum: float,
) -> Callable[[Iterable[Book]], Iterator[Book]]:
    """Відбирає книги з adjusted_rating не нижче за мінімум."""
    return lambda books: (
        book
        for book in books
        if float(book.get("adjusted_rating", 0.0)) >= minimum
    )


def sort_by_rating_desc() -> Callable[[Iterable[Book]], list[Book]]:
    """Сортує за рейтингом спадно, а при рівності — за id зростанням."""
    return lambda books: sorted(
        books,
        key=lambda book: (
            -float(book.get("adjusted_rating", 0.0)),
            int(book.get("id", 0)),
        ),
    )


def take(top_n: int) -> Callable[[Iterable[Book]], list[Book]]:
    """Повертає перші top_n книг."""
    if top_n < 0:
        raise ValueError("top_n має бути невід'ємним")
    return lambda books: list(islice(books, top_n))


def reduce_stats(books: Iterable[Book]) -> Stats:
    """Обчислює кількість, суму та середній рейтинг через reduce."""
    count, total = reduce(
        lambda accumulator, book: (
            accumulator[0] + 1,
            accumulator[1] + float(book.get("adjusted_rating", 0.0)),
        ),
        books,
        (0, 0.0),
    )
    return {
        "count": count,
        "rating_sum": round(total, 2),
        "avg_rating": round(total / count, 2) if count else 0.0,
    }


def build_pipeline(
    top_n: int = 3,
    genre: str = "Fantasy",
    factor: float = 1.1,
    min_rating: float = 3.5,
) -> Callable[[Iterable[Book]], list[Book]]:
    """Будує конвеєр від нормалізації назв до формування Top-N."""
    return cast(
        Callable[[Iterable[Book]], list[Book]],
        compose(
            take(top_n),
            sort_by_rating_desc(),
            filter_min_rating(min_rating),
            boost_genre(genre, factor),
            with_average_rating(),
            normalize_titles(),
        ),
    )


def analyze_books(
    books: Iterable[Book],
    genre: str = "Fantasy",
    factor: float = 1.1,
    min_rating: float = 3.5,
) -> tuple[list[Book], Stats]:
    """Повертає рейтинг усіх допущених книг і reduce-статистику."""
    ranked = cast(
        list[Book],
        compose(
            sort_by_rating_desc(),
            filter_min_rating(min_rating),
            boost_genre(genre, factor),
            with_average_rating(),
            normalize_titles(),
        )(books),
    )
    return ranked, reduce_stats(ranked)

