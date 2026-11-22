
from pathlib import Path

import pandas as pd
import pytest

from book_recommender.dataset_builder import (
    build_master_dataset,
    save_master_dataset,
)


@pytest.fixture
def validation_results():
    """Prepara los datos sintéticos para los tests."""

    books = pd.DataFrame([
        {
            "book_id": 1,
            "goodreads_book_id": 100,
            "title": "Libro uno",
            "authors": "Autor uno",
            "original_publication_year": 2000,
            "language_code": "eng",
            "average_rating": 4.5,
            "ratings_count": 100,
            "image_url": None,
            "small_image_url": None,
        },
        {
            "book_id": 2,
            "goodreads_book_id": 200,
            "title": "Libro dos",
            "authors": "Autor dos",
            "original_publication_year": 2010,
            "language_code": "spa",
            "average_rating": 4.0,
            "ratings_count": 50,
            "image_url": None,
            "small_image_url": None,
        },
        {
            "book_id": 3,
            "goodreads_book_id": 300,
            "title": "Libro tres",
            "authors": "Autor tres",
            "original_publication_year": 2020,
            "language_code": "eng",
            "average_rating": 3.5,
            "ratings_count": 25,
            "image_url": None,
            "small_image_url": None,
        },
    ])

    book_tags = pd.DataFrame([
        {"goodreads_book_id": 100, "tag_id": 1, "count": 10},
        {"goodreads_book_id": 100, "tag_id": 2, "count": 20},
        {"goodreads_book_id": 100, "tag_id": 3, "count": 15},
        {"goodreads_book_id": 100, "tag_id": 4, "count": 20},
        {"goodreads_book_id": 100, "tag_id": 5, "count": 5},
        {"goodreads_book_id": 100, "tag_id": 6, "count": 0},
        {"goodreads_book_id": 200, "tag_id": 1, "count": 8},
        {"goodreads_book_id": 200, "tag_id": 3, "count": 4},
    ])

    tags = pd.DataFrame([
        {"tag_id": 1, "tag_name": "adventure"},
        {"tag_id": 2, "tag_name": "fantasy"},
        {"tag_id": 3, "tag_name": "classics"},
        {"tag_id": 4, "tag_name": "fiction"},
        {"tag_id": 5, "tag_name": "romance"},
        {"tag_id": 6, "tag_name": "unused"},
    ])

    return {
        "books": {"valid": books},
        "book_tags": {"valid": book_tags},
        "tags": {"valid": tags},
    }


def test_build_master_dataset_keeps_all_books(validation_results):
    """Comprueba que se conservan los libros sin etiquetas."""
    results = validation_results

    master = build_master_dataset(results)

    assert len(master) == 3
    assert master["goodreads_book_id"].tolist() == [100, 200, 300]

    # El tercer libro no tiene etiquetas.
    assert pd.isna(master.iloc[2]["tag_1"])


def test_build_master_dataset_selects_top_five_tags(validation_results):
    """Comprueba la selección y el orden de las cinco etiquetas."""
    results = validation_results

    master = build_master_dataset(results)

    first_book = master[master["goodreads_book_id"] == 100].iloc[0]

    assert first_book["tag_1"] == "fantasy"
    assert first_book["tag_2"] == "fiction"
    assert first_book["tag_3"] == "classics"
    assert first_book["tag_4"] == "adventure"
    assert first_book["tag_5"] == "romance"

    # La etiqueta con count cero no debe aparecer.
    assert "unused" not in first_book[
        [f"tag_{i}" for i in range(1, 6)]
    ].tolist()

@pytest.mark.parametrize("position", [3, 4, 5])
def test_build_master_dataset_fills_missing_tags_with_null(validation_results,
    position,
): 
    """Comprueba que los libros con menos de cinco etiquetas tienen nulos."""
    results = validation_results

    master = build_master_dataset(results)

    second_book = master[master["goodreads_book_id"] == 200].iloc[0]

    assert pd.isna(second_book[f"tag_{position}"])


def test_build_master_dataset_has_expected_columns(validation_results):
    """Comprueba que el dataset tiene las 15 columnas esperadas."""
    results = validation_results

    master = build_master_dataset(results)

    expected_columns = [
        "book_id",
        "goodreads_book_id",
        "title",
        "authors",
        "original_publication_year",
        "language_code",
        "average_rating",
        "ratings_count",
        "image_url",
        "small_image_url",
        "tag_1",
        "tag_2",
        "tag_3",
        "tag_4",
        "tag_5",
    ]

    assert master.columns.tolist() == expected_columns


def test_save_master_dataset_creates_csv(validation_results, tmp_path):
    """Comprueba que el CSV se guarda correctamente."""
    results = validation_results
    master = build_master_dataset(results)

    output_path = tmp_path / "processed" / "books_master.csv"

    save_master_dataset(master, output_path)

    assert output_path.exists()

    saved_df = pd.read_csv(output_path)

    assert len(saved_df) == 3
    assert saved_df.columns.tolist() == master.columns.tolist()

    # Comprobamos que no se ha guardado el índice de pandas.
    assert not any(
        column.startswith("Unnamed:")
        for column in saved_df.columns
    )
