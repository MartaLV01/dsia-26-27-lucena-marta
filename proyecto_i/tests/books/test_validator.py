
import pandas as pd
import pytest

from books_app.validator import BookRecord, BookValidator, ValidationError


@pytest.fixture
def valid_row():
    """Devuelve una fila de libro válida."""
    return {
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
    }


def test_split_acepta_un_libro_valido(valid_row):
    validator = BookValidator()

    records, clean_frame, errors = validator.split(
        pd.DataFrame([valid_row])
    )

    assert len(records) == 1
    assert isinstance(records[0], BookRecord)
    assert records[0].title == "Libro Uno"
    assert records[0].average_rating == 4.0
    assert len(clean_frame) == 1
    assert errors.empty


def test_split_rechaza_filas_con_valoracion_fuera_de_rango(valid_row):
    validator = BookValidator()
    valid_row["average_rating"] = 5.1

    records, clean_frame, errors = validator.split(
        pd.DataFrame([valid_row])
    )

    assert records == []
    assert clean_frame.empty
    assert len(errors) == 1


@pytest.mark.parametrize("rating", [-0.1, 5.1])
def test_split_rechaza_valoraciones_fuera_de_limites(valid_row, rating):
    validator = BookValidator()
    valid_row["average_rating"] = rating

    records, _, errors = validator.split(pd.DataFrame([valid_row]))

    assert records == []
    assert len(errors) == 1


@pytest.mark.parametrize("column", [
    "book_id",
    "goodreads_book_id",
    "best_book_id",
    "work_id",
    "books_count",
])
def test_split_rechaza_enteros_que_no_son_positivos(valid_row, column):
    validator = BookValidator()
    valid_row[column] = 0

    records, _, errors = validator.split(pd.DataFrame([valid_row]))

    assert records == []
    assert len(errors) == 1


def test_split_rechaza_numero_de_valoraciones_negativo(valid_row):
    validator = BookValidator()
    valid_row["ratings_count"] = -1

    records, _, errors = validator.split(pd.DataFrame([valid_row]))

    assert records == []
    assert len(errors) == 1


@pytest.mark.parametrize("column", ["title", "authors"])
def test_split_rechaza_texto_vacio(valid_row, column):
    validator = BookValidator()
    valid_row[column] = "   "

    records, _, errors = validator.split(pd.DataFrame([valid_row]))

    assert records == []
    assert len(errors) == 1


def test_split_rechaza_columnas_obligatorias_ausentes(valid_row):
    validator = BookValidator()
    frame = pd.DataFrame([valid_row]).drop(columns=["title"])

    with pytest.raises(ValidationError, match="Faltan columnas obligatorias"):
        validator.split(frame)


def test_split_acepta_isbn_nulo(valid_row):
    validator = BookValidator()
    valid_row["isbn"] = None

    records, clean_frame, errors = validator.split(
        pd.DataFrame([valid_row])
    )

    assert len(records) == 1
    assert records[0].isbn is None
    assert len(clean_frame) == 1
    assert errors.empty


def test_split_rechaza_identificador_decimal(valid_row):
    validator = BookValidator()
    valid_row["book_id"] = 1.5

    records, _, errors = validator.split(pd.DataFrame([valid_row]))

    assert records == []
    assert len(errors) == 1


def test_split_separa_filas_validas_e_invalidas(valid_row):
    validator = BookValidator()
    invalid_row = valid_row.copy()
    invalid_row["book_id"] = 2
    invalid_row["title"] = ""

    frame = pd.DataFrame([valid_row, invalid_row])

    records, clean_frame, errors = validator.split(frame)

    assert len(records) == 1
    assert len(clean_frame) == 1
    assert len(errors) == 1
    assert clean_frame.iloc[0]["title"] == "Libro Uno"
