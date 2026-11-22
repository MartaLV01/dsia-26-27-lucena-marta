
import pandas as pd
import pytest

from book_recommender.model_training import (
    train_and_save_model,
    load_model,
)


@pytest.fixture
def sample_books():
    return pd.DataFrame({
        "book_id": [1, 2, 3],
        "title": [
            "The Dragon",
            "The Dragon Returns",
            "A Space Journey",
        ],
        "authors": [
            "Author One",
            "Author One",
            "Author Two",
        ],
        "tag_1": ["fantasy", "fantasy", "science fiction"],
        "tag_2": ["magic", "adventure", "space"],
        "tag_3": ["", "", ""],
        "tag_4": ["", "", ""],
        "tag_5": ["", "", ""],
    })


def test_train_and_save_model(sample_books, tmp_path):
    model_path = tmp_path / "test_model.joblib"
    # se usa una carpeta temporal para evitar tener nultples joblib de pruebas

    recommender = train_and_save_model(
        sample_books,
        output_path=model_path,
    )

    assert model_path.is_file()
    assert recommender.is_fitted_


def test_load_model_and_recommend(sample_books, tmp_path):
    model_path = tmp_path / "test_model.joblib"

    train_and_save_model(sample_books, output_path=model_path)

    loaded_model = load_model(model_path)

    recommendations = loaded_model.recommend(
        book_ids=[1],
        n_recommendations=1,
    )

    assert loaded_model.is_fitted_
    assert not recommendations.empty
    assert 1 not in recommendations["book_id"].values


def test_load_model_rejects_missing_file(tmp_path):
    model_path = tmp_path / "missing_model.joblib"

    with pytest.raises(FileNotFoundError):
        load_model(model_path)
