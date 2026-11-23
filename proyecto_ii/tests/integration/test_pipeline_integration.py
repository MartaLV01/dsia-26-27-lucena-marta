
"""
Test de integración del pipeline completo.
"""

import pandas as pd
import pytest
#from book_recommender.pipeline import run_pipeline
from book_recommender import pipeline

@pytest.mark.integration
#def test_pipeline_integration(tmp_path):
def test_pipeline_integration(tmp_path, monkeypatch):
    # 1. Crear el directorio temporal de datos.
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    output_path = tmp_path / "processed" / "books_master.csv"

    # 2. Crear books.csv con todas las columnas obligatorias.
    books = pd.DataFrame([
        {
            "book_id": 1,
            "goodreads_book_id": 101,
            "best_book_id": 101,
            "work_id": 1001,
            "books_count": 5,
            "isbn": "1111111111",
            "isbn13": "9781111111111",
            "authors": "Autor Uno",
            "original_publication_year": 2000,
            "original_title": "Libro Uno",
            "title": "Libro Uno",
            "language_code": "eng",
            "average_rating": 4.5,
            "ratings_count": 100,
            "work_ratings_count": 120,
            "work_text_reviews_count": 20,
            "ratings_1": 1,
            "ratings_2": 2,
            "ratings_3": 10,
            "ratings_4": 30,
            "ratings_5": 57,
            "image_url": "https://example.com/book1.jpg",
            "small_image_url": "https://example.com/book1_small.jpg",
        },
        {
            "book_id": 2,
            "goodreads_book_id": 102,
            "best_book_id": 102,
            "work_id": 1002,
            "books_count": 3,
            "isbn": "2222222222",
            "isbn13": "9782222222222",
            "authors": "Autor Dos",
            "original_publication_year": 2010,
            "original_title": "Libro Dos",
            "title": "Libro Dos",
            "language_code": "eng",
            "average_rating": 3.5,
            "ratings_count": 50,
            "work_ratings_count": 60,
            "work_text_reviews_count": 10,
            "ratings_1": 2,
            "ratings_2": 5,
            "ratings_3": 15,
            "ratings_4": 20,
            "ratings_5": 8,
            "image_url": "https://example.com/book2.jpg",
            "small_image_url": "https://example.com/book2_small.jpg",
        },
    ])

    # 3. Crear ratings.csv.
    ratings = pd.DataFrame([
        {"user_id": 1, "book_id": 1, "rating": 5},
        {"user_id": 2, "book_id": 1, "rating": 4},
        {"user_id": 1, "book_id": 2, "rating": 3},
    ])

    # 4. Crear tags.csv.
    tags = pd.DataFrame([
        {"tag_id": 1, "tag_name": "fantasy"},
        {"tag_id": 2, "tag_name": "adventure"},
    ])

    # 5. Crear book_tags.csv.
    book_tags = pd.DataFrame([
        {"goodreads_book_id": 101, "tag_id": 1, "count": 100},
        {"goodreads_book_id": 101, "tag_id": 2, "count": 80},
        {"goodreads_book_id": 102, "tag_id": 2, "count": 60},
    ])

    # 6. Crear to_read.csv.
    to_read = pd.DataFrame([
        {"user_id": 1, "book_id": 1},
        {"user_id": 2, "book_id": 2},
    ])

    # 7. Guardar los cinco CSV.
    books.to_csv(raw_dir / "books.csv", index=False)
    ratings.to_csv(raw_dir / "ratings.csv", index=False)
    tags.to_csv(raw_dir / "tags.csv", index=False)
    book_tags.to_csv(raw_dir / "book_tags.csv", index=False)
    to_read.to_csv(raw_dir / "to_read.csv", index=False)

    # En esta prueba usamos un catálogo pequeño, así que reducimos
    # el número de consultas de evaluación.
    monkeypatch.setattr(pipeline, "N_QUERIES", 1)
    
    # 8. Ejecutar el pipeline completo
    result = pipeline.run_pipeline(
        data_dir=raw_dir,
        output_path=output_path,
    )

    # 9. Comprobar que se ha generado el CSV maestro.
    assert output_path.exists()

    generated_dataset = pd.read_csv(output_path)

    # 10. Comprobar el dataset maestro.
    assert len(generated_dataset) == 2
    assert len(generated_dataset.columns) == 15

    assert generated_dataset["book_id"].tolist() == [1, 2]
    assert generated_dataset["title"].tolist() == [
        "Libro Uno",
        "Libro Dos",
    ]

    assert generated_dataset.loc[0, "tag_1"] == "fantasy"
    assert generated_dataset.loc[0, "tag_2"] == "adventure"

    # 11. Comprobar los resultados devueltos por el pipeline.
    assert len(result["master_dataset"]) == 2
    assert result["output_path"] == output_path

    # 12. Comprobar las métricas.
    metrics = result["metrics"]

    assert metrics["total_books"] == 2
    assert metrics["average_rating"] == 4.0
    assert metrics["most_rated_book"]["title"] == "Libro Uno"

    # 13. Comprobar que los cinco datasets se han validado.
    validation_results = result["validation_results"]

    assert set(validation_results) == {
        "books",
        "ratings",
        "tags",
        "book_tags",
        "to_read",
    }

    for dataset_result in validation_results.values():
        assert len(dataset_result["invalid"]) == 0

    # 14. Comprobar los resultados de evaluación.
    evaluation_results = result["evaluation_results"]

    assert set(evaluation_results) == {
        "book_queries",
        "tag_queries",
        "combined_queries",
    }

    for evaluation in evaluation_results.values():
        assert evaluation["queries_requested"] == 1
        assert evaluation["queries_succeeded"] == 1
        assert evaluation["queries_failed"] == 0

    assert result["evaluation_path"].exists()
