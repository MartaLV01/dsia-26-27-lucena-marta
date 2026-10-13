
import pytest

from books_app.metrics import BooksMetrics
from books_app.validator import BookRecord


@pytest.fixture
def books():
    """Crea libros de ejemplo para probar las métricas."""
    return [
        BookRecord(
            book_id=1,
            goodreads_book_id=101,
            best_book_id=101,
            work_id=1001,
            books_count=5,
            isbn="1234567890",
            authors="Autor Uno",
            title="Libro Uno",
            average_rating=4.0,
            ratings_count=100,
        ),
        BookRecord(
            book_id=2,
            goodreads_book_id=102,
            best_book_id=102,
            work_id=1002,
            books_count=3,
            isbn=None,
            authors="Autor Dos",
            title="Libro Dos",
            average_rating=3.0,
            ratings_count=250,
        ),
        BookRecord(
            book_id=3,
            goodreads_book_id=103,
            best_book_id=103,
            work_id=1003,
            books_count=2,
            isbn="9876543210",
            authors="Autor Tres",
            title="Libro Tres",
            average_rating=5.0,
            ratings_count=50,
        ),
    ]


def test_total_books(books):
    metrics = BooksMetrics()

    assert metrics.total_books(books) == 3


def test_total_books_lista_vacia():
    metrics = BooksMetrics()

    assert metrics.total_books([]) == 0


def test_average_rating(books):
    metrics = BooksMetrics()

    assert metrics.average_rating(books) == pytest.approx(4.0)


def test_average_rating_lista_vacia():
    metrics = BooksMetrics()

    assert metrics.average_rating([]) == 0.0


def test_most_rated_book(books):
    metrics = BooksMetrics()

    result = metrics.most_rated_book(books)

    assert result is not None
    assert result.title == "Libro Dos"
    assert result.ratings_count == 250


def test_most_rated_book_lista_vacia():
    metrics = BooksMetrics()

    assert metrics.most_rated_book([]) is None
