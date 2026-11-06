
import pandas as pd
import pytest

from books_app.loader import CsvBooksRepository
from books_app.validator import BookValidator
from books_app.metrics import BooksMetrics


@pytest.mark.integration
def test_integracion_csv_validacion_y_metricas(tmp_path):
    """Comprueba el flujo desde el CSV hasta las métricas."""

    csv_path = tmp_path / "books_integration.csv"

    data = [
        {
            "book_id": 1,
            "goodreads_book_id": 101,
            "best_book_id": 101,
            "work_id": 1001,
            "books_count": 5,
            "isbn": "1234567890",
            "authors": "Autor Uno",
            "title": "Libro Uno",
            "average_rating": 4.0,
            "ratings_count": 100,
        },
        {
            "book_id": 2,
            "goodreads_book_id": 102,
            "best_book_id": 102,
            "work_id": 1002,
            "books_count": 3,
            "isbn": None,
            "authors": "Autor Dos",
            "title": "Libro Dos",
            "average_rating": 3.0,
            "ratings_count": 250,
        },
        {
            "book_id": 3,
            "goodreads_book_id": 103,
            "best_book_id": 103,
            "work_id": 1003,
            "books_count": 2,
            "isbn": None,
            "authors": "Autor Tres",
            "title": "Libro Inválido",
            "average_rating": 6.0,
            "ratings_count": 50,
        },
    ]

    pd.DataFrame(data).to_csv(csv_path, index=False)

    # 1. Cargar el CSV
    repository = CsvBooksRepository(csv_path)
    frame = repository.load()

    assert len(frame) == 3

    # 2. Validar y separar las filas
    validator = BookValidator()
    records, clean_frame, errors = validator.split(frame)

    assert len(records) == 2
    assert len(clean_frame) == 2
    assert len(errors) == 1

    # 3. Calcular métricas de los libros válidos
    metrics = BooksMetrics()

    assert metrics.total_books(records) == 2
    assert metrics.average_rating(records) == pytest.approx(3.5)

    most_rated = metrics.most_rated_book(records)

    assert most_rated is not None
    assert most_rated.title == "Libro Dos"
    assert most_rated.ratings_count == 250
