from __future__ import annotations

from copy import deepcopy

from core import (
    Book,
    analyze_books,
    boost_genre,
    build_pipeline,
    compose,
    filter_min_rating,
    juxt,
    pipe,
    reduce_stats,
)


SAMPLE: list[Book] = [
    {"id": 1, "title": "python basics", "genre": "Programming", "ratings": [4.0, 5.0, 5.0]},
    {"id": 2, "title": "space odyssey", "genre": "Sci-Fi", "ratings": [4.8, 5.0, 4.7]},
    {"id": 3, "title": "fantasy lands", "genre": "Fantasy", "ratings": [4.0, 4.5, 4.0]},
    {"id": 4, "title": "cooking at home", "genre": "Cooking", "ratings": [3.0, 3.5, 4.0]},
    {"id": 5, "title": "epic realms", "genre": "Fantasy", "ratings": [4.2, 4.4, 4.3]},
    {"id": 6, "title": "young readers", "genre": "Fantasy", "ratings": [2.5, 3.0]},
]


def test_pipeline_returns_top_n_sorted_with_id_tiebreaker() -> None:
    result = build_pipeline(top_n=3, genre="Fantasy", factor=1.1)(SAMPLE)
    assert [book["id"] for book in result] == [2, 5, 1]
    assert [book["adjusted_rating"] for book in result] == [4.83, 4.73, 4.67]
    assert all(book["title"] == book["title"].title() for book in result)


def test_pipeline_does_not_mutate_input() -> None:
    original = deepcopy(SAMPLE)
    build_pipeline(top_n=5)(SAMPLE)
    assert SAMPLE == original


def test_reduce_stats_counts_sums_and_averages() -> None:
    books: list[Book] = [
        {"adjusted_rating": 3.0},
        {"adjusted_rating": 4.0},
        {"adjusted_rating": 5.0},
    ]
    assert reduce_stats(books) == {
        "count": 3,
        "rating_sum": 12.0,
        "avg_rating": 4.0,
    }
    assert reduce_stats([]) == {"count": 0, "rating_sum": 0.0, "avg_rating": 0.0}


def test_genre_boost_creates_new_records() -> None:
    source: list[Book] = [
        {"id": 1, "genre": "Fantasy", "average_rating": 4.0}
    ]
    result = list(boost_genre("Fantasy", 1.1)(source))
    assert result == [
        {
            "id": 1,
            "genre": "Fantasy",
            "average_rating": 4.0,
            "adjusted_rating": 4.4,
        }
    ]
    assert source[0]["average_rating"] == 4.0
    assert result[0] is not source[0]


def test_filter_uses_adjusted_rating() -> None:
    books: list[Book] = [
        {"id": 1, "adjusted_rating": 2.99},
        {"id": 2, "adjusted_rating": 3.0},
    ]
    assert [book["id"] for book in filter_min_rating(3.0)(books)] == [2]


def test_compose_pipe_and_juxt() -> None:
    double = lambda value: value * 2
    plus_three = lambda value: value + 3
    assert compose(plus_three, double)(4) == 11
    assert pipe(4, double, plus_three) == 11
    assert juxt(lambda value: value + 1, lambda value: value * 2)(4) == (5, 8)


def test_analyze_returns_only_books_over_minimum_and_expected_stats() -> None:
    ranked, stats = analyze_books(SAMPLE, genre="Fantasy", factor=1.1, min_rating=3.5)
    assert len(ranked) == 5
    assert stats == {"count": 5, "rating_sum": 22.32, "avg_rating": 4.46}
    assert all(book["adjusted_rating"] >= 3.0 for book in ranked)


def test_repeated_pipeline_calls_are_deterministic() -> None:
    processor = build_pipeline(top_n=4, genre="Fantasy", factor=1.1)
    assert processor(SAMPLE) == processor(SAMPLE)

