
import pandas as pd
import pytest

from book_recommender.recommender import BookRecommender
from book_recommender.evaluation import generate_evaluation_queries


@pytest.fixture
def fitted_recommender():
    books = pd.DataFrame({
        "book_id": [1, 2, 3, 4, 5],
        "title": [
            "Book A",
            "Book B",
            "Book C",
            "Book D",
            "Book E",
        ],
        "content": [
            "fantasy magic",
            "romance love",
            "science fiction",
            "historical romance",
            "fantasy adventure",
        ],
        "tag_1": [
            "fantasy",
            "romance",
            "science-fiction",
            "historical-fiction",
            "fantasy",
        ],
        "tag_2": [
            "magic",
            "love",
            "dystopian",
            "romance",
            "adventure",
        ],
    })

    return BookRecommender().fit(books)

# Para evaluar generate_evaluation_queries
def test_generate_evaluation_queries_returns_three_groups(
    fitted_recommender,
):
    queries = generate_evaluation_queries(
        fitted_recommender,
        n_queries=2,
    )

    assert set(queries) == {
        "book_queries",
        "tag_queries",
        "combined_queries",
    }

    assert len(queries["book_queries"]) == 2
    assert len(queries["tag_queries"]) == 2
    assert len(queries["combined_queries"]) == 2


def test_generate_evaluation_queries_is_reproducible(
    fitted_recommender,
):
    first = generate_evaluation_queries(
        fitted_recommender,
        n_queries=3,
        random_state=42,
    )

    second = generate_evaluation_queries(
        fitted_recommender,
        n_queries=3,
        random_state=42,
    )

    assert first == second


def test_generate_evaluation_queries_uses_different_books(
    fitted_recommender,
):
    queries = generate_evaluation_queries(
        fitted_recommender,
        n_queries=3,
    )

    book_ids = [
        query["book_ids"][0]
        for query in queries["book_queries"]
    ]

    assert len(book_ids) == len(set(book_ids))


def test_generate_evaluation_queries_requires_fitted_model():
    recommender = BookRecommender()

    with pytest.raises(RuntimeError, match="no está entrenado"):
        generate_evaluation_queries(recommender)


def test_generate_evaluation_queries_requires_positive_number(
    fitted_recommender,
):
    with pytest.raises(ValueError, match="positivo"):
        generate_evaluation_queries(
            fitted_recommender,
            n_queries=0,
        )


def test_generate_evaluation_queries_requires_enough_books(
    fitted_recommender,
):
    with pytest.raises(ValueError, match="suficientes libros"):
        generate_evaluation_queries(
            fitted_recommender,
            n_queries=6,
        )


def test_generate_evaluation_queries_uses_catalog_tags(
    fitted_recommender,
):
    queries = generate_evaluation_queries(
        fitted_recommender,
        n_queries=5,
    )

    catalog_tags = {
        tag
        for column in ["tag_1", "tag_2"]
        for tag in fitted_recommender.books_[column].dropna()
    }

    selected_tags = {
        query["tags"][0]
        for query in queries["tag_queries"]
    }

    assert selected_tags.issubset(catalog_tags)

# Para evaluar evaluate_recommender
def test_evaluate_recommender_returns_metrics(fitted_recommender):
    from book_recommender.evaluation import evaluate_recommender

    results = evaluate_recommender(
        recommender=fitted_recommender,
        n_queries=2,
        n_recommendations=2,
        random_state=42,
    )

    assert set(results.keys()) == {
        "book_queries",
        "tag_queries",
        "combined_queries",
    }

    for group in results.values():
        assert group["queries_requested"] == 2
        assert group["queries_succeeded"] == 2
        assert group["queries_failed"] == 0
        assert group["average_similarity"] is not None
        assert group["intra_list_diversity"] is not None
        assert group["catalog_coverage"] is not None
        assert group["errors"] == []


def test_evaluate_recommender_records_failures(
    fitted_recommender,
    monkeypatch,
):
    from book_recommender.evaluation import evaluate_recommender

    def failing_recommend(*args, **kwargs):
        raise ValueError("Error de prueba")

    monkeypatch.setattr(
        fitted_recommender,
        "recommend",
        failing_recommend,
    )

    results = evaluate_recommender(
        recommender=fitted_recommender,
        n_queries=2,
        random_state=42,
    )

    for group in results.values():
        assert group["queries_requested"] == 2
        assert group["queries_succeeded"] == 0
        assert group["queries_failed"] == 2
        assert group["average_similarity"] is None
        assert group["intra_list_diversity"] is None
        assert group["catalog_coverage"] is None
        assert len(group["errors"]) == 2
