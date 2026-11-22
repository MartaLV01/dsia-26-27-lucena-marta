
import pandas as pd
import pytest

from book_recommender.recommender import BookRecommender


@pytest.fixture
def sample_books():
    """Catálogo pequeño para probar el recomendador."""
    return pd.DataFrame({
        "book_id": [1, 2, 3, 4, 5],
        "title": [
            "Libro de magia",
            "Libro de dragones",
            "Historia de fantasía",
            "Historia romántica",
            "Novela de amor",
        ],
        "content": [
            "magia fantasía aventura hechizos",
            "dragones magia fantasía aventura",
            "fantasía magia reino aventura",
            "romance amor historia sociedad",
            "amor romance novela sentimientos",
        ],
    })


@pytest.fixture
def fitted_recommender(sample_books):
    """Recomendador entrenado con el catálogo de prueba."""
    recommender = BookRecommender()
    recommender.fit(sample_books)
    return recommender

"""
Que el modelo se entrena correctamente
Que recomienda libros parecidos al libro seleccionado
Que admite varios libros y etiquetas
Que excluye los libros que el usuario ya ha seleccionado
Que controla los errores cuando recibe datos incorrectos
"""
def test_fit_trains_recommender(sample_books):
    recommender = BookRecommender()

    result = recommender.fit(sample_books)

    assert result is recommender
    assert recommender.is_fitted_
    assert recommender.tfidf_matrix_.shape[0] == 5


def test_recommend_returns_similar_books(fitted_recommender):
    recommendations = fitted_recommender.recommend(
        book_ids=[1],
        n_recommendations=2,
    )

    assert len(recommendations) == 2
    assert 1 not in recommendations["book_id"].values
    assert "similarity" in recommendations.columns
    assert recommendations.iloc[0]["book_id"] in [2, 3]


def test_recommend_accepts_multiple_books_and_tags(fitted_recommender):
    recommendations = fitted_recommender.recommend(
        book_ids=[1, 2],
        tags=["fantasía", "magia"],
        n_recommendations=3,
    )

    assert len(recommendations) == 3
    assert not {1, 2}.intersection(recommendations["book_id"])


def test_recommend_requires_preferences(fitted_recommender):
    with pytest.raises(ValueError):
        fitted_recommender.recommend()


def test_recommend_requires_fitted_model():
    recommender = BookRecommender()

    with pytest.raises(RuntimeError):
        recommender.recommend(book_ids=[1])


def test_fit_rejects_duplicate_book_ids(sample_books):
    sample_books = pd.concat(
        [sample_books, sample_books.iloc[[0]]],
        ignore_index=True,
    )

    recommender = BookRecommender()

    with pytest.raises(ValueError, match="duplicados"):
        recommender.fit(sample_books)


def test_recommend_rejects_unknown_book_ids(fitted_recommender):
    with pytest.raises(ValueError, match="identificadores"):
        fitted_recommender.recommend(book_ids=[999])


def test_recommend_rejects_invalid_number(fitted_recommender):
    with pytest.raises(ValueError):
        fitted_recommender.recommend(
            book_ids=[1],
            n_recommendations=0,
        )
